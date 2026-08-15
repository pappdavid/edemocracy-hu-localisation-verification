#!/usr/bin/env python3
"""Generate complete Hungarian locales from the canonical English YAML catalogue.

The script translates every string leaf through the approved sandbox language model,
validates key coverage plus protected tokens, and writes structurally identical `hu`
locale files. It keeps the reviewed eDemocracy-specific wording as a final override.
"""
from __future__ import annotations

import concurrent.futures
import json
import os
import re
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

import yaml
from openai import OpenAI

ROOT = Path(__file__).resolve().parents[1]
EN_DIR = ROOT / "config/locales/en"
HU_DIR = ROOT / "config/locales/hu-HU"
CURATED_OVERLAY = HU_DIR / "edemocracy_hu.yml"
STATE_DIR = ROOT / "artifacts/complete_hu_translation_state"
MODEL = os.environ.get("HU_TRANSLATION_MODEL", "gpt-5-mini")
BATCH_SIZE = int(os.environ.get("HU_TRANSLATION_BATCH_SIZE", "30"))
MAX_WORKERS = int(os.environ.get("HU_TRANSLATION_WORKERS", "3"))

PLACEHOLDER_RE = re.compile(r"%\{[^}]+\}|%<[^>]+>[^\s]*|%\d*\$?[a-zA-Z]")
TAG_RE = re.compile(r"</?[A-Za-z][^>]*>")
MARKDOWN_LINK_RE = re.compile(r"\[[^\]]*\]\([^)]*\)")
URL_RE = re.compile(r"https?://[^\s<]+")

GLOSSARY = """
Use this Hungarian civic-platform terminology consistently:
- proposal = javaslat; debate = vita; poll = szavazás; legislation = közös jogalkotás;
  participatory budgeting = közösségi költségvetés; support a proposal = javaslat támogatása.
- sign in = bejelentkezés; register = regisztráció; account = fiók; settings = beállítások;
  notification = értesítés; user = felhasználó; administrator = adminisztrátor.
- residence verification = lakóhely ellenőrzése; confirmation code = megerősítő kód;
  identity card = személyi igazolvány; passport = útlevél; address card = lakcímkártya.
- Do not promise that authorities will implement any successful proposal. Keep qualified,
  factual wording around accessibility and legal/policy matters.
""".strip()


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
    for token in re.findall(r"[^.\[\]]+|\[(\d+)\]", path):
        # regexp returns either the raw path token or the list index capture.
        if token.isdigit():
            parts.append(int(token))
        else:
            parts.append(token)
    # The expression above returns empty captures for raw names; use a robust scan instead.
    parts = []
    for match in re.finditer(r"([^.\[\]]+)|\[(\d+)\]", path):
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
        | set(MARKDOWN_LINK_RE.findall(value))
        | set(URL_RE.findall(value))
    )


def validate_translation(source: str, translated: str) -> None:
    if not isinstance(translated, str) or not translated.strip():
        raise ValueError("Translation is empty or not a string")
    missing = sorted(set(protected_tokens(source)) - set(protected_tokens(translated)))
    if missing:
        raise ValueError(f"Protected tokens missing: {missing}")


def state_path(filename: str, batch_index: int) -> Path:
    return STATE_DIR / filename / f"{batch_index:03d}.json"


def request_translation(filename: str, batch_index: int, items: list[dict[str, str]]) -> dict[str, str]:
    saved = state_path(filename, batch_index)
    if saved.exists():
        payload = json.loads(saved.read_text(encoding="utf-8"))
        return {entry["key"]: entry["value"] for entry in payload["items"]}

    client = OpenAI()
    request = {
        "filename": filename,
        "items": items,
    }
    schema = {
        "type": "object",
        "properties": {
            "items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "key": {"type": "string"},
                        "value": {"type": "string"},
                    },
                    "required": ["key", "value"],
                    "additionalProperties": False,
                },
            }
        },
        "required": ["items"],
        "additionalProperties": False,
    }
    prompt = f"""Translate every English value in this CONSUL 2.5.0 locale file to natural, professional Hungarian.

{GLOSSARY}

Rules:
1. Return exactly one translated value for every input key, with keys unchanged.
2. Preserve protected syntax exactly: Rails interpolation placeholders, format directives, HTML tags and attributes, Markdown links, URLs, escaped entities, and newline structure.
3. Translate all user-facing English. Keep only unavoidable proper names, acronyms, technical protocol names, and URLs unchanged.
4. Do not invent policy commitments, legal claims, or product functionality.
5. The output must be JSON matching the requested schema and contain no commentary.

Input:
{json.dumps(request, ensure_ascii=False)}"""
    last_error: Exception | None = None
    expected = {item["key"] for item in items}
    for attempt in range(1, 4):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert Hungarian software-localisation translator. Output valid JSON only."},
                    {"role": "user", "content": prompt},
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": {"name": "hungarian_locale_batch", "strict": True, "schema": schema},
                },
                max_completion_tokens=24000,
            )
            if not response.choices or response.choices[0].message.content is None:
                raise RuntimeError(f"Model returned no usable content: {response.model_dump_json()[:4000]}")
            content = response.choices[0].message.content
            parsed = json.loads(content)
            result = {entry["key"]: entry["value"] for entry in parsed["items"]}
            if set(result) != expected:
                raise ValueError(f"Expected {len(expected)} keys but got {len(result)}")
            for item in items:
                validate_translation(item["value"], result[item["key"]])
            saved.parent.mkdir(parents=True, exist_ok=True)
            saved.write_text(json.dumps(parsed, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            return result
        except Exception as error:  # Retry transient or schema/token failures.
            last_error = error
            time.sleep(attempt * 2)
    raise RuntimeError(f"Translation failed for {filename} batch {batch_index}: {last_error}")


def batches(items: list[dict[str, str]]) -> list[list[dict[str, str]]]:
    return [items[i:i + BATCH_SIZE] for i in range(0, len(items), BATCH_SIZE)]


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
        path = HU_DIR / "zz_hungarian_custom_overrides.yml"
        data: dict[str, Any] = {}
        for key, value in unresolved.items():
            set_path(data, key, value)
        path.write_text(yaml.safe_dump({"hu": data}, allow_unicode=True, sort_keys=False, width=120), encoding="utf-8")
    return overrides


def process_file(en_path: Path, overrides: dict[str, Any]) -> tuple[str, int]:
    english = root_mapping(read_yaml(en_path), "en")
    flat = flatten(english)
    strings = [{"key": key, "value": value} for key, value in flat.items() if isinstance(value, str)]
    translated: dict[str, Any] = {key: value for key, value in flat.items() if not isinstance(value, str)}
    file_batches = batches(strings)
    if file_batches:
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {
                executor.submit(request_translation, en_path.name, index, batch): index
                for index, batch in enumerate(file_batches)
            }
            for future in concurrent.futures.as_completed(futures):
                translated.update(future.result())
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
    print(json.dumps({"model": MODEL, "files": len(completed), "strings": sum(count for _, count in completed)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
