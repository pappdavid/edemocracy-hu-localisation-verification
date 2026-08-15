import type { ReasonCode } from "../../shared/identity/types";

const TIMEOUT_NAMES = new Set(["TimeoutError", "RequestTimeout", "RequestTimeoutException"]);
const ACCESS_NAMES = new Set(["AccessDenied", "AccessDeniedException", "UnauthorizedOperation"]);

export function providerReasonCode(error: unknown): ReasonCode {
  const name = error instanceof Error ? error.name : "";
  if (TIMEOUT_NAMES.has(name)) return "aws_timeout";
  if (ACCESS_NAMES.has(name)) return "aws_permission_denied";
  return "aws_provider_error";
}

export function safeErrorSummary(error: unknown): { code: ReasonCode; retryable: boolean } {
  const code = providerReasonCode(error);
  return { code, retryable: code === "aws_timeout" || code === "aws_provider_error" };
}

export function redactedLogContext(operation: string, error: unknown) {
  const summary = safeErrorSummary(error);
  return { operation, code: summary.code, retryable: summary.retryable };
}
