import { describe, expect, it } from "vitest";
import { runAwsPreflight } from "./awsPreflight";

describe("live AWS KYC preflight", () => {
  it("uses eu-west-1 and accepts the labelled Textract activation-pending fallback state without biometric input", async () => {
    const report = await runAwsPreflight();
    expect(report.expectedRegion).toBe("eu-west-1");
    expect(report.ready, JSON.stringify(report.checks)).toBe(true);
    expect(report.checks.find(check => check.id === "sts")?.state).toBe("passed");
    expect(report.checks.find(check => check.id === "rekognition")?.state).toBe("passed");
    expect(["passed", "warning"]).toContain(report.checks.find(check => check.id === "textract")?.state);
  }, 30_000);
});
