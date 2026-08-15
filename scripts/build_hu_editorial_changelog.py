#!/usr/bin/env python3
"""Build a readable editorial changelog from the per-key TSV audit trails."""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUTO = ROOT / "docs/hungarian_localisation_editorial_changes.tsv"
MANUAL = ROOT / "docs/hungarian_localisation_editorial_manual_changes.tsv"
OUTPUT = ROOT / "docs/hungarian_localisation_editorial_changelog.md"


def rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    result = []
    with path.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if not row or row.get("file") == "file":
                continue
            result.append(row)
    return result


automated = rows(AUTO)
manual = rows(MANUAL)
auto_by_file = Counter(row["file"] for row in automated)
manual_by_file = Counter(row["file"] for row in manual)
priority = [row for row in manual if row["file"] in {"budgets.yml", "devise_views.yml", "verification.yml", "general.yml"}]

lines = [
    "# Hungarian localisation editorial changelog",
    "",
    "## Purpose and standard",
    "",
    "This record documents the second-pass editorial revision of the Hungarian CONSUL 2.5.0 localisation. The first machine-generated wording was frequently literal and grammatically unnatural. The revision standard uses formal **Ön** address, clear civic-platform terminology, natural Hungarian word order, and consistent labels for accounts, registration, proposals, votes, participatory budgeting, verification, and residence checking.",
    "",
    "Rails variables, HTML, URLs, Markdown destinations, protocol names, browser names, brands, and formatting tokens are retained verbatim where they are application syntax or identifiers rather than Hungarian prose.",
    "",
    "## Revision totals",
    "",
    "| Change class | Changed locale leaves | Description |",
    "|---|---:|---|",
    f"| Full-catalogue neural editorial draft | {len(automated):,} | All canonical English locale files were revisited through a checkpointed, token-preserving Hungarian draft pass. |",
    f"| Human editorial corrections | {len(manual):,} | High-visibility registration, verification, participatory-budget, navigation, debate, proposal, poll, search, and shared-interface strings were rewritten manually. |",
    "",
    "## Automated-draft changes by locale file",
    "",
    "| Locale file | Changed leaves |",
    "|---|---:|",
]
for filename, count in sorted(auto_by_file.items()):
    lines.append(f"| `{filename}` | {count:,} |")
lines.extend([
    "",
    "## Human editorial corrections by locale file",
    "",
    "| Locale file | Changed leaves | Focus |",
    "|---|---:|---|",
])
focus = {
    "budgets.yml": "Community-budget votes, project creation, ballots, results, and phases",
    "devise_views.yml": "Registration, login, password recovery, account confirmation, and organisation registration",
    "verification.yml": "Residence checks, consent, SMS, confirmation codes, and verified-account wording",
    "general.yml": "Navigation, comments, debates, proposals, polls, dashboard, search, shared actions, and notifications",
}
for filename, count in sorted(manual_by_file.items()):
    lines.append(f"| `{filename}` | {count:,} | {focus.get(filename, 'Editorial correction')} |")
lines.extend([
    "",
    "## Representative human-edited changes",
    "",
    "| Locale key | Previous wording | Revised wording | Editorial rationale |",
    "|---|---|---|---|",
])
for row in priority[:36]:
    previous = row["previous_hungarian"].replace("|", "\\|").replace("\n", " ")
    revised = row["revised_hungarian"].replace("|", "\\|").replace("\n", " ")
    key = row["key"].replace("|", "\\|")
    lines.append(f"| `{key}` | {previous} | {revised} | Formal Hungarian grammar, natural civic terminology, or clearer user action. |")
lines.extend([
    "",
    "## Complete machine-readable audit trails",
    "",
    "The complete per-key before/after records are retained in the following tab-separated files, including the English source value for every changed leaf:",
    "",
    "- `docs/hungarian_localisation_editorial_changes.tsv` — full-catalogue checkpointed editorial draft changes.",
    "- `docs/hungarian_localisation_editorial_manual_changes.tsv` — reviewed human corrections for the highest-visibility user journeys.",
    "",
    "## Validation requirements",
    "",
    "Before release, run the locale coverage audit and both source validators. Validate the Hungarian registration and identity-verification journey in the isolated synthetic preview. A final native-speaker review remains advisable for long-form policy, SDG, and administrative explanatory text before public production release.",
])
OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"Wrote {OUTPUT}; automated={len(automated)} manual={len(manual)}")
