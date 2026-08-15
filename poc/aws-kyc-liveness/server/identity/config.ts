import { AWS_KYC_REGION } from "../../shared/identity/types";

const MIN_THRESHOLD = 0;
const MAX_THRESHOLD = 100;

function thresholdFromEnv(name: string, fallback: number): number {
  const value = Number(process.env[name] ?? fallback);
  if (!Number.isFinite(value) || value < MIN_THRESHOLD || value > MAX_THRESHOLD) return fallback;
  return value;
}

export function getAwsKycConfig() {
  const configuredRegion = process.env.AWS_REGION ?? AWS_KYC_REGION;
  return {
    configuredRegion,
    expectedRegion: AWS_KYC_REGION,
    isExpectedRegion: configuredRegion === AWS_KYC_REGION,
    livenessThreshold: thresholdFromEnv("AWS_KYC_LIVENESS_THRESHOLD", 92),
    faceMatchThreshold: thresholdFromEnv("AWS_KYC_FACE_MATCH_THRESHOLD", 90),
    temporaryBucket: process.env.AWS_KYC_TEMP_BUCKET?.trim() || undefined,
    temporaryKmsKeyId: process.env.AWS_KYC_TEMP_KMS_KEY_ID?.trim() || undefined,
  } as const;
}

export function assertExpectedRegion(): void {
  if (!getAwsKycConfig().isExpectedRegion) throw new Error("AWS_KYC_REGION_MISMATCH");
}
