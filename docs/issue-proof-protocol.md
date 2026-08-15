# eDemocracy.hu Issue-Proof Protocol

**Purpose.** This protocol converts the project’s 39 documented blockers and oversights into evidence-producing actions. It distinguishes tasks that the private branch can implement from tasks that must be completed by an authorised tenant administrator, infrastructure operator, municipality, or qualified privacy/legal adviser.

> **Legal and privacy notice:** This is an implementation and evidence checklist, not legal advice. Census processing, data-sharing, electoral framing, accessibility obligations, contracts, and privacy impact assessments require review and sign-off by the appropriate qualified professionals and decision-makers.

## Evidence rules

A record becomes **proven** only when its named artifact is available, dated, attributable to the responsible role, and covers the stated acceptance condition. Source code or an unexecuted test plan alone is not proof of a production outcome. Tests must use a non-production tenant, synthetic census records, a controlled test telephone, and a disposable account; they must never interact with a live poll without written authorisation.

| Evidence class | Acceptable artifact |
|---|---|
| Source-level implementation | Commit SHA, reviewed diff, deterministic validator or passing automated test. |
| Tenant configuration | Export/screenshot from the correct tenant admin, redacted where necessary, plus a date and operator. |
| End-to-end flow | Test case, synthetic data fixture, timestamped outcome, and negative-case result. |
| Infrastructure | Configuration change record and post-change command output or monitoring evidence. |
| Governance/legal | Signed decision, agreement, policy, DPIA, legal review, or board/municipal record. |

## Blocker proof register

| Record | Required proof artifact | Responsible role | Branch can complete it? |
|---|---|---|---|
| B-01 Census data | Lawful data-source decision; approved synthetic fixture; successful and failing sandbox match record. | Municipality/data controller; tenant admin. | No. |
| B-02 Key-person risk | Named deputy, access inventory, recovery procedure, and signed continuity plan. | Service owner/operator. | No. |
| B-03 Hungarian localisation | Human-review sign-off for every enabled locale screen, plus route-by-route screenshot set. | Hungarian content owner. | Partly; reviewed overlay already supplied. |
| B-04 Geozones | Written inclusion/geozone rule and tested tenant configuration export. | Municipality; tenant admin. | No. |
| B-05 Pilot topic | Approved pilot charter naming topic, audience, timescale, and owner. | Municipality. | No. |
| B-06 TTSZ review | Completed requirements traceability review and explicit decision log. | Reviewers/product owner. | No. |
| B-07 TT tenant/support | Tenant-admin access test, named support contact, response commitment, and handover record. | Operator/tenant administrator. | No. |
| B-08 Recruitment path | Approved resident-recruitment plan with channels, eligibility, accessibility, and measurement. | Municipality/facilitation lead. | No. |
| B-09 Facilitation gap | Named facilitators, moderation rota, escalation process, and training evidence. | Service owner/municipality. | No. |
| B-10 SMS/helpdesk | Sandbox SMS send/receive evidence, provider configuration record, helpdesk runbook, and support test ticket. | SMS operator; support lead. | No. |

## Oversight proof register

| Record | Required proof artifact | Responsible role | Branch can complete it? |
|---|---|---|---|
| O-01 Lawful census basis | Written legal/data-protection assessment approving the proposed data flow. | Data controller; qualified privacy/legal adviser. | No. |
| O-02 DPA | Executed data-processing agreement defining parties, instructions, security, subprocessors, retention, and deletion. | Municipality; Webinform/operator; legal adviser. | No. |
| O-03 DPIA | Approved DPIA covering identity data, political-opinion risk, retention, access, and residual risks. | Data controller; DPO/privacy adviser. | No. |
| O-04 Security maintenance | Production commit, deployment record, and `curl -I https://edemocracy.hu` output showing HSTS; owner/patch and monitoring records. | Deployer/operator. | **Partly:** branch now enforces HTTPS and HSTS in production configuration. |
| O-05 AGPL obligation | Public source-offer URL for the exact deployed modified source and corresponding licence/notice verification. | Operator/legal adviser. | No; a private review repository is insufficient for a public deployment. |
| O-06 Political neutrality | Signed separation policy for identity, domains, operators, roles, branding, and tenant administration. | Municipality/operator governance. | No. |
| O-07 Fork drift | Upstream/Crowdin contribution record or documented release-rebase and translation-sync process. | Maintainer/localisation owner. | No. |
| O-08 Continuity plan | Same access escrow, deputy, and recovery evidence required for B-02. | Service owner/operator. | No. |
| O-09 Sustainability | Approved operating budget, commercial/support model, and renewal owner. | Municipality/operator. | No. |
| O-10 Procurement | Applicable procurement assessment and decision record. | Municipality procurement/legal function. | No. |
| O-11 Selection bias | Recruitment design, target segments, non-digital measures, and participant-distribution review. | Research/facilitation lead. | No. |
| O-12 Pilot survey design | Testable question set, sampling method, analysis plan, and approval. | Research/pilot owner. | No. |
| O-13 Deck overclaim | Corrected deck version and stakeholder approval. | Deck owner/communications lead. | No. |
| O-14 Moderation | Published policy/code of conduct, moderator capacity/rota, escalation SLA, and training evidence. | Moderation/service lead. | No. |
| O-15 Outcome commitment | Municipal decision stating what vote outcomes mean, who acts, and how feedback is published. | Municipality. | No; branch corrects the misleading public statement only. |
| O-16 Success criteria | Approved pilot scorecard with baselines, targets, owner, cadence, and exit criteria. | Pilot sponsor. | No. |
| O-17 Digital divide | Accessibility/inclusion plan, assisted/offline participation measures, and uptake evidence. | Municipality/service owner. | No. |
| O-18 Email deliverability | DNS record evidence for SPF/DKIM/DMARC, authenticated sending proof, seed-mail delivery results, and bounce-monitoring dashboard. | DNS/mail operator. | No. |
| O-19 Municipal owner | Named accountable municipal owner and written mandate. | Municipality. | No. |
| O-20 Broadcast asks | Decision/action log with owner, deadline, status, and escalation mechanism. | Project owner. | No. |
| O-21 Untested flows | Completed sandbox test run from sign-up through synthetic census match, SMS, final verification, and a negative case. | Tenant admin; SMS/census operator. | Partly; branch adds regression scenarios and test plan. |
| O-22 Support load | Forecast model, staffing plan, response targets, and pilot support metrics. | Support/service lead. | No. |
| O-23 Unread sources | Review notes for both primary sources and resulting decision-log updates. | Project owner/research lead. | No. |
| O-24 Undefined handover | Handover plan, access inventory, acceptance checklist, and named recipient sign-off. | Current owner and Dávid. | No. |
| O-25 Accessibility | Accessibility audit, remediation log, and current accessibility statement. | Accessibility specialist; public body. | Partly; branch removes the unsupported conformance claim. |
| O-26 Referendum framing | Qualified Hungarian legal review of terms, page wording, and process design. | Municipality/legal adviser. | No. |
| O-27 Live poll not voteable | Controlled tenant test with synthetic resident and test SMS, followed by authorised verification that the relevant non-live poll is voteable. | Tenant admin; SMS/census operator. | No. |
| O-28 Consent/document UI | Branch diff; validator pass; system-test pass; sandbox screenshot of the exact tenant form. | Developer; tenant admin. | **Partly:** source correction and validator exist; live tenant screenshot remains needed. |
| O-29 Ballot linkability/erasure | Data-flow review, approved retention policy, and source/database tests showing the authorised behaviour. | Data controller; developer; privacy adviser. | No. |

## Controlled sandbox test protocol

1. Obtain written authorisation for the **sandbox tenant**, a synthetic local-census fixture, and one controlled test telephone. Do not use production resident data or a live poll.
2. Record the exact deployed commit SHA and tenant name before testing.
3. Complete a successful path: registration → email confirmation → sign-in → `/verification` → residence match → SMS code → final verification.
4. Complete a negative path using a deliberately non-matching synthetic fixture; confirm rejection without exposing unnecessary data in the UI or logs.
5. Capture dated screenshots and redacted admin evidence for the local census, tenant locale configuration, SMS delivery, and final user verification state.
6. Test `curl -I https://<test-domain>` after deployment and retain the output showing `Strict-Transport-Security`; test the HTTP-to-HTTPS redirect separately.
7. Record defects, expected/actual results, operator, and cleanup of synthetic fixtures. Only then consider a production change request.

## Branch-owned implementation evidence

The private branch contains the following source-level changes that can be reproduced now:

```bash
git checkout feature/hu-localisation-ux-verification
python3 scripts/validate_hu_overlay.py
python3 scripts/validate_production_hardening.py
```

The first validator covers the Hungarian localisation/verification corrections. The second verifies that production code enables `assume_ssl`, mandatory `force_ssl`, and one-year subdomain HSTS. Deployment is still required before a real HTTP response can prove the header.
