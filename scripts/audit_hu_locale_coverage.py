#!/usr/bin/env python3
"""Audit complete Hungarian locale coverage against the English source catalogue."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
EN_DIR = ROOT / "config/locales/en"
HU_DIR = ROOT / "config/locales/hu-HU"
OUT = ROOT / "artifacts/hu_locale_coverage_audit.json"


def load_locale(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Expected mapping at root of {path}")
    return data


def locale_root(data: dict[str, Any], preferred: str) -> dict[str, Any]:
    if preferred in data:
        value = data[preferred]
        return value if isinstance(value, dict) else {}
    # Locale keys may occasionally include symbol-like variants; accept the sole mapping root.
    if len(data) == 1:
        only = next(iter(data.values()))
        if isinstance(only, dict):
            return only
    raise ValueError(f"Could not locate locale root '{preferred}'")


def flatten(value: Any, prefix: str = "") -> dict[str, Any]:
    result: dict[str, Any] = {}
    if isinstance(value, dict):
        for key, child in value.items():
            key_path = f"{prefix}.{key}" if prefix else str(key)
            result.update(flatten(child, key_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            key_path = f"{prefix}[{index}]"
            result.update(flatten(child, key_path))
    else:
        result[prefix] = value
    return result


def normalise_text(value: Any) -> str | None:
    return value.strip() if isinstance(value, str) else None


def is_untranslated(en_value: Any, hu_value: Any) -> bool:
    en = normalise_text(en_value)
    hu = normalise_text(hu_value)
    if not en or not hu:
        return False
    # Expected technical tokens and proper names do not indicate an untranslated sentence.
    if en in {"SMS", "SDG", "CONSUL DEMOCRACY", "WAI", "WCAG", "Google", "Facebook", "Twitter", "X", "PDF", "CSV", "URL", "OK"}:
        return False
    return en.casefold() == hu.casefold()


def main() -> None:
    reports: list[dict[str, Any]] = []
    totals = {"english_leaves": 0, "hungarian_leaves": 0, "missing": 0, "untranslated": 0}

    for en_path in sorted(EN_DIR.glob("*.yml")):
        hu_path = HU_DIR / en_path.name
        en_flat = flatten(locale_root(load_locale(en_path), "en"))
        hu_flat: dict[str, Any] = {}
        if hu_path.exists():
            hu_data = load_locale(hu_path)
            try:
                hu_root = locale_root(hu_data, "hu-HU")
            except ValueError:
                hu_root = locale_root(hu_data, "hu")
            hu_flat = flatten(hu_root)

        missing = sorted(set(en_flat) - set(hu_flat))
        untranslated = sorted(key for key in set(en_flat) & set(hu_flat) if is_untranslated(en_flat[key], hu_flat[key]))
        report = {
            "file": en_path.name,
            "english_leaves": len(en_flat),
            "hungarian_leaves": len(hu_flat),
            "missing_keys": missing,
            "untranslated_identical_values": untranslated,
        }
        reports.append(report)
        totals["english_leaves"] += len(en_flat)
        totals["hungarian_leaves"] += len(hu_flat)
        totals["missing"] += len(missing)
        totals["untranslated"] += len(untranslated)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"totals": totals, "files": reports}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"totals": totals}, ensure_ascii=False))
    for report in reports:
        if report["missing_keys"] or report["untranslated_identical_values"]:
            print(f"{report['file']}: missing={len(report['missing_keys'])}; identical={len(report['untranslated_identical_values'])}")


if __name__ == "__main__":
    main()
