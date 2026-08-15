# Curated AWS KYC PoC status

This branch contains only the portable identity-verification backend/provider subset from the uploaded standalone PoC.

## Included

- Textract `AnalyzeID` document inspection path
- Rekognition OCR fallback for the known Textract activation-pending state
- Rekognition Face Liveness session creation/result retrieval
- server-side `CompareFaces`
- TD1 MRZ parsing and checksums
- Hungarian name normalization
- separate document/liveness/face-match decision signals
- privacy-safe provider error categorization
- transient S3 cleanup logic
- local mocked tests
- one explicit live AWS preflight test, excluded from default tests

## Current live-AWS gate

Textract service/account activation still needs to propagate before the real document path can be accepted as live-verified. The live preflight can treat `SubscriptionRequiredException` as a labelled warning during that activation window.

## Not imported

The generated Manus application shell, UI component library, Drizzle/database scaffolding, hosting/debug helpers, account-specific IAM files, bucket-specific policy files, and browser app scaffolding were deliberately omitted.

No `.env` file, environment-loader file, or secret-bearing environment file from the source package is part of this curated import.

## What this proves

This is an identity-consistency PoC, not document-authenticity proof. OCR/MRZ consistency, liveness, and face similarity do not establish that a Hungarian identity document itself is genuine or unrevoked.
