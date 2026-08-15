# eDemocracy.hu Issue-Fix Evidence Audit

**Assessment date:** 2026-08-15
**Implementation examined:** the current `feature/hu-localisation-ux-verification` branch, including the published HTTPS/HSTS hardening change.
**Baseline:** CONSUL `2.5.0` (`43704021e78b202af335ab93a5483610a8e039f0`)
**Evidence boundary:** This audit compares the supplied project’s issue register with the private branch and its static validator/tests. The branch has **not** been deployed to `sandbox.edemocracy.hu` or `edemocracy.hu`; therefore, it cannot prove live configuration, legal, operational, security, email, census, SMS, governance, or end-to-end outcomes.

> **Conclusion:** The evidence does **not** show that all known issues are fixed. It proves one source-level form defect is corrected, shows five issues have a narrow or partial source-level remedy, and shows **no fix evidence in this branch for 33 of the 39 documented issues**. Any claim that all issues are fixed would be unsupported.

## Evidence standard

| Status | Meaning | Count |
|---|---|---:|
| **Implemented in source** | The branch contains a direct, inspectable change matching the documented defect; static validation covers the critical condition. Live deployment remains unproven. | 1 |
| **Partial source remedy** | The branch improves one aspect, but the project issue has a wider policy, completeness, operational, or deployment requirement. | 5 |
| **No fix evidence** | No change in the branch proves resolution of the issue. This does not prove the issue still exists; it means the supplied branch cannot evidence a fix. | 33 |
| **Total documented issues** | Ten blockers and 29 oversights in the supplied registers. | 39 |

## Direct and partial remedies evidenced by the branch

| Record | Project finding | Status | Branch evidence | What remains unproven or unresolved |
|---|---|---|---|---|
| **B-03** | Hungarian localisation incomplete. | **Partial source remedy** | `config/locales/hu-HU/edemocracy_hu.yml` supplies reviewed Hungarian copy for language naming, shared navigation/footer, registration, account verification, residence verification, help and accessibility. `scripts/validate_hu_overlay.py` requires the key Hungarian entries. | The project record describes an incomplete locale across the product. This branch does not contain a complete human-reviewed translation of every administrative and feature-specific screen. |
| **O-04** | Security patching and maintenance were unowned; the observed service lacked HSTS/CSP. | **Partial source remedy** | `config/environments/production.rb` now trusts the SSL proxy, enforces HTTPS unconditionally, and configures one-year HSTS for subdomains. `scripts/validate_production_hardening.py` checks the source settings. | The branch cannot prove deployment, real response headers, CSP rollout, monitoring, patch ownership, or an operational maintenance process. |
| **O-15** | Public help text made an unsupported promise that the council would accept and implement successful proposals. | **Partial source remedy** | The Hungarian `pages.help.proposals.description` now states that a proposal can proceed to a public vote and that the result is decided under the applicable local procedure; it does not state that the council will automatically implement it. The validator rejects the original unsupported phrase. | Correcting displayed copy does not establish a municipal commitment, decision rule, or written governance policy. |
| **O-21** | Core flows had never been tested end to end. | **Partial source remedy** | `spec/system/registration_verification_flow_spec.rb` covers Hungarian registration guidance → account action → verification wizard. `spec/system/verification/hungarian_residence_spec.rb` covers document labels, consent link, and wizard rendering. `docs/edemocracy_hu_test_plan.md` defines sandbox and production test stages. | The full Rails suite was not executable in the available environment, and no live sandbox/tenant end-to-end evidence exists. Census, SMS, and final verification are not proven. |
| **O-25** | The public accessibility page made an unqualified WCAG conformance claim. | **Partial source remedy** | The Hungarian accessibility copy now says the portal aims to follow WAI guidance and requires regular assessment, replacing the categorical conformance statement. | This is a claims correction, not an accessibility audit, a conformance report, or proof of compliance. |
| **O-28** | The census consent checkbox rendered a raw placeholder and the document list used Spanish `DNI`. | **Implemented in source** | The Hungarian consent string uses exactly `%{terms_url}`; document type is displayed as **Személyi igazolvány**; document help names Hungarian identity documents. The validator explicitly fails if `__MASZK_` or `DNI` remains. The Hungarian system spec asserts the terms link, absence of the mask token, and document options. | The code has not been deployed to the live tenant, so rendering under its exact theme/configuration still needs sandbox confirmation. |

## Complete blocker register

| Record | Issue | Evidence status | Evidence or required proof |
|---|---|---|---|
| **B-01** | Census data for verified users | **No fix evidence** | No municipal lawful-basis decision, test census fixture, local-census import evidence, or remote-census configuration is in the branch. |
| **B-02** | Key-person risk | **No fix evidence** | Requires ownership/continuity arrangements, not a localisation code change. |
| **B-03** | Hungarian localisation incomplete | **Partial source remedy** | See direct-remedy table; selected resident journeys are corrected, not the complete product locale. |
| **B-04** | Geozone decision pending | **No fix evidence** | No geozone policy/configuration or tenant evidence in the branch. |
| **B-05** | Only one pilot topic exists | **No fix evidence** | Requires a municipal pilot decision and content, not code evidence. |
| **B-06** | TTSZ requirements review never happened | **No fix evidence** | Requires completed requirements review and recorded approval. |
| **B-07** | TT tenant, admin rights and technical support | **No fix evidence** | No tenant administrator access/support agreement evidence. |
| **B-08** | Recruitment path for residents unclear | **No fix evidence** | Requires an outreach/recruitment plan and operational proof. |
| **B-09** | Facilitation and motivation gap | **No fix evidence** | Requires staffing/process commitment. |
| **B-10** | SMS gateway and user helpdesk | **No fix evidence** | The branch preserves the existing SMS UI but includes no provider credentials, deliverability test, support process, or helpdesk evidence. |

## Complete oversight register

| Record | Issue | Evidence status | Evidence or required proof |
|---|---|---|---|
| **O-01** | Lawful basis for the census extract | **No fix evidence** | Requires qualified legal/data-protection assessment and documented lawful basis. |
| **O-02** | No data processing agreement | **No fix evidence** | Requires an executed agreement, not a code change. |
| **O-03** | No DPIA; political opinions are special-category data | **No fix evidence** | Requires a completed DPIA and risk controls. |
| **O-04** | Security patching and maintenance unowned | **Partial source remedy** | Production code now enforces HTTPS and HSTS; deployment output, CSP rollout, monitoring, patch ownership, and maintenance process remain required. |
| **O-05** | AGPL-3.0 network copyleft obligation | **No fix evidence** | A private downstream repository does not itself prove compliant public source availability for a deployed modified service. |
| **O-06** | Political neutrality and TISZA entanglement | **No fix evidence** | Requires governance, operator, brand, and access separation. |
| **O-07** | Fork drift; translations not going upstream | **No fix evidence** | The repository is a traceable private downstream mirror, but no upstream contribution/Crowdin workflow proves that drift has been resolved. |
| **O-08** | Bus factor and no continuity plan | **No fix evidence** | Requires named successors, documentation, access escrow, and handover plan. |
| **O-09** | No commercial model or sustainability plan | **No fix evidence** | Requires a sustainable operating model. |
| **O-10** | Procurement and the free-favour trap | **No fix evidence** | Requires procurement/legal process evidence. |
| **O-11** | Selection bias in the recruitment plan | **No fix evidence** | Requires an inclusive recruitment design and measurement. |
| **O-12** | Pilot survey design is not answerable | **No fix evidence** | Requires revised research/survey design. |
| **O-13** | Stakeholder deck contains a factual overclaim | **No fix evidence** | No revised deck or approved correction is included. |
| **O-14** | No moderation policy, capacity, or code of conduct | **No fix evidence** | Requires policy, staffing, and operational process. |
| **O-15** | No commitment to outcome | **Partial source remedy** | Public help claim removed; a formal decision/outcome commitment still needs evidence. |
| **O-16** | No success criteria for pilot or project | **No fix evidence** | Requires agreed success criteria and measurement plan. |
| **O-17** | Digital divide excludes the most affected residents | **No fix evidence** | Requires offline/accessibility/inclusion measures. |
| **O-18** | Email deliverability will silently kill the launch | **No fix evidence** | No DMARC/DKIM configuration, sending-path changes, or delivery test exists in the branch. |
| **O-19** | No named municipal project owner | **No fix evidence** | Requires a named municipal owner and mandate. |
| **O-20** | Broadcast asks without deadline produce nothing | **No fix evidence** | Requires project-management process changes. |
| **O-21** | Core flows never tested end to end | **Partial source remedy** | Source-level regression scenarios and a test plan are present; no live end-to-end evidence exists. |
| **O-22** | Support load estimate is optimistic | **No fix evidence** | Requires support model, volume estimates, and service process. |
| **O-23** | Two primary sources remain unread | **No fix evidence** | Requires source review and updated conclusions. |
| **O-24** | Handover to Dávid is undefined | **No fix evidence** | Requires an agreed handover and access/documentation inventory. |
| **O-25** | Public-sector accessibility obligations | **Partial source remedy** | The false Hungarian claim is removed; formal accessibility assessment/compliance remains unproven. |
| **O-26** | “Szavazás” framing versus local referendum law | **No fix evidence** | The branch uses neutral guidance in selected help copy but does not supply legal framing or advice. |
| **O-27** | Live poll is running with no demonstrated verification path | **No fix evidence** | The UI/wiring is improved, but no controlled tenant test proves census/SMS path works or that a live poll is voteable. |
| **O-28** | Broken census consent string and Spanish ID list | **Implemented in source** | Corrected translation, validator, and system test prove intended source-level behavior. |
| **O-29** | Poll answers identity-linked and survive account erasure | **No fix evidence** | No change to data model, vote storage, or erasure behavior is included. |

## Reproducible branch evidence

The following commands reproduce the source-level evidence in a checked-out private branch:

```bash
git checkout feature/hu-localisation-ux-verification
python3 scripts/validate_hu_overlay.py
python3 scripts/validate_production_hardening.py

git diff 43704021e78b202af335ab93a5483610a8e039f0...HEAD -- \
  config/locales/hu-HU/edemocracy_hu.yml \
  app/views/users/registrations/success.html.erb \
  app/views/verification/residence/new.html.erb \
  spec/system/registration_verification_flow_spec.rb \
  spec/system/verification/hungarian_residence_spec.rb
```

The localisation validator checks that the selected Hungarian localisation keys exist, the consent link retains `%{terms_url}`, the raw mask token is absent, `DNI` is absent from the document help, the unsupported help promise is absent, the registration next-step UI exists, and the account component links to `verification_path`. The hardening validator checks the branch’s production HTTPS/HSTS source settings; a deployed response check is still required.

## Evidence required before any “all fixed” declaration

| Priority | Required evidence | Appropriate environment/owner |
|---|---|---|
| Critical | Written lawful-basis assessment, DPA, DPIA, political-neutrality separation, and decision on identity-data retention. | Municipality, data controller, qualified privacy/legal adviser, operator. |
| Critical | Controlled sandbox run from registration through census match, SMS delivery, and final verification using synthetic data; negative-case test; no live-poll interaction. | Tenant administrator and authorised SMS/census operator. |
| High | Complete Hungarian localisation review, accessibility assessment, email DNS/sending evidence, moderation policy, support plan, named owner, and continuity plan. | Content owner, accessibility specialist, Webinform/operator, municipality. |
| Before production | Release record, backup/rollback plan, monitoring/patch ownership, tenant-specific sign-off, and post-deploy visual evidence. | Deployer and named service owner. |

## References

[1]: `edemocracy.zip` → `knowledge/blockers/index.md` — supplied blocker register.
[2]: `edemocracy.zip` → `knowledge/oversights/index.md` — supplied oversight register.
[3]: [`feature/hu-localisation-ux-verification`](https://github.com/pappdavid/edemocracy-hu-localisation-verification/tree/feature/hu-localisation-ux-verification) — private branch implementation evidence.
[4]: [`docs/edemocracy_hu_test_plan.md`](https://github.com/pappdavid/edemocracy-hu-localisation-verification/blob/feature/hu-localisation-ux-verification/docs/edemocracy_hu_test_plan.md) — branch test plan and deployment boundary.
