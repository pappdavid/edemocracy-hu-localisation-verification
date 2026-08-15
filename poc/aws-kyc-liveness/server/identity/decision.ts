import type { Decision, DocumentSignal, FaceMatchSignal, LivenessSignal, ReasonCode, VerificationResult } from "../../shared/identity/types";

export function buildDecision(input: {
  document: DocumentSignal;
  liveness: LivenessSignal;
  faceMatch: FaceMatchSignal;
  livenessThreshold: number;
  faceMatchThreshold: number;
  reasons: ReasonCode[];
}): VerificationResult {
  const reasons = Array.from(new Set(input.reasons));
  const technicalSignalsPass = input.document.readable && input.document.internallyConsistent && input.liveness.passed && input.faceMatch.passed;
  let decision: Decision = "review";

  if (technicalSignalsPass) decision = "pass";
  if (!input.document.readable || !input.liveness.passed || !input.faceMatch.passed) decision = "fail";
  if (reasons.includes("aws_provider_error") || reasons.includes("aws_timeout") || reasons.includes("provider_response_invalid") || reasons.includes("face_comparison_unavailable")) decision = "review";

  return {
    document: input.document,
    liveness: input.liveness,
    faceMatch: input.faceMatch,
    identityConsistent: technicalSignalsPass,
    decision,
    reasonCodes: reasons,
    thresholds: { liveness: input.livenessThreshold, faceMatch: input.faceMatchThreshold },
  };
}
