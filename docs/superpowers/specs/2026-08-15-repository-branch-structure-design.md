# Repository and Branch Structure Design

## Goal

Turn this repository from a pristine upstream mirror with useful work hidden on feature branches into the actual eDemocracy integration repository, while preserving an immutable CONSUL Democracy 2.5.0 reference point for later rebasing onto the company fork.

## Baseline

- Official CONSUL Democracy 2.5.0 commit: `43704021e78b202af335ab93a5483610a8e039f0`.
- The project must remain on CONSUL Democracy 2.5.0. This work does not upgrade to 2.5.1.
- The current `main` points at the pristine upstream commit.
- `feature/hu-localisation-ux-verification` contains the broad Hungarian catalogue/editorial remediation and local preview helpers.
- `feature/ui-localisation-regression` contains the completed screenshot-backed UI/localisation regression package and evidence.
- Those two workstreams diverged after commit `689db9c0a2097a207dfaa61b4f92b10bf4fd017e` and should remain independently attributable until reconciled.

## Target branch model

### `baseline/consul-2.5.0`

Immutable reference branch pointing at the official 2.5.0 baseline commit. It is the three-way merge/rebase anchor for later company-fork work.

### `main`

Default project integration branch. It should no longer be the untouched upstream branch. It should contain the current broad Hungarian remediation line plus project-facing documentation/checklists. Additional verified workstreams are merged into this branch after reconciliation.

### `feature/*`

Active or completed portable engineering workstreams that may need independent review or later porting. Existing completed branches are preserved rather than destructively rewritten.

### `poc/*`

Experimental work that must not be treated as production-ready, such as Local Census `district_code` experiments or AWS KYC/liveness work if it is later placed in this repository.

### Existing completed branches

- `feature/hu-localisation-ux-verification`: source line for the broad Hungarian catalogue/editorial work.
- `feature/ui-localisation-regression`: source line for screenshot-backed regression/evidence work.

They remain available for attribution and later conflict resolution even after `main` becomes the integration branch.

## README design

The root README becomes project-facing and contains:

1. project purpose and the explicit 2.5.0 baseline rule;
2. branch map;
3. current completion status;
4. live technical checklist grouped as complete, in progress, actionable, gated, and external-decision blocked;
5. verification commands/evidence pointers;
6. later company-fork porting model;
7. upstream CONSUL attribution and license information.

The README must not claim KYC live-AWS validation is complete while AWS/Textract account verification is still propagating.

## Integration policy

- Preserve the two completed localisation branches.
- Advance `main` to the broad Hungarian remediation branch as the starting integration state.
- Do not silently merge the divergent UI-regression branch if GitHub reports conflicts. Preserve it and document reconciliation as an explicit integration task.
- Future portable work branches from `main`; experimental work branches under `poc/*`.
- The company fork remains the deployment target, not the development baseline.

## Success criteria

- `baseline/consul-2.5.0` points exactly at `43704021e78b202af335ab93a5483610a8e039f0`.
- `main` points at project work, not pristine upstream.
- The root README accurately explains the repository and includes the current checklist.
- Existing completed feature branches remain available.
- No production/company-fork assumptions are introduced.
- No application version upgrade occurs.
