import { describe, expect, it } from "vitest";
import { buildDecision } from "./decision";
import { checksumMatches, mrzChecksum, namesAreConsistent, normalizeIdentityName, parseTd1Mrz } from "./mrz";
import { redactedLogContext } from "./redaction";

describe("MRZ helpers", () => {
  it("calculates ICAO checksum values", () => {
    expect(mrzChecksum("123456789")).toBe(7);
    expect(checksumMatches("123456789", "7")).toBe(true);
    expect(checksumMatches("123456789", "6")).toBe(false);
  });

  it("normalizes accented Hungarian names without retaining punctuation", () => {
    expect(normalizeIdentityName("Árvíztűrő Tükörfúrógép")).toBe("ARVIZTURO TUKORFUROGEP");
    expect(namesAreConsistent("Nagy Éva", "NAGY EVA")).toBe(true);
    expect(namesAreConsistent("Nagy Éva", "Kiss Éva")).toBe(false);
  });

  it("reports a malformed TD1 MRZ as invalid", () => {
    const result = parseTd1Mrz("I<HUN1234567890<<<<<<<<<<<<<<<\n8001011F3001012HUN<<<<<<<<<<<0\nNAGY<<EVA<<<<<<<<<<<<<<<<<<<<");
    expect(result.found).toBe(true);
    expect(result.checksumsValid).toBe(false);
  });
});

describe("decision builder", () => {
  it("keeps document, liveness, and face-match signals distinct", () => {
    const result = buildDecision({
      document: { readable: true, internallyConsistent: true },
      liveness: { passed: true, confidence: 97, status: "SUCCEEDED" },
      faceMatch: { passed: true, similarity: 96 },
      livenessThreshold: 92,
      faceMatchThreshold: 90,
      reasons: [],
    });
    expect(result).toMatchObject({ identityConsistent: true, decision: "pass", liveness: { confidence: 97 }, faceMatch: { similarity: 96 } });
  });

  it("routes provider uncertainty to review rather than pass", () => {
    const result = buildDecision({
      document: { readable: true, internallyConsistent: true },
      liveness: { passed: true, confidence: 97, status: "SUCCEEDED" },
      faceMatch: { passed: true, similarity: 96 },
      livenessThreshold: 92,
      faceMatchThreshold: 90,
      reasons: ["aws_timeout"],
    });
    expect(result.decision).toBe("review");
  });
});

describe("privacy-safe errors", () => {
  it("retains an error category without returning the provider message", () => {
    const error = Object.assign(new Error("Sensitive document number: 123456"), { name: "AccessDeniedException" });
    expect(redactedLogContext("document.inspect", error)).toEqual({ operation: "document.inspect", code: "aws_permission_denied", retryable: false });
  });
});
