import { describe, expect, it } from "vitest";
import { vi } from "vitest";
import { AwsIdentityVerificationProvider, decodeDocumentBase64 } from "./awsProvider";

type ProviderInternals = {
  records: Map<string, { verificationId: string; document: { readable: boolean; internallyConsistent: boolean }; reasonCodes: []; portraitBytes: Uint8Array | null; outputPrefix: string }>;
  sessions: Map<string, string>;
  rekognition: { send: (command: unknown) => Promise<unknown> };
  s3: { send: (command: unknown) => Promise<unknown> };
};

function getInternals(provider: AwsIdentityVerificationProvider) {
  return provider as unknown as ProviderInternals;
}

function readyRecord(verificationId = "verification") {
  return {
    verificationId,
    document: { readable: true, internallyConsistent: true },
    reasonCodes: [],
    portraitBytes: new Uint8Array([1, 2, 3]),
    outputPrefix: `liveness/${verificationId}/`,
  };
}

describe("document upload decoding", () => {
  it("accepts a compact base64 image payload without retaining a data URL prefix", () => {
    expect(Array.from(decodeDocumentBase64("data:image/jpeg;base64,AQID"))).toEqual([1, 2, 3]);
  });

  it("rejects malformed or oversized-looking upload payloads before an AWS call", () => {
    expect(() => decodeDocumentBase64("not an image!")).toThrow("INVALID_DOCUMENT_INPUT");
  });

  it("returns a document-unreadable result for malformed inspection input", async () => {
    const provider = new AwsIdentityVerificationProvider();
    const result = await provider.inspectDocument({ imageBytes: new Uint8Array(), mimeType: "image/jpeg" });
    expect(result.document).toEqual({ readable: false, internallyConsistent: false });
    expect(result.reasonCodes).toEqual(["document_unreadable"]);
  });

  it("uses the Rekognition OCR fallback when Textract account activation is pending", async () => {
    const provider = new AwsIdentityVerificationProvider();
    const internals = provider as unknown as {
      textract: { send: (command: unknown) => Promise<unknown> };
      rekognition: { send: (command: unknown) => Promise<unknown> };
    };
    internals.textract = {
      send: vi.fn().mockRejectedValue(Object.assign(new Error("activation pending"), { name: "SubscriptionRequiredException" })),
    };
    internals.rekognition = {
      send: vi.fn().mockResolvedValueOnce({ TextDetections: [{ DetectedText: "I<HUN1234567890<<<<<<<<<<<<<<<" }] }).mockResolvedValueOnce({ FaceDetails: [] }),
    };
    const result = await provider.inspectDocument({ imageBytes: new Uint8Array([1, 2, 3]), mimeType: "image/jpeg" });
    expect(result.extractionSource).toBe("rekognition_ocr");
    expect(result.document.readable).toBe(true);
    expect(result.reasonCodes).toContain("textract_pending");
  });

  it("reports inconsistent extracted name and date-of-birth values without accepting the document", async () => {
    const provider = new AwsIdentityVerificationProvider();
    const internals = provider as unknown as ProviderInternals & { textract: { send: (command: unknown) => Promise<unknown> } };
    internals.textract = {
      send: vi.fn().mockResolvedValue({
        IdentityDocuments: [{
          IdentityDocumentFields: [
            { Type: { Text: "FIRST_NAME" }, ValueDetection: { Text: "Kiss" } },
            { Type: { Text: "LAST_NAME" }, ValueDetection: { Text: "Éva" } },
            { Type: { Text: "DATE_OF_BIRTH" }, ValueDetection: { NormalizedValue: { Value: "1990-01-01" } } },
          ],
          Blocks: [
            { Text: "I<HUN1234567890<<<<<<<<<<<<<<<" },
            { Text: "8001011F3001012HUN<<<<<<<<<<<0" },
            { Text: "NAGY<<EVA<<<<<<<<<<<<<<<<<<<<" },
          ],
        }],
      }),
    };
    internals.rekognition = { send: vi.fn().mockResolvedValue({ FaceDetails: [] }) };
    const result = await provider.inspectDocument({ imageBytes: new Uint8Array([1, 2, 3]), mimeType: "image/jpeg" });
    expect(result.document.internallyConsistent).toBe(false);
    expect(result.reasonCodes).toEqual(expect.arrayContaining(["document_name_inconsistent", "document_dob_inconsistent"]));
  });

  it("reports an invalid TD1 MRZ through the document inspection flow", async () => {
    const provider = new AwsIdentityVerificationProvider();
    const internals = provider as unknown as ProviderInternals & { textract: { send: (command: unknown) => Promise<unknown> } };
    internals.textract = {
      send: vi.fn().mockResolvedValue({
        IdentityDocuments: [{
          IdentityDocumentFields: [],
          Blocks: [
            { Text: "I<HUN1234567890<<<<<<<<<<<<<<<" },
            { Text: "8001011F3001012HUN<<<<<<<<<<<0" },
            { Text: "NAGY<<EVA<<<<<<<<<<<<<<<<<<<<" },
          ],
        }],
      }),
    };
    internals.rekognition = { send: vi.fn().mockResolvedValue({ FaceDetails: [] }) };
    const result = await provider.inspectDocument({ imageBytes: new Uint8Array([1, 2, 3]), mimeType: "image/jpeg" });
    expect(result.document.internallyConsistent).toBe(false);
    expect(result.reasonCodes).toContain("document_mrz_invalid");
  });

  it("marks a readable document as not ready when its inspection finds no face", async () => {
    const provider = new AwsIdentityVerificationProvider();
    const internals = provider as unknown as ProviderInternals & { textract: { send: (command: unknown) => Promise<unknown> } };
    internals.textract = { send: vi.fn().mockResolvedValue({ IdentityDocuments: [{ IdentityDocumentFields: [], Blocks: [{ Text: "LEGIBLE DOCUMENT TEXT" }] }] }) };
    internals.rekognition = { send: vi.fn().mockResolvedValue({ FaceDetails: [] }) };
    const result = await provider.inspectDocument({ imageBytes: new Uint8Array([1, 2, 3]), mimeType: "image/jpeg" });
    expect(result.document).toEqual({ readable: true, internallyConsistent: false });
    expect(result.reasonCodes).toContain("document_face_missing");
  });

  it("blocks liveness creation when a document record has no detectable portrait", async () => {
    const provider = new AwsIdentityVerificationProvider();
    const internals = getInternals(provider);
    internals.records.set("no-face", { ...readyRecord("no-face"), document: { readable: true, internallyConsistent: false }, portraitBytes: null });
    await expect(provider.createLivenessSession({ verificationId: "no-face" })).rejects.toThrow("VERIFICATION_NOT_READY");
  });

  it("returns a failed decision and clears a terminal expired session", async () => {
    const provider = new AwsIdentityVerificationProvider();
    const internals = getInternals(provider);
    internals.records.set("expired-verification", readyRecord("expired-verification"));
    internals.sessions.set("expired-session", "expired-verification");
    internals.rekognition = { send: vi.fn().mockResolvedValue({ Status: "EXPIRED" }) };
    internals.s3 = { send: vi.fn().mockResolvedValue({ Contents: [] }) };
    const result = await provider.resolveLiveness({ sessionId: "expired-session" });
    expect(result).toMatchObject({ decision: "fail", liveness: { status: "EXPIRED", passed: false } });
    expect(result.reasonCodes).toContain("liveness_expired");
    expect(internals.sessions.has("expired-session")).toBe(false);
    expect(internals.records.has("expired-verification")).toBe(false);
  });

  it("returns a failed decision and clears a terminal liveness failure", async () => {
    const provider = new AwsIdentityVerificationProvider();
    const internals = getInternals(provider);
    internals.records.set("failed-verification", readyRecord("failed-verification"));
    internals.sessions.set("failed-session", "failed-verification");
    internals.rekognition = { send: vi.fn().mockResolvedValue({ Status: "FAILED" }) };
    internals.s3 = { send: vi.fn().mockResolvedValue({ Contents: [] }) };
    const result = await provider.resolveLiveness({ sessionId: "failed-session" });
    expect(result).toMatchObject({ decision: "fail", liveness: { status: "FAILED", passed: false } });
    expect(result.reasonCodes).toContain("liveness_failed");
    expect(internals.sessions.has("failed-session")).toBe(false);
  });

  it("returns a review decision with a redacted timeout reason when AWS fails during result retrieval", async () => {
    const provider = new AwsIdentityVerificationProvider();
    const internals = getInternals(provider);
    internals.records.set("timeout-verification", readyRecord("timeout-verification"));
    internals.sessions.set("timeout-session", "timeout-verification");
    internals.rekognition = { send: vi.fn().mockRejectedValue(Object.assign(new Error("provider transport detail"), { name: "TimeoutError" })) };
    internals.s3 = { send: vi.fn().mockResolvedValue({ Contents: [] }) };
    const result = await provider.resolveLiveness({ sessionId: "timeout-session" });
    expect(result).toMatchObject({ decision: "review", liveness: { status: "UNAVAILABLE" } });
    expect(result.reasonCodes).toContain("aws_timeout");
  });

  it("returns a failed decision when a successful liveness reference does not match the document portrait", async () => {
    const provider = new AwsIdentityVerificationProvider();
    const internals = getInternals(provider);
    const bucket = process.env.AWS_KYC_TEMP_BUCKET ?? "test-kyc-bucket";
    internals.records.set("mismatch-verification", readyRecord("mismatch-verification"));
    internals.sessions.set("mismatch-session", "mismatch-verification");
    internals.rekognition = {
      send: vi.fn()
        .mockResolvedValueOnce({ Status: "SUCCEEDED", Confidence: 99, ReferenceImage: { S3Object: { Bucket: bucket, Name: "liveness/mismatch-verification/reference.jpg" } } })
        .mockResolvedValueOnce({ FaceMatches: [{ Similarity: 12 }] }),
    };
    internals.s3 = { send: vi.fn().mockResolvedValue({ Contents: [] }) };
    const result = await provider.resolveLiveness({ sessionId: "mismatch-session" });
    expect(result).toMatchObject({ decision: "fail", faceMatch: { passed: false, similarity: 12 } });
    expect(result.reasonCodes).toContain("face_mismatch");
  });

  it("returns a review decision for a result request with no matching provider session", async () => {
    const provider = new AwsIdentityVerificationProvider();
    const result = await provider.resolveLiveness({ sessionId: "unknown-session" });
    expect(result).toMatchObject({ decision: "review", liveness: { status: "UNAVAILABLE" } });
    expect(result.reasonCodes).toContain("provider_response_invalid");
  });
});
