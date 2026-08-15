export const AWS_KYC_REGION = "eu-west-1" as const;

export type CheckState = "passed" | "failed" | "warning" | "pending";
export type Decision = "pass" | "fail" | "review";
export type ReasonCode =
  | "aws_region_mismatch"
  | "aws_credentials_unavailable"
  | "aws_permission_denied"
  | "aws_provider_error"
  | "aws_timeout"
  | "textract_pending"
  | "document_unreadable"
  | "document_mrz_invalid"
  | "document_name_inconsistent"
  | "document_dob_inconsistent"
  | "document_face_missing"
  | "liveness_in_progress"
  | "liveness_failed"
  | "liveness_expired"
  | "liveness_below_threshold"
  | "liveness_reference_missing"
  | "face_mismatch"
  | "face_comparison_unavailable"
  | "provider_response_invalid";

export type DocumentSignal = {
  readable: boolean;
  internallyConsistent: boolean;
};

export type LivenessSignal = {
  passed: boolean;
  confidence: number | null;
  status: "CREATED" | "IN_PROGRESS" | "SUCCEEDED" | "FAILED" | "EXPIRED" | "UNAVAILABLE";
};

export type FaceMatchSignal = {
  passed: boolean;
  similarity: number | null;
};

export type VerificationResult = {
  document: DocumentSignal;
  liveness: LivenessSignal;
  faceMatch: FaceMatchSignal;
  identityConsistent: boolean;
  decision: Decision;
  reasonCodes: ReasonCode[];
  thresholds: {
    liveness: number;
    faceMatch: number;
  };
};

export type PreflightCheck = {
  id: string;
  label: string;
  state: CheckState;
  detail: string;
};

export type PreflightReport = {
  expectedRegion: typeof AWS_KYC_REGION;
  checks: PreflightCheck[];
  ready: boolean;
};
