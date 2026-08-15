#!/usr/bin/env python3
"""Generate a complete Hungarian locale catalogue with a local Argos Translate model.

This fallback is intentionally offline-capable: it translates every English string leaf,
protects Rails syntax byte-for-byte, checkpoints batches, and applies the reviewed
site-specific overlay last. It is used only when the approved sandbox LLM is unavailable.
"""
from __future__ import annotations

import concurrent.futures
import json
import os
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

import argostranslate.translate
import yaml

ROOT = Path(__file__).resolve().parents[1]
EN_DIR = ROOT / "config/locales/en"
HU_DIR = ROOT / "config/locales/hu-HU"
CURATED_OVERLAY = HU_DIR / "edemocracy_hu.yml"
STATE_DIR = ROOT / "artifacts/complete_hu_translation_state_offline"
BATCH_SIZE = int(os.environ.get("HU_TRANSLATION_BATCH_SIZE", "30"))
MAX_WORKERS = int(os.environ.get("HU_TRANSLATION_WORKERS", "3"))

PLACEHOLDER_RE = re.compile(r"%\{[^}]+\}|%<[^>]+>[^\s]*|%\d*\$?[a-zA-Z]")
TAG_RE = re.compile(r"</?[A-Za-z][^>]*>")
MARKDOWN_LINK_RE = re.compile(r"\[[^\]]*\]\([^)]*\)")
URL_RE = re.compile(r"https?://[^\s<>'\"]+")

# Fixed strings and source-aware adjustments correct common generic-MT mistakes for
# civic platform terminology without changing unrelated domain language.
POST_TRANSLATION_OVERRIDES: dict[str, dict[str, str]] = {
    "activerecord.yml": {
        "activerecord.models.milestone/status.other": "Mérföldkő állapotai",
        "activerecord.models.progress_bar.one": "Előrehaladási sáv",
        "activerecord.models.tag.one": "Címke",
        "activerecord.models.poll.one": "Szavazás",
        "activerecord.attributes.budget/investment.milestone_tag_list": "Mérföldkőcímkék",
        "activerecord.attributes.poll/question.poll_id": "Szavazás",
        "activerecord.attributes.poll/ballot_sheet.poll_id": "Szavazás",
        "activerecord.attributes.site_customization/page.slug": "Keresőbarát azonosító",
    },
    "admin.yml": {
        "admin.budget_investments.index.list.valuation_finished": "Értékelés lezárva",
        "admin.budget_investments.show.by": "Készítette",
        "admin.dashboard.actions.index.default.poster": "Plakát",
        "admin.administrators.index.id": "Adminisztrátori azonosító",
        "admin.stats.polls.title": "Szavazási statisztikák",
        "admin.stats.polls.table.poll_name": "Szavazás",
        "admin.site_customization.pages.page.slug": "Keresőbarát azonosító",
    },
    "budgets.yml": {
        "budgets.executions.filters.milestone_tag.label": "Mérföldkőcímke",
    },
    "devise_views.yml": {
        "devise_views.mailer.reset_password_instructions.hello": "Üdvözöljük",
        "devise_views.mailer.unlock_instructions.hello": "Üdvözöljük",
    },
    "general.yml": {
        # This key is requested by the poll index view but is absent from the upstream
        # English catalogue; defining it prevents the Rails translation-missing fallback.
        "polls.index.filter": "Szűrő",
        "form.banner": "Értesítési sáv",
        "dashboard.menu.poster": "Plakát",
        "dashboard.index.title": "Kiadás",
        "dashboard.poster.index.title": "Plakát előnézete",
        "polls.show.stats.web": "Web",
        "polls.show.stats.mail": "E-mail",
        "polls.show.stats.booth": "Szavazóhelyiség",
    },
    "officing.yml": {
        "officing.voters.new.table_poll": "Szavazás",
    },
    "pages.yml": {
        "pages.accessibility.keyboard_shortcuts.browser_table.browser_header": "Böngésző",
        "pages.accessibility.textsize.browser_settings_table.browser_header": "Böngésző",
    },
    "rails.yml": {
        "date.abbr_day_names[3]": "Sze",
        "date.abbr_day_names[4]": "Csü",
        "date.abbr_day_names[5]": "Pén",
        "date.abbr_month_names[2]": "febr.",
        "date.abbr_month_names[3]": "márc.",
        "date.abbr_month_names[4]": "ápr.",
        "date.abbr_month_names[6]": "jún.",
        "date.abbr_month_names[8]": "aug.",
        "date.abbr_month_names[11]": "nov.",
        "date.month_names[11]": "november",
        "number.human.decimal_units.units.quadrillion": "billiárd",
        "number.human.storage_units.units.byte.one": "bájt",
        "time.am": "de.",
        "time.pm": "du.",
    },
    "seeds.yml": {
        "seeds.budgets.groups.all_city": "Egész város",
    },
    "settings.yml": {
        "settings.twitter_hashtag": "Twitter-címke",
        "settings.proposals.poster_short_title": "Plakát",
        "settings.feature.saml_login": "SAML-bejelentkezés",
        "settings.llm.provider": "LLM-szolgáltató",
    },
    "stats.yml": {
        "stats.polls.web_percentage": "%{percentage} web",
    },
}

FIXED_TRANSLATIONS = {
    "Create an account": "Fiók létrehozása",
    "Create account": "Fiók létrehozása",
    "Your account has been created successfully.": "Fiókja sikeresen létrejött.",
    "Sign in": "Bejelentkezés",
    "Sign up": "Regisztráció",
    "Log in": "Bejelentkezés",
    "Log out": "Kijelentkezés",
    "Register": "Regisztráció",
    "Registration": "Regisztráció",
    "Settings": "Beállítások",
    "Notifications": "Értesítések",
    "My account": "Fiókom",
    "My profile": "Profilom",
    "Support": "Támogatás",
    "Support this proposal": "Javaslat támogatása",
    "Support %{proposal}": "%{proposal} támogatása",
    "Create proposal": "Javaslat létrehozása",
    "Participatory budgets": "Közösségi költségvetések",
    "Participatory budgeting": "Közösségi költségvetés",
    "Debates": "Viták",
    "Legislation": "Közös jogalkotás",
    "Polls": "Szavazások",
    "Verify your residence": "Lakóhely ellenőrzése",
    "Residence verification": "Lakóhely ellenőrzése",
    "Confirmation code": "Megerősítő kód",
    "Postal code": "Irányítószám",
    "Identity card": "Személyi igazolvány",
    "Address card": "Lakcímkártya",
}


def read_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Expected YAML mapping in {path}")
    return data


def root_mapping(data: dict[str, Any], root: str) -> dict[str, Any]:
    value = data.get(root)
    return value if isinstance(value, dict) else {}


def flatten(value: Any, prefix: str = "") -> dict[str, Any]:
    leaves: dict[str, Any] = {}
    if isinstance(value, dict):
        for key, child in value.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            leaves.update(flatten(child, path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            leaves.update(flatten(child, f"{prefix}[{index}]"))
    else:
        leaves[prefix] = value
    return leaves


def path_parts(path: str) -> list[str | int]:
    parts: list[str | int] = []
    for match in re.finditer(r"([^\.\[\]]+)|\[(\d+)\]", path):
        parts.append(int(match.group(2)) if match.group(2) is not None else match.group(1))
    return parts


def set_path(target: dict[str, Any], path: str, value: Any) -> None:
    current: Any = target
    parts = path_parts(path)
    for index, part in enumerate(parts):
        final = index == len(parts) - 1
        next_is_list = not final and isinstance(parts[index + 1], int)
        if final:
            if isinstance(current, list):
                while len(current) <= int(part):
                    current.append(None)
                current[int(part)] = value
            else:
                current[part] = value
            continue
        if isinstance(current, list):
            while len(current) <= int(part):
                current.append([] if next_is_list else {})
            current = current[int(part)]
        else:
            if part not in current:
                current[part] = [] if next_is_list else {}
            current = current[part]


def protected_tokens(value: str) -> list[str]:
    return sorted(
        set(PLACEHOLDER_RE.findall(value))
        | set(TAG_RE.findall(value))
        | set(URL_RE.findall(value)),
        key=len,
        reverse=True,
    )


def validate_translation(source: str, translated: str) -> None:
    if not isinstance(translated, str) or not translated.strip():
        raise ValueError("Translation is empty or not a string")
    missing = sorted(set(protected_tokens(source)) - set(protected_tokens(translated)))
    if missing:
        raise ValueError(f"Protected tokens missing: {missing}")


def state_path(filename: str, batch_index: int) -> Path:
    return STATE_DIR / filename / f"{batch_index:03d}.json"


def protected_spans(source: str) -> list[tuple[int, int, str]]:
    """Return non-overlapping protected syntax spans, preferring outer HTML tags."""
    matches: list[tuple[int, int, str]] = []
    for pattern in (TAG_RE, PLACEHOLDER_RE, URL_RE):
        matches.extend((match.start(), match.end(), match.group(0)) for match in pattern.finditer(source))
    selected: list[tuple[int, int, str]] = []
    for start, end, value in sorted(matches, key=lambda item: (item[0], -(item[1] - item[0]))):
        if selected and start < selected[-1][1]:
            continue
        selected.append((start, end, value))
    return selected


def translate_plain_segment(source: str) -> str:
    """Translate text while retaining its boundary whitespace verbatim."""
    leading = re.match(r"^\s*", source).group(0)
    trailing = re.search(r"\s*$", source).group(0)
    core_end = len(source) - len(trailing) if trailing else len(source)
    core = source[len(leading):core_end]
    return leading + (argostranslate.translate.translate(core, "en", "hu") if core else "") + trailing


def translate_structured_fragment(source: str) -> str:
    """Translate only natural-language segments, retaining protected syntax exactly."""
    pieces: list[str] = []
    cursor = 0
    for start, end, token in protected_spans(source):
        if cursor < start:
            pieces.append(translate_plain_segment(source[cursor:start]))
        pieces.append(token)
        cursor = end
    if cursor < len(source):
        pieces.append(translate_plain_segment(source[cursor:]))
    return "".join(pieces)


def translate_with_markdown_links(source: str) -> str:
    """Translate Markdown link labels while retaining their destination and syntax."""
    pieces: list[str] = []
    cursor = 0
    for match in MARKDOWN_LINK_RE.finditer(source):
        if cursor < match.start():
            pieces.append(translate_structured_fragment(source[cursor:match.start()]))
        label, target = match.group(0)[1:].split("](", 1)
        pieces.append(f"[{translate_structured_fragment(label)}]({target}")
        cursor = match.end()
    if cursor < len(source):
        pieces.append(translate_structured_fragment(source[cursor:]))
    return "".join(pieces)


def apply_civic_glossary(source: str, translated: str) -> str:
    if source in FIXED_TRANSLATIONS:
        return FIXED_TRANSLATIONS[source]
    lower = source.lower()
    # Argos often treats application accounts as financial accounts. This source-driven
    # normalization keeps the intended platform meaning while leaving budget/invoice text alone.
    if re.search(r"\baccount\b", source, flags=re.IGNORECASE):
        replacements = {
            "Számláját": "Fiókját", "számláját": "fiókját",
            "Számlája": "Fiókja", "számlája": "fiókja",
            "Számlájának": "Fiókjának", "számlájának": "fiókjának",
            "Számlához": "Fiókhoz", "számlához": "fiókhoz",
            "Számlát": "Fiókot", "számlát": "fiókot",
            "Számla": "Fiók", "számla": "fiók",
        }
        for before, after in replacements.items():
            translated = translated.replace(before, after)
    if "participatory budgeting" in lower:
        translated = re.sub(r"(?i)részvételi költségvet\w*", "közösségi költségvetés", translated)
    if "residence verification" in lower:
        translated = re.sub(r"(?i)lakóhelyi ellenőrzés", "lakóhely ellenőrzése", translated)
    return translated


def translate_value(source: str) -> str:
    if source == "":
        return ""
    if source in FIXED_TRANSLATIONS:
        return FIXED_TRANSLATIONS[source]
    translated = translate_with_markdown_links(source)
    translated = apply_civic_glossary(source, translated)
    try:
        validate_translation(source, translated)
    except ValueError as error:
        raise ValueError(f"{error}; source={source!r}; translated={translated!r}") from error
    return translated


def translate_batch(filename: str, batch_index: int, items: list[dict[str, str]]) -> dict[str, str]:
    saved = state_path(filename, batch_index)
    if saved.exists():
        payload = json.loads(saved.read_text(encoding="utf-8"))
        output = {entry["key"]: entry["value"] for entry in payload["items"]}
        if len(output) == len(items):
            return output
    output = {item["key"]: translate_value(item["value"]) for item in items}
    payload = {"backend": "argos-offline-en-hu", "items": [{"key": key, "value": value} for key, value in output.items()]}
    saved.parent.mkdir(parents=True, exist_ok=True)
    saved.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return output


def batches(items: list[dict[str, str]]) -> list[list[dict[str, str]]]:
    return [items[index:index + BATCH_SIZE] for index in range(0, len(items), BATCH_SIZE)]


def load_curated_overrides(owners: dict[str, str]) -> dict[str, dict[str, Any]]:
    if not CURATED_OVERLAY.exists():
        return {}
    curated = flatten(root_mapping(read_yaml(CURATED_OVERLAY), "hu"))
    overrides: dict[str, dict[str, Any]] = defaultdict(dict)
    unresolved: dict[str, Any] = {}
    for key, value in curated.items():
        if key in owners:
            overrides[owners[key]][key] = value
        else:
            unresolved[key] = value
    if unresolved:
        output: dict[str, Any] = {}
        for key, value in unresolved.items():
            set_path(output, key, value)
        (HU_DIR / "zz_hungarian_custom_overrides.yml").write_text(
            yaml.safe_dump({"hu": output}, allow_unicode=True, sort_keys=False, width=120), encoding="utf-8"
        )
    return overrides


def process_file(en_path: Path, overrides: dict[str, Any]) -> tuple[str, int]:
    english = root_mapping(read_yaml(en_path), "en")
    flat = flatten(english)
    strings = [{"key": key, "value": value} for key, value in flat.items() if isinstance(value, str)]
    translated: dict[str, Any] = {key: value for key, value in flat.items() if not isinstance(value, str)}
    file_batches = batches(strings)
    if file_batches:
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = [executor.submit(translate_batch, en_path.name, index, batch) for index, batch in enumerate(file_batches)]
            for future in concurrent.futures.as_completed(futures):
                translated.update(future.result())
    translated.update(POST_TRANSLATION_OVERRIDES.get(en_path.name, {}))
    translated.update(overrides)
    output: dict[str, Any] = {}
    for key, value in translated.items():
        set_path(output, key, value)
    destination = HU_DIR / en_path.name
    destination.write_text(yaml.safe_dump({"hu": output}, allow_unicode=True, sort_keys=False, width=120), encoding="utf-8")
    return en_path.name, len(strings)


def main() -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    sources = sorted(EN_DIR.glob("*.yml"))
    owners: dict[str, str] = {}
    for source in sources:
        for key in flatten(root_mapping(read_yaml(source), "en")):
            owners.setdefault(key, source.name)
    overrides = load_curated_overrides(owners)
    completed: list[tuple[str, int]] = []
    for source in sources:
        print(f"Translating {source.name}...", flush=True)
        completed.append(process_file(source, overrides.get(source.name, {})))
    print(json.dumps({"backend": "argos-offline-en-hu", "files": len(completed), "strings": sum(count for _, count in completed)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
