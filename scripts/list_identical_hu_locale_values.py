#!/usr/bin/env python3
"""List English/Hungarian locale leaves with exactly identical scalar values."""
from pathlib import Path
from typing import Any
import yaml

ROOT = Path(__file__).resolve().parents[1]
EN_DIR = ROOT / "config/locales/en"
HU_DIR = ROOT / "config/locales/hu-HU"


def load(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def flatten(value: Any, prefix: str = "") -> dict[str, Any]:
    result: dict[str, Any] = {}
    if isinstance(value, dict):
        for key, child in value.items():
            result.update(flatten(child, f"{prefix}.{key}" if prefix else str(key)))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            result.update(flatten(child, f"{prefix}[{index}]"))
    else:
        result[prefix] = value
    return result


for en_file in sorted(EN_DIR.glob("*.yml")):
    hu_file = HU_DIR / en_file.name
    english = flatten(load(en_file).get("en", {}))
    hungarian = flatten(load(hu_file).get("hu", {})) if hu_file.exists() else {}
    for key, value in english.items():
        if isinstance(value, str) and value and value == hungarian.get(key):
            print(f"{en_file.name}\t{key}\t{value}")
