# AWS KYC PoC integration notes

The portable contract is intentionally isolated from CONSUL. A later integration should call the provider through `IdentityVerificationProvider` and persist only a minimal verification result, not raw document/selfie/liveness media.

Suggested durable fields:

- verification id
- verification method/version
- decision (`pass`, `fail`, `review`)
- reason codes
- verified timestamp
- opaque/pseudonymous subject token once that layer is added

Keep these concepts separate:

1. identity consistency
2. residence/census eligibility
3. poll/voting authorization

The current provider is experimental and must not be wired into real municipal-user verification until the technical live-AWS tests and data-processing decisions are complete.
