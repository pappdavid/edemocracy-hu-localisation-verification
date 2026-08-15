#!/usr/bin/env python3
"""Second-pass Hungarian localisation using a neural translation draft plus an audit log.

The script is deliberately file-selectable. It retains protected Rails/HTML/URL syntax,
checkpoints every translated leaf, applies the project’s reviewed Hungarian overlay last,
and writes a TSV row for every changed value. It is intended for editorial review, not for
blind production deployment.
"""
from __future__ import annotations

import csv
import html
import json
import os
import re
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

import requests
import yaml
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
EN_DIR = ROOT / "config/locales/en"
HU_DIR = ROOT / "config/locales/hu-HU"
CURATED_OVERLAY = HU_DIR / "edemocracy_hu.yml"
STATE_DIR = ROOT / "artifacts/editorial_google_translation_state"
CHANGELOG = ROOT / "docs/hungarian_localisation_editorial_changes.tsv"
REQUEST_DELAY = float(os.environ.get("HU_EDITORIAL_REQUEST_DELAY", "0.15"))
SELECTED = {name.strip() for name in os.environ.get("HU_EDITORIAL_FILES", "").split(",") if name.strip()}

PLACEHOLDER_RE = re.compile(r"%\{[^}]+\}|%<[^>]+>[^\s]*|%\d*\$?[a-zA-Z]")
TAG_RE = re.compile(r"</?[A-Za-z][^>]*>")
URL_RE = re.compile(r"https?://[^\s<>'\"]+")
MARKDOWN_TARGET_RE = re.compile(r"\]\(([^)]*)\)")

# Project terminology is normalized after the neural draft. Context-specific reviewed
# wording from edemocracy_hu.yml still wins over these general normalization rules.
TERM_REPLACEMENTS = (
    ("részvételi költségvetéseket", "közösségi költségvetéseket"),
    ("részvételi költségvetések", "közösségi költségvetések"),
    ("részvételi költségvetéssel", "közösségi költségvetéssel"),
    ("részvételi költségvetés", "közösségi költségvetés"),
    ("közvélemény-kutatások", "szavazások"),
    ("közvélemény-kutatás", "szavazás"),
)


def read_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Expected YAML mapping: {path}")
    return data


def flatten(value: Any, prefix: str = "") -> dict[str, Any]:
    leaves: dict[str, Any] = {}
    if isinstance(value, dict):
        for key, child in value.items():
            leaves.update(flatten(child, f"{prefix}.{key}" if prefix else str(key)))
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


def protected(source: str) -> dict[str, set[str]]:
    return {
        "placeholders": set(PLACEHOLDER_RE.findall(source)),
        "tags": set(TAG_RE.findall(source)),
        "urls": set(URL_RE.findall(source)),
        "markdown_targets": set(MARKDOWN_TARGET_RE.findall(source)),
    }


def validate(source: str, translated: str) -> None:
    if source and (not isinstance(translated, str) or not translated.strip()):
        raise ValueError("Translation is empty")
    source_tokens = protected(source)
    output_tokens = protected(translated)
    for kind, values in source_tokens.items():
        missing = values - output_tokens[kind]
        if missing:
            raise ValueError(f"Missing {kind}: {sorted(missing)}")


def normalize_terms(value: str) -> str:
    for before, after in TERM_REPLACEMENTS:
        value = re.sub(rf"(?i){re.escape(before)}", after, value)
    return value


def mask_protected(source: str) -> tuple[str, dict[str, str]]:
    tokens = sorted(
        set(PLACEHOLDER_RE.findall(source)) | set(TAG_RE.findall(source)) | set(URL_RE.findall(source)),
        key=len,
        reverse=True,
    )
    masked = source
    replacements: dict[str, str] = {}
    for index, token in enumerate(tokens):
        marker = f"[[EDM{index}]]"
        replacements[marker] = token
        masked = masked.replace(token, marker)
    return masked, replacements


def restore_protected(value: str, replacements: dict[str, str]) -> str:
    for marker, token in replacements.items():
        value = value.replace(marker, token)
    return value


def state_path(filename: str, key: str) -> Path:
    safe_key = re.sub(r"[^A-Za-z0-9_.-]+", "_", key)
    return STATE_DIR / filename / f"{safe_key}.json"


def google_draft(session: requests.Session, source: str) -> str:
    masked, replacements = mask_protected(source)
    for attempt in range(1, 4):
        try:
            response = session.get(
                "https://translate.google.com/m",
                params={"sl": "en", "tl": "hu", "q": masked},
                timeout=30,
                headers={"User-Agent": "Mozilla/5.0 (compatible; eDemocracy localisation editorial review)"},
            )
            response.raise_for_status()
            page = BeautifulSoup(response.text, "html.parser")
            result = page.select_one(".result-container")
            if result is None:
                raise RuntimeError("No translation result element")
            translated = html.unescape(result.get_text("", strip=True))
            translated = restore_protected(translated, replacements)
            if not translated:
                raise RuntimeError("Empty translation result")
            return normalize_terms(translated)
        except Exception as error:
            if attempt == 3:
                raise RuntimeError(f"Translation request failed: {error}") from error
            time.sleep(attempt * 2)
    raise AssertionError("unreachable")


def load_overrides(owners: dict[str, str]) -> dict[str, dict[str, Any]]:
    if not CURATED_OVERLAY.exists():
        return {}
    overlay = flatten(read_yaml(CURATED_OVERLAY).get("hu", {}))
    result: dict[str, dict[str, Any]] = defaultdict(dict)
    for key, value in overlay.items():
        if key in owners:
            result[owners[key]][key] = value
    return result


def translate_file(en_path: Path, overrides: dict[str, Any], changes: list[tuple[str, str, str, str, str]]) -> int:
    english_tree = read_yaml(en_path).get("en", {})
    existing_tree = read_yaml(HU_DIR / en_path.name).get("hu", {})
    english = flatten(english_tree)
    existing = flatten(existing_tree)
    output = {key: value for key, value in english.items() if not isinstance(value, str)}
    session = requests.Session()
    for key, source in english.items():
        if not isinstance(source, str):
            continue
        if source == "":
            revised = ""
        else:
            saved = state_path(en_path.name, key)
            if saved.exists():
                revised = json.loads(saved.read_text(encoding="utf-8"))["translation"]
            else:
                revised = google_draft(session, source)
                try:
                    validate(source, revised)
                    method = "neural_draft"
                except ValueError:
                    # Complex nested links can be rewritten by the public draft service.
                    # Preserve the already validated Hungarian value rather than risk syntax loss.
                    revised = str(existing.get(key, ""))
                    validate(source, revised)
                    method = "preserved_existing_for_complex_syntax"
                saved.parent.mkdir(parents=True, exist_ok=True)
                saved.write_text(json.dumps({"source": source, "translation": revised, "method": method}, ensure_ascii=False) + "\n", encoding="utf-8")
                time.sleep(REQUEST_DELAY)
        output[key] = revised
    output.update(overrides)
    result: dict[str, Any] = {}
    for key, value in output.items():
        set_path(result, key, value)
        previous = existing.get(key, "")
        if isinstance(value, str) and previous != value:
            changes.append((en_path.name, key, str(previous), value, str(english.get(key, ""))))
    (HU_DIR / en_path.name).write_text(yaml.safe_dump({"hu": result}, allow_unicode=True, sort_keys=False, width=120), encoding="utf-8")
    return sum(isinstance(value, str) for value in english.values())


def main() -> None:
    sources = sorted(EN_DIR.glob("*.yml"))
    if SELECTED:
        unknown = SELECTED - {source.name for source in sources}
        if unknown:
            raise ValueError(f"Unknown locale files: {sorted(unknown)}")
        sources = [source for source in sources if source.name in SELECTED]
    owners: dict[str, str] = {}
    for source in EN_DIR.glob("*.yml"):
        for key in flatten(read_yaml(source).get("en", {})):
            owners.setdefault(key, source.name)
    overrides = load_overrides(owners)
    changes: list[tuple[str, str, str, str, str]] = []
    total = 0
    for source in sources:
        print(f"Rewriting {source.name}...", flush=True)
        total += translate_file(source, overrides.get(source.name, {}), changes)
    CHANGELOG.parent.mkdir(parents=True, exist_ok=True)
    write_header = not CHANGELOG.exists()
    with CHANGELOG.open("a", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t")
        if write_header:
            writer.writerow(["file", "key", "previous_hungarian", "revised_hungarian", "english_source"])
        writer.writerows(changes)
    print(json.dumps({"files": len(sources), "string_leaves": total, "changed": len(changes), "changelog": str(CHANGELOG)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
