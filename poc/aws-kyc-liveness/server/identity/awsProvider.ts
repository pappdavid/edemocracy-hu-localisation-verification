import {
  CompareFacesCommand,
  CreateFaceLivenessSessionCommand,
  DetectFacesCommand,
  DetectTextCommand,
  GetFaceLivenessSessionResultsCommand,
  RekognitionClient,
  type GetFaceLivenessSessionResultsCommandOutput,
} from "@aws-sdk/client-rekognition";
import { DeleteObjectsCommand, ListObjectsV2Command, S3Client } from "@aws-sdk/client-s3";
import { AnalyzeIDCommand, TextractClient } from "@aws-sdk/client-textract";
import { nanoid } from "nanoid";
import sharp from "sharp";
import type { FaceMatchSignal, LivenessSignal, ReasonCode, VerificationResult } from "../../shared/identity/types";
import { buildDecision } from "./decision";
import { getAwsKycConfig } from "./config";
import type { DocumentInspection, IdentityVerificationProvider } from "./contract";
import { namesAreConsistent, parseTd1Mrz } from "./mrz";
import { providerReasonCode } from "./redaction";
import { runAwsPreflight } from "./awsPreflight";

type VerificationRecord = {
  verificationId: string;
  document: VerificationResult["document"];
  reasonCodes: ReasonCode[];
  portraitBytes: Uint8Array | null;
  outputPrefix: string;
};

const MAX_DOCUMENT_BYTES = 10 * 1024 * 1024;
const acceptedMimeTypes = new Set(["image/jpeg", "image/png"]);

export function decodeDocumentBase64(dataBase64: string): Uint8Array {
  const payload = dataBase64.includes(",") ? dataBase64.slice(dataBase64.indexOf(",") + 1) : dataBase64;
  if (!payload || payload.length > 14_000_000 || !/^[A-Za-z0-9+/=\s]+$/.test(payload)) throw new Error("INVALID_DOCUMENT_INPUT");
  const bytes = Buffer.from(payload, "base64");
  if (!bytes.length || bytes.length > MAX_DOCUMENT_BYTES) throw new Error("INVALID_DOCUMENT_INPUT");
  return bytes;
}

function normalizedDate(value: string | undefined): string | null {
  if (!value) return null;
  const matched = value.match(/(\d{4})[-/.]?(\d{2})[-/.]?(\d{2})/);
  return matched ? `${matched[1]}-${matched[2]}-${matched[3]}` : null;
}

function terminalStatus(status: string | undefined): boolean {
  return status === "SUCCEEDED" || status === "FAILED" || status === "EXPIRED";
}

function livenessStatus(status: string | undefined): LivenessSignal["status"] {
  if (status === "CREATED" || status === "IN_PROGRESS" || status === "SUCCEEDED" || status === "FAILED" || status === "EXPIRED") return status;
  return "UNAVAILABLE";
}

export class AwsIdentityVerificationProvider implements IdentityVerificationProvider {
  private readonly rekognition = new RekognitionClient({ region: "eu-west-1" });
  private readonly textract = new TextractClient({ region: "eu-west-1" });
  private readonly s3 = new S3Client({ region: "eu-west-1" });
  private readonly records = new Map<string, VerificationRecord>();
  private readonly sessions = new Map<string, string>();

  async preflight() {
    return runAwsPreflight();
  }

  async inspectDocument(input: { imageBytes: Uint8Array; mimeType: string }): Promise<DocumentInspection> {
    const verificationId = nanoid(20);
    const reasons: ReasonCode[] = [];
    if (!acceptedMimeTypes.has(input.mimeType) || !input.imageBytes.length || input.imageBytes.length > MAX_DOCUMENT_BYTES) {
      return {
        verificationId,
        document: { readable: false, internallyConsistent: false },
        reasonCodes: ["document_unreadable"],
        extractionSource: "textract",
      };
    }

    try {
      const fieldValues = new Map<string, string>();
      let allText = "";
      let extractionSource: DocumentInspection["extractionSource"] = "textract";
      try {
        const textractResult = await this.textract.send(new AnalyzeIDCommand({ DocumentPages: [{ Bytes: input.imageBytes }] }));
        const identityDocument = textractResult.IdentityDocuments?.[0];
        const fields = identityDocument?.IdentityDocumentFields ?? [];
        for (const field of fields) {
          const type = field.Type?.Text?.trim();
          const value = field.ValueDetection?.NormalizedValue?.Value ?? field.ValueDetection?.Text;
          if (type && value) fieldValues.set(type, value.trim());
        }
        allText = [
          ...Array.from(fieldValues.values()),
          ...(identityDocument?.Blocks?.map(block => block.Text).filter((value): value is string => Boolean(value)) ?? []),
        ].join("\n");
      } catch (error) {
        const errorName = error instanceof Error ? error.name : "";
        if (errorName !== "SubscriptionRequiredException") throw error;
        const fallback = await this.rekognition.send(new DetectTextCommand({ Image: { Bytes: input.imageBytes } }));
        allText = (fallback.TextDetections ?? []).map(detection => detection.DetectedText).filter((value): value is string => Boolean(value)).join("\n");
        extractionSource = "rekognition_ocr";
        reasons.push("textract_pending");
      }
      const mrz = parseTd1Mrz(allText);
      const documentName = [fieldValues.get("FIRST_NAME"), fieldValues.get("LAST_NAME")].filter(Boolean).join(" ") || null;
      const documentDob = normalizedDate(fieldValues.get("DATE_OF_BIRTH"));
      const nameConsistent = namesAreConsistent(documentName, mrz.name);
      const dobConsistent = !mrz.dateOfBirth || !documentDob || mrz.dateOfBirth === documentDob;
      const readable = allText.trim().length > 0;

      if (!mrz.checksumsValid) reasons.push("document_mrz_invalid");
      if (!nameConsistent) reasons.push("document_name_inconsistent");
      if (!dobConsistent) reasons.push("document_dob_inconsistent");

      const faceResult = await this.rekognition.send(new DetectFacesCommand({ Image: { Bytes: input.imageBytes }, Attributes: ["DEFAULT"] }));
      const face = faceResult.FaceDetails?.sort((left, right) => (right.BoundingBox?.Width ?? 0) - (left.BoundingBox?.Width ?? 0))[0];
      let portraitBytes: Uint8Array | null = null;
      if (face?.BoundingBox) {
        const metadata = await sharp(input.imageBytes).metadata();
        const width = metadata.width ?? 0;
        const height = metadata.height ?? 0;
        const box = face.BoundingBox;
        const left = Math.max(0, Math.floor((box.Left ?? 0) * width));
        const top = Math.max(0, Math.floor((box.Top ?? 0) * height));
        const cropWidth = Math.max(1, Math.min(width - left, Math.ceil((box.Width ?? 0) * width)));
        const cropHeight = Math.max(1, Math.min(height - top, Math.ceil((box.Height ?? 0) * height)));
        portraitBytes = await sharp(input.imageBytes).extract({ left, top, width: cropWidth, height: cropHeight }).jpeg({ quality: 92 }).toBuffer();
      } else {
        reasons.push("document_face_missing");
      }

      const document = {
        readable,
        internallyConsistent: readable && mrz.checksumsValid && nameConsistent && dobConsistent && Boolean(portraitBytes),
      };
      if (!readable) reasons.push("document_unreadable");
      const record: VerificationRecord = {
        verificationId,
        document,
        reasonCodes: Array.from(new Set(reasons)),
        portraitBytes,
        outputPrefix: `liveness/${verificationId}/`,
      };
      this.records.set(verificationId, record);
      return { verificationId, document, reasonCodes: record.reasonCodes, extractionSource };
    } catch (error) {
      return {
        verificationId,
        document: { readable: false, internallyConsistent: false },
        reasonCodes: ["document_unreadable", providerReasonCode(error)],
        extractionSource: "textract",
      };
    }
  }

  async createLivenessSession(input: { verificationId: string }): Promise<{ sessionId: string }> {
    const record = this.records.get(input.verificationId);
    const config = getAwsKycConfig();
    if (!record || !record.portraitBytes || !record.document.internallyConsistent || !config.temporaryBucket) throw new Error("VERIFICATION_NOT_READY");
    const created = await this.rekognition.send(
      new CreateFaceLivenessSessionCommand({
        ClientRequestToken: input.verificationId,
        Settings: {
          AuditImagesLimit: 0,
          OutputConfig: { S3Bucket: config.temporaryBucket, S3KeyPrefix: record.outputPrefix },
        },
      }),
    );
    if (!created.SessionId) throw new Error("LIVENESS_SESSION_UNAVAILABLE");
    this.sessions.set(created.SessionId, input.verificationId);
    return { sessionId: created.SessionId };
  }

  async resolveLiveness(input: { sessionId: string }): Promise<VerificationResult> {
    const verificationId = this.sessions.get(input.sessionId);
    const record = verificationId ? this.records.get(verificationId) : undefined;
    const config = getAwsKycConfig();
    if (!record) {
      return buildDecision({
        document: { readable: false, internallyConsistent: false },
        liveness: { passed: false, confidence: null, status: "UNAVAILABLE" },
        faceMatch: { passed: false, similarity: null },
        livenessThreshold: config.livenessThreshold,
        faceMatchThreshold: config.faceMatchThreshold,
        reasons: ["provider_response_invalid"],
      });
    }

    let result: GetFaceLivenessSessionResultsCommandOutput | undefined;
    let shouldCleanup = false;
    try {
      result = await this.rekognition.send(new GetFaceLivenessSessionResultsCommand({ SessionId: input.sessionId }));
      const status = livenessStatus(result.Status);
      shouldCleanup = terminalStatus(result.Status);
      const confidence = result.Confidence ?? null;
      const livenessPassed = status === "SUCCEEDED" && confidence !== null && confidence >= config.livenessThreshold;
      const reasons: ReasonCode[] = [...record.reasonCodes];
      if (status === "IN_PROGRESS" || status === "CREATED") reasons.push("liveness_in_progress");
      if (status === "FAILED") reasons.push("liveness_failed");
      if (status === "EXPIRED") reasons.push("liveness_expired");
      if (status === "SUCCEEDED" && !livenessPassed) reasons.push("liveness_below_threshold");

      let faceMatch: FaceMatchSignal = { passed: false, similarity: null };
      if (status === "SUCCEEDED" && livenessPassed && record.portraitBytes) {
        const reference = result.ReferenceImage;
        if (reference?.S3Object?.Bucket && reference.S3Object.Name) {
          const compared = await this.rekognition.send(
            new CompareFacesCommand({
              SourceImage: { S3Object: { Bucket: reference.S3Object.Bucket, Name: reference.S3Object.Name } },
              TargetImage: { Bytes: record.portraitBytes },
              SimilarityThreshold: config.faceMatchThreshold,
              QualityFilter: "AUTO",
            }),
          );
          const similarity = Math.max(0, ...(compared.FaceMatches?.map(match => match.Similarity ?? 0) ?? []));
          faceMatch = { passed: similarity >= config.faceMatchThreshold, similarity };
          if (!faceMatch.passed) reasons.push("face_mismatch");
        } else {
          reasons.push("liveness_reference_missing", "face_comparison_unavailable");
        }
      }

      return buildDecision({
        document: record.document,
        liveness: { passed: livenessPassed, confidence, status },
        faceMatch,
        livenessThreshold: config.livenessThreshold,
        faceMatchThreshold: config.faceMatchThreshold,
        reasons,
      });
    } catch (error) {
      shouldCleanup = true;
      return buildDecision({
        document: record.document,
        liveness: { passed: false, confidence: null, status: "UNAVAILABLE" },
        faceMatch: { passed: false, similarity: null },
        livenessThreshold: config.livenessThreshold,
        faceMatchThreshold: config.faceMatchThreshold,
        reasons: [...record.reasonCodes, providerReasonCode(error)],
      });
    } finally {
      if (shouldCleanup) {
        await this.cleanupOutput(record.outputPrefix, result).catch(() => undefined);
        this.sessions.delete(input.sessionId);
        this.records.delete(record.verificationId);
      }
    }
  }

  private async cleanupOutput(prefix: string, result?: GetFaceLivenessSessionResultsCommandOutput): Promise<void> {
    const config = getAwsKycConfig();
    if (!config.temporaryBucket) return;
    const fromResult = [result?.ReferenceImage, ...(result?.AuditImages ?? [])]
      .map(image => image?.S3Object)
      .filter((object): object is { Bucket?: string; Name?: string } => Boolean(object?.Name && object?.Bucket === config.temporaryBucket))
      .map(object => ({ Key: object.Name! }));
    const listed = await this.s3.send(new ListObjectsV2Command({ Bucket: config.temporaryBucket, Prefix: prefix }));
    const objects = Array.from(new Map([...fromResult, ...(listed.Contents?.flatMap(item => (item.Key ? [{ Key: item.Key }] : [])) ?? [])].map(item => [item.Key, item])).values());
    if (objects.length) await this.s3.send(new DeleteObjectsCommand({ Bucket: config.temporaryBucket, Delete: { Objects: objects, Quiet: true } }));
  }
}

let provider: AwsIdentityVerificationProvider | undefined;

export function getAwsIdentityVerificationProvider(): AwsIdentityVerificationProvider {
  provider ??= new AwsIdentityVerificationProvider();
  return provider;
}
