# Hungarian Localisation, UX/UI and Identity-Verification Test Plan

## Purpose and scope

This branch provides a reviewed Hungarian localisation overlay and a small user-interface improvement for the existing CONSUL 2.5.0 residence-verification flow. It is deliberately a **downstream deployment branch**, based on the upstream `2.5.0` release used by eDemocracy.hu, so that an eDemocracy developer can review the diff, cherry-pick the commits, or merge the branch into the existing eDemocracy codebase without inheriting unrelated production data or configuration.

The branch does **not** change census matching, SMS delivery, retention, permissions, or voter eligibility. Those functions depend on tenant configuration, municipal data governance, and protected credentials; they must be verified in a controlled environment with non-production test records.

## Registration-to-verification journey

The identity-verification route is now explicit in the registration UI while preserving the secure existing sequence. After registration, the completion page tells the resident to confirm their email address first. Once signed in, **Saját fiók** displays the Hungarian **Fiókom ellenőrzése** action, which uses CONSUL’s existing `/verification` router to continue through **Lakóhely**, **Megerősítő kód**, and **Végső ellenőrzés**. No identity document or SMS step is exposed before authentication and email confirmation.

| Workstream | Delivered change | Expected result |
|---|---|---|
| Localisation | Adds the `hu` locale and a reviewed Hungarian overlay for shared navigation, footer, help/accessibility copy, and the verification journey. | The language selector displays **Magyar** and the covered resident-facing screens use correct Hungarian. |
| UX/UI | Replaces the blank document-type select prompt with the existing shared “Kérjük, válasszon” prompt. | Residents are asked to make an explicit document-type choice. |
| Identity-verification UI | Corrects the visible Spanish `DNI` label to **Személyi igazolvány**, corrects document help, and restores the census-terms link interpolation. | The sensitive document-data form is understandable, and its consent link contains no raw mask token. |
| Public-content accuracy | Rewrites the Hungarian help and accessibility copy that overpromised council implementation or declared unverified conformance. | The interface avoids commitments and accessibility claims that have not been approved or audited. |

## Automated checks

The branch includes a deterministic YAML and regression-content check that does not require access to a census, SMS provider, or production database.

```bash
python3 scripts/validate_hu_overlay.py
```

It also adds `spec/system/verification/hungarian_residence_spec.rb`. The upstream GitHub Actions workflow will run that scenario as part of the test suite after the branch is pushed or opened as a pull request.

## Three-track test matrix

The requested three areas should be tested separately. Do not use an actual resident’s identity document or telephone number in any test.

| Track | Controlled test procedure | Pass criteria | Owner / prerequisite |
|---|---|---|---|
| 1. Registration and localisation | Register a disposable account, confirm its email address, sign in, select **Magyar**, then review the completion page, **Saját fiók**, footer, navigation, `/help`, `/accessibility`, and `/residence/new`. | The completion page states the next identity-verification step; **Fiókom ellenőrzése** opens the wizard; “Magyar” is shown; the footer contains no “angol”, “korányzat”, “hasznája”, or incorrect city-case copy; help/accessibility wording matches approved policy. | Application deployer; locale must be enabled for the tenant. |
| 2. UX/UI | Open `/residence/new` as a disposable test account and inspect the document selector and consent checkbox. | The selector begins with “Kérjük, válasszon”; choices are **Személyi igazolvány**, **Útlevél**, and **Lakcímkártya**; no `DNI` or `__MASZK_0__` is visible; the terms link opens correctly. | Application deployer; no census connection required for the screen-level test. |
| 3. Identity verification | In a non-production tenant, create one clearly labelled Local Census test fixture, use a disposable account and test telephone, then complete the residence, SMS, and final-verification flow. Repeat once with an intentionally non-matching fixture. | The matching test account reaches the configured verification level; the non-matching account is refused with the Hungarian error; no real citizen data is used. | Tenant administrator plus authorised census/SMS operator. |

## Environment order

Run the same three tracks in the following order. This order limits risk and keeps the production environment free of experimental identity data.

| Order | Environment | Permitted activity | Prohibited activity |
|---|---|---|---|
| 1 | Private branch CI or local Docker installation | Automated system test and manual UI review with generated fixtures. | Production credentials or municipal source data. |
| 2 | `sandbox.edemocracy.hu` sandbox tenant, after a controlled deployment of this branch | Full three-track validation using disposable accounts, a synthetic local-census record, and an authorised test SMS number. | Testing against a live municipal poll or uploading real resident data. |
| 3 | `edemocracy.hu` default/production tenant, only after sandbox sign-off and change approval | Read-only/smoke confirmation of the locale and form presentation; a controlled end-to-end verification only if authorised by the data controller. | Creating real test users, altering census records, changing SMS secrets, or voting in a live poll without written approval. |

The public vendor demo is useful only for comparing upstream behavior. It cannot validate this private branch because it does not run this branch’s code.

## Deployment checklist

The server-side deployer should preserve existing secrets and database data. The branch itself contains neither a migration nor a secret. Before enabling the locale for a tenant, take a database backup and record the deployed commit SHA.

1. Fetch the private repository and check out `feature/hu-localisation-ux-verification`.
2. Install the normal application dependencies and run the existing test suite.
3. Deploy through the existing eDemocracy release process; do not replace tenant databases or secret files.
4. In each intended tenant, enable the `hu` locale in the administrative locale settings and leave English as a fallback during the review period.
5. Execute the three-track matrix above and capture screenshots of the covered pages.
6. Promote only after the Hungarian content owner, tenant administrator, and data controller approve the results.

## Merge procedure for the eDemocracy developer

This repository is a **private downstream mirror** rather than a GitHub network fork. GitHub does not allow a public repository to be forked directly into a private repository. The repository has two remotes configured: `origin` is the private review repository and `upstream` is `consuldemocracy/consuldemocracy` at tag `2.5.0`.

To merge the finished changes into the existing eDemocracy source, the developer should add this private repository as a remote, inspect the diff, and cherry-pick the implementation commit(s):

```bash
git remote add edemocracy-hu-private https://github.com/pappdavid/edemocracy-hu-localisation-verification.git
git fetch edemocracy-hu-private
git diff <eDemocracy-base-ref>..edemocracy-hu-private/feature/hu-localisation-ux-verification -- \
  config/application.rb config/environments/test.rb config/locales/hu-HU \
  app/views/verification/residence/new.html.erb spec/system/verification
# Review the commits, then cherry-pick the selected commit SHA(s).
git cherry-pick <commit-sha>
```

If the production codebase already has a local Hungarian translation bundle, retain it and merge only the reviewed keys in `config/locales/hu-HU/edemocracy_hu.yml`. Do not overwrite an existing production census integration or tenant-specific verification settings with this branch.

## Explicit completion boundary

The overlay covers the defects documented in the supplied evidence and the complete resident-verification journey. It does not claim to be a complete translation of every administrative and feature-specific screen. Any wider translation should be completed through an approved translation workflow and reviewed by a Hungarian-language content owner before release.
