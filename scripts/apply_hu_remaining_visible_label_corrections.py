#!/usr/bin/env python3
"""Replace residual visible English labels found by the equality audit."""
from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
CHANGELOG = ROOT / "docs/hungarian_localisation_editorial_manual_changes.tsv"

OVERRIDES = {
    "activemodel.yml": {
        "activemodel.attributes.verification.email.recipient": "E-mail-cím",
        "activemodel.attributes.verification/letter.email": "E-mail-cím",
    },
    "activerecord.yml": {
        "attributes.email": "E-mail-cím",
        "activerecord.models.link.one": "Hivatkozás",
        "activerecord.attributes.budget/investment.feasibility_undecided": "Nincs meghatározva",
        "activerecord.attributes.user.email": "E-mail-cím",
        "activerecord.attributes.sdg/phase/kind.monitoring": "Nyomon követés",
        "activerecord.attributes.site_customization/content_block.locale": "Nyelvi beállítás",
        "activerecord.attributes.tenant.domain": "Domainnév",
        "activerecord.attributes.banner.target_url": "Hivatkozás",
        "activerecord.attributes.admin_notification.link": "Hivatkozás",
        "activerecord.attributes.widget/card.link_url": "Hivatkozás URL-je",
        "activerecord.attributes.link.url": "URL",
    },
    "admin.yml": {
        "admin.budget_investments.show.undefined": "Nincs meghatározva",
        "admin.budget_investments.edit.undefined": "Nincs meghatározva",
        "admin.comments.index.table_link": "Hivatkozás",
        "admin.dashboard.actions.index.default.email": "E-mail-cím",
        "admin.hidden_users.show.email": "E-mail-cím:",
        "admin.menu.geozones": "Földrajzi zónák",
        "admin.admin_notifications.show.link": "Hivatkozás",
        "admin.valuators.index.email": "E-mail-cím",
        "admin.valuators.show.email": "E-mail-cím",
        "admin.poll_officers.officer.email": "E-mail-cím",
        "admin.poll_officer_assignments.index.table_email": "E-mail-cím",
        "admin.poll_shifts.new.table_email": "E-mail-cím",
        "admin.organizations.index.email": "E-mail-cím",
        "admin.geozones.index.title": "Földrajzi zóna",
        "admin.users.columns.email": "E-mail-cím",
    },
    "general.yml": {
        "polls.show.stats.web": "ONLINE",
    },
    "management.yml": {
        "management.account_info.email_label": "E-mail-cím:",
    },
    "rails.yml": {
        "number.human.storage_units.units.byte.one": "bájt",
        "time.am": "de.",
        "time.pm": "du.",
    },
    "sdg.yml": {
        "sdg.goals.goal_2.title": "Az éhezés felszámolása",
        "sdg.goals.goal_2.description": "Az éhezés felszámolása.",
    },
    "seeds.yml": {
        "seeds.polls.recounting_poll": "Szavazatok újraszámlálása",
    },
    "settings.yml": {
        "settings.twitter_hashtag": "Twitter-hashtag",
        "settings.proposals.email_short_title": "E-mail",
        "settings.analytics_url": "Analitikai URL",
    },
    "social_share_button.yml": {
        "social_share_button.email": "E-mail",
    },
    "stats.yml": {
        "stats.polls.web_percentage": "%{percentage} online",
        "stats.polls.letter_percentage": "%{percentage} levélben",
    },
    "valuation.yml": {
        "valuation.budget_investments.show.undefined": "Nincs meghatározva",
    },
}


def load(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def flatten(value: Any, prefix: str = "") -> dict[str, Any]:
    output: dict[str, Any] = {}
    if isinstance(value, dict):
        for key, child in value.items():
            output.update(flatten(child, f"{prefix}.{key}" if prefix else str(key)))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            output.update(flatten(child, f"{prefix}[{index}]"))
    else:
        output[prefix] = value
    return output


def set_path(target: dict[str, Any], path: str, value: Any) -> None:
    current: Any = target
    parts: list[str | int] = []
    for match in re.finditer(r"([^\.\[\]]+)|\[(\d+)\]", path):
        parts.append(int(match.group(2)) if match.group(2) is not None else match.group(1))
    for index, part in enumerate(parts):
        if index == len(parts) - 1:
            current[part] = value
        else:
            next_is_list = isinstance(parts[index + 1], int)
            if part not in current:
                current[part] = [] if next_is_list else {}
            current = current[part]


def main() -> None:
    changes: list[tuple[str, str, str, str, str, str]] = []
    for filename, values in OVERRIDES.items():
        en_path = ROOT / "config/locales/en" / filename
        hu_path = ROOT / "config/locales/hu-HU" / filename
        english = flatten(load(en_path).get("en", {}))
        document = load(hu_path)
        hungarian = document.setdefault("hu", {})
        current = flatten(hungarian)
        for key, revised in values.items():
            if key not in english:
                raise KeyError(f"Unknown locale key: {filename}:{key}")
            previous = current.get(key, "")
            if previous != revised:
                set_path(hungarian, key, revised)
                changes.append((filename, key, previous, revised, english[key], "visible-label editorial revision"))
        hu_path.write_text(yaml.safe_dump(document, allow_unicode=True, sort_keys=False, width=120), encoding="utf-8")
    header = not CHANGELOG.exists()
    with CHANGELOG.open("a", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t")
        if header:
            writer.writerow(["file", "key", "previous_hungarian", "revised_hungarian", "english_source", "method"])
        writer.writerows(changes)
    print(f"Applied {len(changes)} visible-label corrections")


if __name__ == "__main__":
    main()
