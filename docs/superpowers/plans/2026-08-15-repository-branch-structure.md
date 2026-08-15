# Repository Branch Structure Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Preserve the pristine CONSUL 2.5.0 baseline, turn `main` into the eDemocracy integration branch, preserve completed workstreams, and make the root README the live project/checklist entry point.

**Architecture:** Keep the official upstream commit as `baseline/consul-2.5.0`. Advance `main` to the broad Hungarian remediation line, then reconcile other completed workstreams into `main` only when their differences are explicitly reviewed. Keep experimental work under `poc/*` and portable implementation work under `feature/*`.

**Tech Stack:** Git/GitHub branches, Markdown documentation, CONSUL Democracy 2.5.0.

## Global Constraints

- Keep the application on official CONSUL Democracy 2.5.0.
- Do not upgrade to 2.5.1.
- Preserve existing completed feature-branch history.
- Do not claim live AWS/Textract verification is complete until the provider gate clears and live tests pass.
- Keep company-fork-specific deployment changes out of this restructuring.

---

### Task 1: Preserve the pristine baseline

**Files:** none

- [ ] Create `baseline/consul-2.5.0` at `43704021e78b202af335ab93a5483610a8e039f0`.
- [ ] Verify the branch SHA exactly matches the official 2.5.0 commit.

### Task 2: Make the broad Hungarian remediation line the integration base

**Files:** branch refs only

- [ ] Advance `main` to the current head of `feature/hu-localisation-ux-verification` using a fast-forward.
- [ ] Verify `main` is ahead of `baseline/consul-2.5.0` and still has that baseline as its merge base.
- [ ] Preserve `feature/hu-localisation-ux-verification` as a historical/workstream branch.

### Task 3: Replace the upstream-only root README with the project README

**Files:**
- Modify: `README.md`

- [ ] Replace the upstream-only introduction with an eDemocracy project overview.
- [ ] Add the exact 2.5.0 baseline rule and branch map.
- [ ] Add completion status for Hungarian remediation and the KYC AWS verification gate.
- [ ] Add the technical checklist grouped by complete, active, actionable, gated, and stakeholder/legal blockers.
- [ ] Add verification/evidence pointers and the later company-fork porting model.
- [ ] Preserve upstream CONSUL attribution, documentation links, and AGPLv3 license information.

### Task 4: Preserve and correctly label the divergent UI regression workstream

**Files:**
- Modify: `README.md`

- [ ] Verify `feature/ui-localisation-regression` still exists at its completed head.
- [ ] Record that it diverges from the broad Hungarian catalogue/editorial branch after the shared remediation base.
- [ ] Do not destructively rewrite it.
- [ ] Add an explicit checklist item to reconcile its screenshot-backed evidence/tests into `main` after conflict review.

### Task 5: Verify final repository structure

**Files:** none

- [ ] Verify `baseline/consul-2.5.0` points to the pristine upstream SHA.
- [ ] Verify `main` points to project work and contains the project README.
- [ ] Verify both completed localisation branches still exist.
- [ ] Compare `main` to the baseline and confirm there is no version upgrade.
- [ ] Fetch the final README from `main` and confirm the branch map/checklist are present.
