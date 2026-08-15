# eDemocracy Hungary — CONSUL Democracy 2.5.0 remediation donor

This repository is the **reference implementation and remediation donor** for the Hungarian eDemocracy deployment built on CONSUL Democracy.

It is intentionally pinned to **CONSUL Democracy 2.5.0**. The goal is to implement and verify portable fixes here, then rebase/cherry-pick/port them onto the company deployment fork when that fork becomes available.

> **Baseline rule:** do not upgrade this repository to CONSUL Democracy 2.5.1. `baseline/consul-2.5.0` is the immutable three-way merge/rebase anchor.

## Branch structure

| Branch | Purpose | State |
|---|---|---|
| `baseline/consul-2.5.0` | Pristine official CONSUL Democracy 2.5.0 at `43704021e78b202af335ab93a5483610a8e039f0` | Reference only |
| `main` | Current eDemocracy integration branch | Active |
| `feature/hu-localisation-ux-verification` | Broad Hungarian catalogue, editorial rewrite, verification UX, preview helpers and evidence | Completed source workstream, preserved |
| `feature/ui-localisation-regression` | Screenshot-backed UI/localisation remediation, focused regression tests and evidence | Completed, pending reconciliation into `main` |
| `feature/*` | Portable engineering work intended for later company-fork porting | Active work |
| `poc/*` | Experimental work that must remain isolated until explicitly accepted | Proof of concept |

The two completed localisation branches diverged after the shared remediation base. Their history is intentionally preserved instead of being rewritten into one opaque commit pile. `main` currently follows the broader Hungarian catalogue/editorial line; the focused UI-regression branch still needs an explicit reconciliation pass before its extra evidence/tests are merged.

## Current status

### Completed / established

- [x] Preserve the official CONSUL Democracy 2.5.0 baseline.
- [x] Move the project default/integration work onto `main` while keeping the pristine baseline separately.
- [x] Initial Hungarian verification localisation and UX fixes.
- [x] Hungarian verification-facing labels and document terminology cleanup.
- [x] Full Hungarian locale catalogue generation against the 2.5.0 source tree.
- [x] Hungarian catalogue validation and coverage audit.
- [x] Natural Hungarian civic-language editorial rewrite.
- [x] Translation/editorial changelog generation.
- [x] Hungarian localisation validator and production-hardening validator.
- [x] Screenshot-backed UI/localisation regression workstream completed on `feature/ui-localisation-regression`.
- [x] Focused UI/localisation regression verification completed there with **8 examples, 0 failures** and **0 blocking critical-surface localisation regressions**.
- [x] Original issue evidence/proof protocol documented.
- [x] Local/runtime preview helper scripts added to the broad Hungarian remediation branch.

### Integration work still required

- [ ] Reconcile `feature/ui-localisation-regression` into `main` after reviewing overlapping locale/validator changes.
- [ ] Preserve the stronger screenshot evidence and focused regression specs during that reconciliation.
- [ ] Add donor-specific CI for `main`, `feature/**`, `fix/**` and pull requests.
- [ ] Make the Hungarian validator + focused system specs mandatory donor acceptance checks.
- [ ] Add an exact regression reproduction for original issue #17, verified-user registration HTTP 422.
- [ ] Reconcile the original 17-item issue tracker into verified fixed / reopened / blocked / obsolete states.

## Master technical checklist

### A. Hungarian UI and localisation

- [x] Full 2.5.0 Hungarian catalogue exists.
- [x] Critical public-facing Hungarian wording has been remediated.
- [x] Civic terminology received an editorial rewrite.
- [x] Localisation coverage/validation tooling exists.
- [x] Screenshot-backed regression package exists on its completed feature branch.
- [ ] Merge the extra UI-regression evidence/specs into `main` without losing the broader catalogue/editorial work.
- [ ] Keep translation correctness separate from institutional/policy copy.
- [ ] Continue non-blocking editorial review of low-priority catalogue strings as needed.

### B. Application acceptance and runtime verification

- [ ] Create the project-specific end-to-end acceptance suite.
- [ ] Registration → confirmation → login/logout.
- [ ] Debate creation/read/comment journey.
- [ ] Proposal creation/support journey.
- [ ] Residence-verification journey with synthetic residents.
- [ ] Verified-user voting journey.
- [ ] Poll-officer/officing journey.
- [ ] Negative tests for census mismatch, wrong DOB/postcode, duplicate identity, wrong geozone and duplicate voting.
- [ ] Emit screenshots/evidence for failed acceptance tests.
- [ ] Use this suite later as the company-fork port acceptance gate.

### C. Local Census and remote census test layer

- [ ] Build synthetic Hungarian resident fixtures/factories.
- [ ] Test Local Census CSV import and matching behavior.
- [ ] Cover malformed input, duplicates, Unicode/whitespace and not-found cases.
- [ ] Build a deterministic fake remote-census service.
- [ ] Cover found / not found / `district_code` / timeout / provider error / malformed response.
- [ ] Document the exact CONSUL 2.5.0 census-adapter contract.
- [ ] Ensure census identity fields are not leaked to logs.

### D. Geozones

- [ ] Characterize stock `Geozone.census_code` behavior.
- [ ] Prove eligible vs. ineligible residents with a synthetic `district_code`.
- [ ] Keep the optional Local Census `district_code` implementation on an isolated `poc/*` branch.
- [ ] Do not merge a Local Census schema extension until the real census backend is known.

### E. Tenant isolation

- [ ] Test tenant-local data isolation.
- [ ] Test tenant-local admin boundaries.
- [ ] Test settings, branding, locale/content, polls, proposals and debates across tenants.
- [ ] Test host routing.
- [ ] Re-run the same isolation suite after the later company-fork port.

### F. Ballot/privacy characterization

- [ ] Characterize the stock `Poll::Answer -> author` relationship in executable tests.
- [ ] Trace admin/API/export visibility of voter-answer linkage.
- [ ] Characterize online voting separately from officing/onsite voting.
- [ ] Characterize account erasure after verification and voting.
- [ ] Document what identity/voting relationships remain after normal erasure.
- [ ] Do not redesign ballot anonymity until the required secrecy model is explicitly decided.

### G. PII and logging safety

- [ ] Test that document number, DOB, phone number and SMS codes do not leak into logs.
- [ ] Prevent full census payload logging.
- [ ] Add structured non-identifying error codes.
- [ ] Verify Rails sensitive-parameter filtering.

### H. Email / SMS / deployment-independent integration tests

- [ ] Add transactional-mail test doubles and tenant/locale/link checks.
- [ ] Add fake SMS adapter with success/error/timeout/invalid/expired-code cases.
- [ ] Keep real SMTP/SMS provider configuration outside portable donor commits.

### I. Security/configuration

- [x] Initial HTTPS/HSTS hardening exists as a deployment-sensitive change.
- [ ] Keep HSTS/force-SSL assumptions separate from portable application fixes.
- [ ] Add static security-header checks.
- [ ] Add secret/config presence validation and repository secret scanning.
- [ ] Prepare CSP report-only validation before any production enforcement.

### J. Company-fork portability

- [ ] Add `scripts/compare_target_fork.sh`.
- [ ] Add `scripts/check_portability.py`.
- [ ] Add a machine-readable donor change manifest.
- [ ] Document changed files, baseline hashes, portability, conflict risk and required tests per patch.
- [ ] When the company fork arrives, compare it against `baseline/consul-2.5.0` before porting changes.
- [ ] Prefer narrow cherry-picks/ports over one giant merge.
- [ ] Run the donor acceptance suite after every port batch.

### K. AWS KYC / identity-verification PoC — parallel track

This work is a **parallel PoC track**, not yet the production municipal identity-verification system.

- [x] Deterministic synthetic KYC core implemented.
- [x] Hungarian personal-ID validation implemented.
- [x] MRZ parsing/checksum validation implemented.
- [x] Name and cross-document DOB consistency checks implemented.
- [x] Textract integration path implemented.
- [x] Rekognition `CompareFaces` integration path implemented.
- [x] Synthetic AWS-shaped mocks, redacted result model, FastAPI backend and test fixtures implemented.
- [~] Live AWS verification is waiting for AWS account/service verification to propagate so Textract can be exercised.
- [ ] Run real Textract document extraction after AWS activation.
- [ ] Run real Rekognition comparison/liveness validation after AWS activation.
- [ ] Test the PoC on an explicitly experimental/private route on the project owner's site before any CONSUL integration.
- [ ] Keep identity verification, residence verification and voting authorization as separate layers.
- [ ] Keep real biometric municipal-user use behind a legal/data-processing decision gate.

## External decision gates

The following are intentionally **not** engineering decisions:

- [ ] Final privacy-policy wording.
- [ ] Final terms-of-service wording.
- [ ] Lawful basis and controller/processor model for municipal census data.
- [ ] Retention rules for identity/census/verification data.
- [ ] Required ballot-secrecy model and whether operator/database-linkable votes are acceptable.
- [ ] Geographic eligibility for the real pilot.
- [ ] Whether a poll/result is advisory or binding and what consequence it has.
- [ ] Final municipal governance/help wording.
- [ ] Whether biometric KYC will be used for real municipal users and under what retention model.

## Verification and evidence

Useful project-specific files currently on `main` include:

- `docs/complete_hungarian_localisation.md`
- `docs/hungarian_localisation_editorial_changelog.md`
- `docs/hungarian_localisation_editorial_changes.tsv`
- `docs/hungarian_localisation_editorial_manual_changes.tsv`
- `docs/edemocracy_hu_test_plan.md`
- `docs/issue-fix-evidence-audit.md`
- `docs/issue-proof-protocol.md`
- `artifacts/hu_locale_coverage_audit.json`

The completed screenshot-backed workstream additionally contains `docs/evidence/` and its focused system specs on `feature/ui-localisation-regression` until reconciliation is complete.

Typical focused checks:

```bash
python3 scripts/validate_hu_overlay.py
bundle exec rspec spec/system/registration_verification_flow_spec.rb
bundle exec rspec spec/system/verification/hungarian_residence_spec.rb
```

Do not interpret a generated translation or a recorded tracker result as verification by itself. A remediation is considered closed when its expected behavior is reproduced by a test or documented evidence against the applicable branch/runtime.

## Later company-fork porting model

```text
baseline/consul-2.5.0
        |\
        | \__ company fork ............. future deployment target
        |
        \____ main ..................... verified donor remediation
                 |
                 +-- feature/* ......... portable workstreams
                 +-- poc/* ............. isolated experiments
```

When the company fork becomes available, use the pristine baseline as the common ancestor, classify downstream differences, then port the verified donor changes with their tests/evidence.

## Upstream CONSUL Democracy

This repository is based on [CONSUL Democracy](https://github.com/consuldemocracy/consuldemocracy), an open-source citizen participation and open-government platform.

Upstream documentation: <https://docs.consuldemocracy.org/>

The baseline used here is **CONSUL Democracy 2.5.0**.

## License

CONSUL Democracy and this derivative repository are published under the **GNU Affero General Public License v3 (AGPL-3.0)**. See `LICENSE-AGPLv3.txt`.
