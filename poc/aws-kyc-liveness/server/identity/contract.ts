import type { PreflightReport, VerificationResult } from "../../shared/identity/types";

export type DocumentInspection = {
  verificationId: string;
  document: VerificationResult["document"];
  reasonCodes: VerificationResult["reasonCodes"];
  extractionSource: "textract" | "rekognition_ocr";
};

export interface IdentityVerificationProvider {
  preflight(): Promise<PreflightReport>;
  inspectDocument(input: { imageBytes: Uint8Array; mimeType: string }): Promise<DocumentInspection>;
  createLivenessSession(input: { verificationId: string }): Promise<{ sessionId: string }>;
  resolveLiveness(input: { sessionId: string }): Promise<VerificationResult>;
}
