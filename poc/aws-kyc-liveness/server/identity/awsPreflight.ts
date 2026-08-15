import { GetFaceLivenessSessionResultsCommand, RekognitionClient } from "@aws-sdk/client-rekognition";
import { STSClient, GetCallerIdentityCommand } from "@aws-sdk/client-sts";
import { AnalyzeIDCommand, TextractClient } from "@aws-sdk/client-textract";
import { AWS_KYC_REGION, type PreflightCheck, type PreflightReport } from "../../shared/identity/types";
import { getAwsKycConfig } from "./config";
import { safeErrorSummary } from "./redaction";

function failedCheck(id: string, label: string, error: unknown): PreflightCheck {
  const summary = safeErrorSummary(error);
  return {
    id,
    label,
    state: "failed",
    detail:
      summary.code === "aws_permission_denied"
        ? "Access was denied. Review the least-privilege IAM policy."
        : "The service could not be reached with the configured runtime credentials.",
  };
}

function pendingTextractCheck(id: string, label: string, error: unknown): PreflightCheck | null {
  const errorName = error instanceof Error ? error.name : "";
  if (id !== "textract" || errorName !== "SubscriptionRequiredException") return null;
  return {
    id,
    label,
    state: "warning",
    detail: "Textract account activation is still pending. The active workflow will use the labelled Rekognition OCR fallback for document readability and MRZ checks.",
  };
}

async function probe(id: string, label: string, action: () => Promise<string>): Promise<PreflightCheck> {
  try {
    return { id, label, state: "passed", detail: await action() };
  } catch (error) {
    return failedCheck(id, label, error);
  }
}

async function permissionProbe(
  id: string,
  label: string,
  expectedServiceErrors: string[],
  action: () => Promise<unknown>,
): Promise<PreflightCheck> {
  try {
    await action();
    return { id, label, state: "passed", detail: "The configured runtime identity completed the capability check." };
  } catch (error) {
    const name = error instanceof Error ? error.name : "";
    if (expectedServiceErrors.includes(name)) {
      return {
        id,
        label,
        state: "passed",
        detail: "The service accepted the authenticated capability probe; a valid verification input is required for the live workflow.",
      };
    }
    const pending = pendingTextractCheck(id, label, error);
    if (pending) return pending;
    return failedCheck(id, label, error);
  }
}

export async function runAwsPreflight(): Promise<PreflightReport> {
  const config = getAwsKycConfig();
  const regionCheck: PreflightCheck = config.isExpectedRegion
    ? { id: "region", label: "Fixed AWS region", state: "passed", detail: `Runtime is pinned to ${AWS_KYC_REGION}.` }
    : {
        id: "region",
        label: "Fixed AWS region",
        state: "failed",
        detail: `The runtime is configured for a region other than ${AWS_KYC_REGION}.`,
      };
  const browserSecretsCheck: PreflightCheck = process.env.VITE_AWS_ACCESS_KEY_ID || process.env.VITE_AWS_SECRET_ACCESS_KEY
    ? {
        id: "browser-secrets",
        label: "Frontend credential safeguard",
        state: "failed",
        detail: "A credential-like variable was detected in frontend configuration.",
      }
    : {
        id: "browser-secrets",
        label: "Frontend credential safeguard",
        state: "passed",
        detail: "Permanent AWS credentials are not exposed through frontend configuration.",
      };

  if (!config.isExpectedRegion) {
    return { expectedRegion: AWS_KYC_REGION, checks: [regionCheck, browserSecretsCheck], ready: false };
  }

  const sts = new STSClient({ region: AWS_KYC_REGION });
  const rekognition = new RekognitionClient({ region: AWS_KYC_REGION });
  const textract = new TextractClient({ region: AWS_KYC_REGION });
  const checks = await Promise.all([
    probe("sts", "STS caller identity", async () => {
      const result = await sts.send(new GetCallerIdentityCommand({}));
      const suffix = result.Account ? result.Account.slice(-4) : "unknown";
      return `Runtime identity confirmed for AWS account ending ${suffix}.`;
    }),
    permissionProbe("rekognition", "Rekognition capability", ["ResourceNotFoundException", "SessionNotFoundException", "InvalidParameterException", "ValidationException"], () =>
      rekognition.send(new GetFaceLivenessSessionResultsCommand({ SessionId: "preflight" })),
    ),
    permissionProbe("textract", "Textract capability", ["InvalidParameterException", "InvalidImageFormatException", "UnsupportedDocumentException"], () =>
      textract.send(new AnalyzeIDCommand({ DocumentPages: [{ Bytes: new Uint8Array([0]) }] })),
    ),
  ]);
  const probesReady = checks.every(check => check.state === "passed" || check.state === "warning");
  const policyCheck: PreflightCheck = {
    id: "required-actions",
    label: "Required runtime actions",
    state: probesReady ? "warning" : "failed",
    detail: probesReady
      ? "Capability probes passed or have an explicitly labelled activation fallback. The live workflow verifies session creation, result retrieval, face comparison, and AnalyzeID only with authorized verification inputs."
      : "One or more capability probes failed, so required runtime actions cannot be verified yet.",
  };
  const allChecks = [regionCheck, browserSecretsCheck, ...checks, policyCheck];
  return {
    expectedRegion: AWS_KYC_REGION,
    checks: allChecks,
    ready: allChecks.every(check => check.state === "passed" || check.state === "warning"),
  };
}
