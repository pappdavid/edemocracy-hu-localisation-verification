# Hungarian UI and Localisation Verification

**Branch:** `feature/ui-localisation-regression`  
**Baseline:** CONSUL Democracy **2.5.0**, commit `43704021e78b202af335ab93a5483610a8e039f0`  
**Verification date:** 2026-08-15  
**Evidence boundary:** This report records source-level and local automated-test evidence. It does **not** claim that the changes have been deployed to `edemocracy.hu` or a sandbox tenant, and it does not establish production configuration, legal compliance, municipal policy, census operation, or identity-verification outcomes.

> **Result:** The deterministic Hungarian UI defects in the agreed public, authentication, help, and supplied administration-screen scope were classified and remediated where a source-level fix was appropriate. The extended validator passed with **zero blocking critical-surface fallback, Spanish-fragment, placeholder, HTML/tag, terminology, or mechanically detected informal-address violations**. The focused system suite passed **5 examples**, and the pre-existing Hungarian verification suite passed **3 examples**.

| Verification area | Result | Evidence |
|---|---:|---|
| Critical Hungarian UI/localisation validator | Pass | `docs/evidence/hu-localisation-validator-report.txt` |
| Focused login, registration, header, footer, debates, proposals, help, and admin tests | 5 examples, 0 failures | `docs/evidence/focused-hungarian-system-specs.txt` |
| Pre-existing Hungarian registration/residence tests | 3 examples, 0 failures | `docs/evidence/existing-hungarian-verification-specs.txt` |
| YAML, Ruby syntax, and diff whitespace | Pass | Command record below |
| Screenshot integrity | SHA-256 recorded | `docs/evidence/screenshot-checksums.sha256` |

## Scope and method

The work used the provided Hungarian localisation reference, the existing compatible remediation branch, the original issue material, and the supplied administration screenshots. The implementation remained on the CONSUL 2.5.0 baseline; it did not upgrade application or dependency versions in source, redesign identity verification, change census behaviour, alter runtime/database configuration, or add legal or municipal-policy claims.

The remediation deliberately separates **deterministic interface text** from policy-dependent content. The branch corrects source-backed navigation, authentication, help, footer, public index, and administration labels. It leaves the actual privacy policy, terms of service, municipal governance commitments, and the binding/advisory meaning of votes as named stakeholder decisions rather than inventing substantive content.

| Source type | Material used | Purpose |
|---|---|---|
| Existing remediation | `feature/hu-localisation-ux-verification` | Retained reviewed verification, help, accessibility, and initial overlay fixes. |
| CONSUL baseline | Commit `43704021e78b202af335ab93a5483610a8e039f0` | Key structure and source-language comparison target. |
| Project reference | `edemocracy.zip` → `knowledge/platform/localization-hu.md` | Recorded public Hungarian defects and terminology context. |
| Supplied screenshots | `docs/evidence/screenshots/*.jpg` | Route/surface evidence for the administration census form and visible `DNI` / `angol` defects. |
| Source tracing | Views, helpers, components, and locale files in this branch | Mapped visible text to presentation and locale sources. |

## Issues investigated and outcome

The machine-readable record is [`ui-issue-map.yml`](ui-issue-map.yml). The table below is a concise human-readable summary.

| Issue | Surface and source | Result | Implemented evidence |
|---|---|---|---|
| #1 — tegeződés/magázódás | Login, registration, debate help; `devise_views.yml`, `general.yml` | **Implemented and verified** | Formal copy was added; the validator scans critical keys for detectable informal terms. |
| #2 — login wording | `new_user_session_path(locale: :hu)`; `devise_views.yml`, `general.yml`, `activerecord.yml` | **Implemented and verified** | Hungarian session title, actions, field labels, provider actions, and recovery links are tested. |
| #3 — header and language naming | Shared layout / locale switcher; `general.yml` | **Implemented and verified** | `Magyar`, `Nyelv:`, Hungarian navigation labels, and the absence of `angol` on the reviewed root page are tested. |
| #6 — footer wording | Shared footer; `general.yml` | **Implemented and verified** | Corrected footer strings are tested; validator rejects the recorded typo and case-error forms. |
| #7 — debate/proposal terminology | Public indexes; `general.yml` | **Implemented and verified** | `Viták`, `Javaslatok`, reviewed collaborative-legislation label, help labels, search, ordering, and proposal-list labels are covered. |
| #8 — debate/proposal help | Debate index and `/help`; `general.yml`, `edemocracy_hu.yml` | **Implemented and verified** | Formal neutral help text is covered; the validator rejects the unsupported automatic-implementation phrase. |
| #9 — Hungarian `ő` / `ű` rendering | Supplied local-census screenshot, locale UTF-8 files | **No longer reproducible in source** | Standard UTF-8 locale values render in the focused admin spec. No font/encoding configuration change was needed. |
| #10 — `javaslat` versus `ajánlat` | Proposal and help surfaces; `general.yml`, `edemocracy_hu.yml` | **Implemented and verified** | Proposal terminology is standardised and `ajánlat` is a validator violation. |
| O-28 / visible `DNI` | Public residence and screenshoted administration form; helper plus locale files | **Implemented and verified** | The shared document-type helper resolves to `Személyi igazolvány`; both public and administration regressions cover it. |
| Obvious English/Spanish fragments | Critical launch surfaces and reviewed locale values | **Implemented and verified within scope** | Validator reports 0 suspicious Spanish fragments and 0 suspicious English fallbacks on configured critical prefixes. |
| Interpolation and translated HTML | All overlapping English/Hungarian string keys | **Implemented and verified** | Validator reports 0 interpolation-placeholder and 0 HTML/tag mismatches. |

## Files changed

The changes are intentionally limited to localised UI source, regression coverage, validation tooling, and portable evidence.

| Area | Files |
|---|---|
| Public authentication | `config/locales/hu-HU/devise_views.yml`, `config/locales/hu-HU/activerecord.yml`, `config/locales/hu-HU/general.yml` |
| Public navigation, footer, debates, proposals, and shared controls | `config/locales/hu-HU/general.yml` |
| Screenshoted administration form | `config/locales/hu-HU/admin.yml`, `config/locales/hu-HU/activerecord.yml` |
| Validation | `scripts/validate_hu_overlay.py` |
| Focused regression coverage | `spec/system/hungarian_launch_localisation_spec.rb`, `spec/system/admin/hungarian_local_census_localisation_spec.rb` |
| Existing Hungarian test robustness | `spec/system/verification/hungarian_residence_spec.rb` |
| Evidence | `docs/evidence/ui-issue-map.yml`, this report, test logs, validation output, screenshot files, and checksums |

The existing residence test now checks two wizard-step labels case-insensitively. The rendered UI intentionally applies all-caps styling, so the original case-sensitive assertions failed even though the correctly localised words were visibly present. The change preserves the semantic Hungarian-copy regression check without coupling it to CSS capitalization.

## Validation tooling

`scripts/validate_hu_overlay.py` is now a CONSUL 2.5.0-aware Hungarian localisation checker. It merges the standard `config/locales/hu-HU/*.yml` files, compares their leaf keys to the `en` baseline, and distinguishes an incomplete locale report from a blocking launch-critical regression.

| Check | Default behaviour | Current result |
|---|---|---:|
| Missing keys versus CONSUL 2.5.0 | Reports all missing Hungarian baseline keys; `--strict-missing` makes them blocking. | 4,335 reported |
| Exact source-language fallback | Reports equal English/Hungarian values. | 13 reported, none on defined critical text surfaces |
| Suspicious English on critical surfaces | Blocking when detected. | 0 |
| Suspicious Spanish fragments | Blocking when detected. | 0 |
| Placeholder parity | Blocking when source and Hungarian `%{…}` variables differ. | 0 mismatches |
| HTML/tag parity | Blocking when source and Hungarian tag sequences differ. | 0 mismatches |
| Terminology violations | Blocks the recorded bad labels, `DNI`, `ajánlat`, and the outcome promise. | 0 |
| Mechanically detectable informal address | Blocks matches on defined critical surfaces. | 0 |

The validator intentionally does **not** misrepresent the Hungarian locale as complete. Its 4,335 missing-key report records the remaining localisation backlog, while the configured critical-surface checks provide a reproducible regression gate for this remediation package.

## Automated tests executed

The test environment used the repository’s Ruby `3.3.11`, a disposable local PostgreSQL test database, and locked project dependencies. No project runtime/database source files were modified for this setup.

```bash
python3 scripts/validate_hu_overlay.py

DB_HOST=/var/run/postgresql RAILS_ENV=test bundle exec rspec \
  spec/system/hungarian_launch_localisation_spec.rb \
  spec/system/admin/hungarian_local_census_localisation_spec.rb

DB_HOST=/var/run/postgresql RAILS_ENV=test bundle exec rspec \
  spec/system/registration_verification_flow_spec.rb \
  spec/system/verification/hungarian_residence_spec.rb

git diff --check
ruby -c spec/system/hungarian_launch_localisation_spec.rb
ruby -c spec/system/admin/hungarian_local_census_localisation_spec.rb
```

| Test artifact | Outcome | Coverage |
|---|---:|---|
| `focused-hungarian-system-specs.txt` | **5 examples, 0 failures** | Login, registration, header, footer, debates, proposals, help, and supplied administration form. |
| `existing-hungarian-verification-specs.txt` | **3 examples, 0 failures** | Existing registration-to-verification and Hungarian residence flows. |
| `hu-localisation-validator-report.txt` | **Pass** | Critical locale regressions, source-language fallbacks, Spanish/English fragments, placeholders, tags, terminology, and formality. |

## Screenshot evidence and source mapping

The project archive contains two relevant screenshot assets for the administration surface. They are stored in the branch under `docs/evidence/screenshots/` and checked by [`screenshot-checksums.sha256`](screenshot-checksums.sha256).

| Screenshot | Identified route/surface | Visible observation | Mapped source | Status |
|---|---|---|---|---|
| `edemocracy-production-census-DNI-2026-08-07.jpg` | Local-census record form; equivalent source route `new_admin_local_census_record_path(locale: :hu)` | `DNI` appears under a Hungarian document-type label; selector names Hungarian as `angol`. | `app/helpers/verification_helper.rb`; `verification.residence.new.document_type.*`; `admin.local_census_records.*`; `activerecord.attributes.local_census_record.*`; `i18n.language.name`. | **Implemented and verified in source** |
| `edemocracy-production-census-document-types-2026-08-07.jpg` | Same local-census record form before selection | Establishes the form route and shared selector context; corroborates `angol` label defect. | Same as above. | **Implemented and verified in source** |

The screenshot evidence is used only to map and verify visible text. It is **not** evidence for changes to census data, identity-verification policy, local-census configuration, or tenant administration.

## Unresolved items and stakeholder/content decisions

| Item | Classification | Required next step |
|---|---|---|
| 4,335 missing Hungarian 2.5.0 baseline keys | **Localisation backlog** | Continue human-reviewed translation in small, module-specific batches; use `--strict-missing` only when a full locale is a release requirement. |
| 13 exact fallback values | **Reported, non-blocking** | Mostly accepted proper names, product names, browser names, `SMS`, or `CONSUL DEMOCRACY`; review only if product style requires Hungarianisation. |
| Privacy policy body and deployed target | **CONTENT_DECISION_REQUIRED_PRIVACY_POLICY** | Stakeholder/legal owner must provide the approved content and link destination. |
| Terms of service body and deployed target | **CONTENT_DECISION_REQUIRED_TERMS_OF_SERVICE** | Stakeholder/legal owner must provide the approved content and link destination. |
| Binding/advisory meaning of votes and proposals | **CONTENT_DECISION_REQUIRED_MUNICIPAL_GOVERNANCE** | Municipality must approve governance wording; current help copy intentionally remains neutral. |
| Production/sandbox visual confirmation | **Deployment evidence required** | Run the same focused routes after authorised deployment and archive fresh screenshots. |

## References

[1]: `edemocracy.zip` → `knowledge/platform/localization-hu.md` — supplied Hungarian localisation reference and defect inventory.

[2]: `docs/evidence/ui-issue-map.yml` — machine-readable issue, screenshot, route, source, test, and status map.

[3]: `docs/evidence/hu-localisation-validator-report.txt` — final validator output.

[4]: `docs/evidence/focused-hungarian-system-specs.txt` — focused surface-system-test result.

[5]: `docs/evidence/existing-hungarian-verification-specs.txt` — pre-existing Hungarian verification-test result.

[6]: `docs/evidence/screenshots/` and `docs/evidence/screenshot-checksums.sha256` — portable supplied screenshot evidence and integrity data.
