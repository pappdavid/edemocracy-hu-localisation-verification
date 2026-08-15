# Complete Hungarian localisation record

## Scope and coverage

The branch now includes a complete Hungarian catalogue corresponding to all **30** canonical English CONSUL 2.5.0 locale files. The coverage audit reports **4,629 English leaves**, **4,630 Hungarian leaves**, and **0 missing keys**. The one additional Hungarian key, `polls.index.filter`, supplies an application key requested by the poll-index view but absent from the upstream English catalogue; it prevents Rails from rendering the translation-missing fallback.

The equality comparison reports 57 intentionally identical values. They consist of product and third-party brands, browser names, acronyms and protocol names, URLs, dynamic interpolation-only values, date/number format directives, units, and social-network identifiers. They are not untranslated application wording.

## Translation and safeguards

The complete catalogue was generated through the reproducible offline generator at `scripts/translate_complete_hungarian_locales_offline.py`. It translates ordinary text while structurally retaining Rails interpolation values, format directives, HTML, URLs, and Markdown-link destinations. It applies a civic-platform glossary and reviewed eDemocracy-specific overrides last. The existing language-model generator remains included for environments where that backend is available.

The catalogue contains targeted terminology corrections for account, registration, verification, residence verification, voting, proposals, collaborative legislation, participatory budgeting, filters, and accessibility-facing browser labels. A native Hungarian editorial review remains appropriate before a public production release, particularly for longer informational paragraphs; this is an editorial-quality review, not a coverage gap.

## Validation results

| Check | Result |
|---|---|
| English/Hungarian structural coverage audit | 4,629 English leaves; 4,630 Hungarian leaves; 0 missing |
| Protected token preservation | Enforced by the generator before every batch checkpoint is saved |
| Reviewed overlay validator | Passed |
| Production HTTPS/HSTS hardening validator | Passed |
| Git whitespace check | Passed |
| Synthetic Hungarian identity journey | Passed: sign-in, local census residence match, development SMS stub, SMS confirmation, and final-step transition |
| Representative public preview pages | Home, sign-in, registration, debates, proposals, polls, budgets, legislation processes, and help all returned HTTP 200 with no common residual English UI candidates |

## Preview

The safe local preview uses only the synthetic identity fixture and development-only SMS stub. It is available at:

<https://3001-ie555xnvgu5zbpvb91gyn-c62a25fe.us3.manus.computer/?locale=hu>

The synthetic account is `identity-preview@example.test` with password `PreviewOnly2026!`. The local-only residence test record uses document `12345680X`, date of birth `1980-01-15`, postal code `1111`, and the development SMS step. No real census record, SMS credential, resident data, or live poll is used.
