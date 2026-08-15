# AWS KYC + Face Liveness PoC

Curated portable import from the standalone AWS identity-verification PoC.

## Scope included here

- AWS Rekognition Face Liveness session creation/result handling
- server-side `CompareFaces`
- Textract `AnalyzeID` document inspection with a labelled Rekognition OCR fallback while Textract activation is pending
- TD1 MRZ parsing/checksum validation
- Hungarian name normalization and cross-document consistency checks
- separate document/liveness/face-match decision signals
- redacted provider error categories
- transient S3 cleanup logic
- deterministic provider/unit tests
- manual live-AWS preflight tests kept separate from the default test run

## Deliberately excluded from the import

- all `.env` or environment-secret files and environment-loader files
- Manus runtime/framework scaffolding
- generated UI component library
- Drizzle/database scaffolding
- hosting/build/debug artifacts
- account-specific IAM JSON and bucket-specific policy files
- the generated site shell

The full browser UI from the standalone Manus application is not copied into the CONSUL donor because it is coupled to that generated application stack. The backend/provider contract is the portable part intended for later integration.

## Current gate

The implementation is prepared for real AWS testing. Textract live validation remains gated on AWS account/service activation propagating. Live tests must be invoked explicitly and must use runtime-provided credentials; no credentials belong in this repository.

## Commands

```bash
cd poc/aws-kyc-liveness
npm install
npm test
npm run check
```

Default tests are local/mocked and do not intentionally perform live AWS calls.

Manual AWS checks:

```bash
npm run test:live
```

Only run the live command in an explicitly configured AWS test environment.

## Integration boundary

Keep this PoC outside CONSUL models/controllers until the provider interface is accepted. Identity verification, census/residence verification, and voting authorization remain separate layers.
