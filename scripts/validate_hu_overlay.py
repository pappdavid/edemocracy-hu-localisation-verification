#!/usr/bin/env python3
"""Validate the Hungarian localisation overlay against the CONSUL 2.5.0 source locale.

The checker distinguishes *reports* from *blocking regressions*. A partial Hungarian
locale is expected while remediation is ongoing, so missing non-critical keys are
reported by default and become blocking only with --strict-missing. Critical public
and screenshoted admin surfaces must not fall back to English or Spanish.
"""
from __future__ import annotations

import argparse
import re
import sys
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
LOCALES = ROOT / "config" / "locales"
ENGLISH_DIR = LOCALES / "en"
HUNGARIAN_DIR = LOCALES / "hu-HU"
REGISTRATION_SUCCESS = ROOT / "app" / "views" / "users" / "registrations" / "success.html.erb"
VERIFY_ACCOUNT_COMPONENT = ROOT / "app" / "components" / "account" / "verify_account_component.html.erb"

PLACEHOLDER = re.compile(r"%\{[^}]+\}")
HTML_TAG = re.compile(r"<\s*(/?)\s*([A-Za-z][\w:-]*)\b[^>]*>")
SPANISH_FRAGMENT = re.compile(
    r"\b(?:DNI|Ayuntamiento|Ciudad|debate ciudadano|propuesta ciudadana|empadronamiento)\b",
    re.IGNORECASE,
)
ENGLISH_SIGNAL = re.compile(
    r"\b(?:the|and|or|you|your|sign|register|email|password|debate|proposal|help|create|save|"
    r"document|type|local|census|language|terms|privacy|accessibility|search|start|forgotten)\b",
    re.IGNORECASE,
)
INFORMAL_FRAGMENT = re.compile(
    r"\b(?:te|téged|neked|veled|regisztrálj|kattints|válaszd|indíts|támogasd|add meg|"
    r"nézd meg|olvasd el)\b",
    re.IGNORECASE,
)

CRITICAL_PREFIXES = (
    "devise_views.menu.login_items.",
    "devise_views.passwords.",
    "devise_views.sessions.",
    "devise_views.shared.links.",
    "devise_views.users.registrations.new.",
    "layouts.header.",
    "layouts.footer.",
    "debates.",
    "proposals.",
    "pages.help.",
    "verification.",
    "admin.local_census_records.",
)

REQUIRED_KEYS = {
    "i18n.language.name": "Magyar",
    "devise_views.menu.login_items.login": "Bejelentkezés",
    "devise_views.menu.login_items.signup": "Regisztráció",
    "devise_views.sessions.new.title": "Bejelentkezés",
    "devise_views.users.registrations.new.title": "Regisztráció",
    "layouts.header.debates": "Viták",
    "layouts.header.proposals": "Javaslatok",
    "layouts.header.collaborative_legislation": "Közösségi jogalkotás",
    "layouts.footer.participation_text": None,
    "debates.index.section_header.title": "Viták",
    "debates.index.section_header.help": "Segítség a vitákhoz",
    "proposals.index.section_header.title": "Javaslatok",
    "proposals.index.section_header.help": "Segítség a javaslatokhoz",
    "pages.help.debates.description": None,
    "pages.help.proposals.description": None,
    "verification.residence.new.document_type.spanish_id": "Személyi igazolvány",
    "verification.residence.new.accept_terms_text": None,
    "admin.local_census_records.new.creating": "Új helyi névjegyzék-rekord létrehozása",
    "admin.local_census_records.index.document_type": "Okmány típusa",
}

FORBIDDEN_TERMS = {
    "language label `angol`": re.compile(r"^angol$", re.IGNORECASE),
    "Spanish identity-document label `DNI`": re.compile(r"\bDNI\b", re.IGNORECASE),
    "recorded footer typo `korányzat`": re.compile(r"korányzat", re.IGNORECASE),
    "recorded footer typo `hasznája`": re.compile(r"hasznája", re.IGNORECASE),
    "recorded footer case error `azt a város`": re.compile(r"azt a város(?:\b|[^t])", re.IGNORECASE),
    "unsupported automatic-implementation promise": re.compile(r"elfogadja és végrehajtja", re.IGNORECASE),
    "unreviewed proposal term `ajánlat`": re.compile(r"\bajánlat", re.IGNORECASE),
    "unreviewed collaborative-legislation label": re.compile(
        r"Együttműködési jogszabályok|Együttműködő jogalkotás", re.IGNORECASE
    ),
}


def load_locale_files(directory: Path, locale: str) -> dict[str, Any]:
    """Merge a locale directory in deterministic path order."""
    merged: dict[str, Any] = {}
    for path in sorted(directory.glob("*.yml")):
        document = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        if not isinstance(document, dict) or locale not in document:
            raise ValueError(f"{path.relative_to(ROOT)} must contain a top-level `{locale}` mapping")
        locale_data = document[locale]
        if locale_data is None:
            locale_data = {}
        if not isinstance(locale_data, dict):
            raise ValueError(f"{path.relative_to(ROOT)} has a non-mapping `{locale}` value")
        deep_merge(merged, locale_data)
    return merged


def deep_merge(destination: dict[str, Any], source: dict[str, Any]) -> None:
    for key, value in source.items():
        if isinstance(value, dict) and isinstance(destination.get(key), dict):
            deep_merge(destination[key], value)
        else:
            destination[key] = value


def flatten(value: Any, prefix: str = "") -> Iterator[tuple[str, Any]]:
    if isinstance(value, dict):
        for key, child in value.items():
            child_key = f"{prefix}.{key}" if prefix else str(key)
            yield from flatten(child, child_key)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from flatten(child, f"{prefix}[{index}]")
    else:
        yield prefix, value


def lookup(data: dict[str, Any], dotted_key: str) -> Any:
    value: Any = data
    for part in dotted_key.split("."):
        if not isinstance(value, dict) or part not in value:
            raise KeyError(dotted_key)
        value = value[part]
    return value


def tags(value: str) -> list[tuple[str, str]]:
    return [(closing, name.lower()) for closing, name in HTML_TAG.findall(value)]


def is_critical(key: str) -> bool:
    return key.startswith(CRITICAL_PREFIXES)


def report(title: str, findings: list[str], limit: int = 24) -> None:
    print(f"{title}: {len(findings)}")
    for finding in findings[:limit]:
        print(f"  - {finding}")
    if len(findings) > limit:
        print(f"  - … {len(findings) - limit} additional findings omitted from console output")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--strict-missing",
        action="store_true",
        help="treat every key absent from the Hungarian locale as a validation failure",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        english = load_locale_files(ENGLISH_DIR, "en")
        hungarian = load_locale_files(HUNGARIAN_DIR, "hu")
    except (OSError, ValueError, yaml.YAMLError) as error:
        print(f"Hungarian localisation validation could not load locale YAML: {error}", file=sys.stderr)
        return 1

    en_flat = dict(flatten(english))
    hu_flat = dict(flatten(hungarian))
    missing_keys = sorted(key for key in en_flat if key not in hu_flat)
    source_fallbacks: list[str] = []
    english_on_critical: list[str] = []
    placeholder_mismatches: list[str] = []
    html_mismatches: list[str] = []
    spanish_fragments: list[str] = []
    terminology_violations: list[str] = []
    formality_violations: list[str] = []

    failures: list[str] = []
    for dotted_key, expected in REQUIRED_KEYS.items():
        try:
            value = lookup(hungarian, dotted_key)
        except KeyError:
            failures.append(f"missing required key: {dotted_key}")
            continue
        if not isinstance(value, str) or not value.strip():
            failures.append(f"required key has no Hungarian text: {dotted_key}")
        elif expected is not None and value != expected:
            failures.append(f"unexpected value for {dotted_key}: {value!r}")

    for key in sorted(set(en_flat).intersection(hu_flat)):
        source = en_flat[key]
        translated = hu_flat[key]
        if not isinstance(source, str) or not isinstance(translated, str):
            continue
        if source.strip() == translated.strip() and source.strip():
            source_fallbacks.append(key)
            if is_critical(key) and ENGLISH_SIGNAL.search(translated):
                english_on_critical.append(f"{key}: {translated!r}")
        if sorted(PLACEHOLDER.findall(source)) != sorted(PLACEHOLDER.findall(translated)):
            placeholder_mismatches.append(
                f"{key}: source={PLACEHOLDER.findall(source)!r} hu={PLACEHOLDER.findall(translated)!r}"
            )
        if tags(source) != tags(translated):
            html_mismatches.append(f"{key}: source={tags(source)!r} hu={tags(translated)!r}")

    for key, value in sorted(hu_flat.items()):
        if not isinstance(value, str):
            continue
        if SPANISH_FRAGMENT.search(value):
            spanish_fragments.append(f"{key}: {value!r}")
        for name, pattern in FORBIDDEN_TERMS.items():
            if pattern.search(value):
                terminology_violations.append(f"{name} at {key}: {value!r}")
        if is_critical(key) and INFORMAL_FRAGMENT.search(value):
            formality_violations.append(f"{key}: {value!r}")

    try:
        consent = lookup(hungarian, "verification.residence.new.accept_terms_text")
    except KeyError:
        consent = ""
    if not isinstance(consent, str) or PLACEHOLDER.findall(consent) != ["%{terms_url}"]:
        failures.append("consent copy must retain exactly the %{terms_url} link placeholder")
    if isinstance(consent, str) and "__MASZK_" in consent:
        failures.append("consent copy contains an unresolved mask placeholder")

    document_help = lookup(hungarian, "verification.residence.new.document_number_help_text")
    if not isinstance(document_help, str) or "DNI" in document_help or "Személyi igazolvány" not in document_help:
        failures.append("document help must name the Hungarian identity card, not DNI")

    registration_template = REGISTRATION_SUCCESS.read_text(encoding="utf-8")
    if "devise_views.users.registrations.success.verification_title" not in registration_template:
        failures.append("registration-success page does not show the identity-verification next step")
    verify_account_component = VERIFY_ACCOUNT_COMPONENT.read_text(encoding="utf-8")
    if "verification_path" not in verify_account_component:
        failures.append("account verification component is not wired to the verification route")

    if placeholder_mismatches:
        failures.append("interpolation placeholder mismatch found")
    if html_mismatches:
        failures.append("HTML/tag mismatch found")
    if spanish_fragments:
        failures.append("suspicious Spanish fragment found")
    if terminology_violations:
        failures.append("Hungarian terminology violation found")
    if formality_violations:
        failures.append("informal second-person wording found on a critical surface")
    if english_on_critical:
        failures.append("English source fallback found on a critical launch surface")
    if args.strict_missing and missing_keys:
        failures.append("missing Hungarian keys found while --strict-missing is enabled")

    print("CONSUL baseline: 2.5.0")
    print(f"English leaf keys: {len(en_flat)}")
    print(f"Hungarian leaf keys: {len(hu_flat)}")
    report("Missing keys against CONSUL 2.5.0", missing_keys)
    report("Exact source-language fallbacks", source_fallbacks)
    report("Suspicious English on critical launch surfaces", english_on_critical)
    report("Suspicious Spanish fragments", spanish_fragments)
    report("Interpolation placeholder mismatches", placeholder_mismatches)
    report("HTML/tag mismatches", html_mismatches)
    report("Terminology violations", terminology_violations)
    report("Mechanically detected informal wording", formality_violations)

    if failures:
        print("Hungarian localisation validation failed:", file=sys.stderr)
        for failure in sorted(set(failures)):
            print(f"- {failure}", file=sys.stderr)
        return 1

    print("Hungarian localisation validation passed: no blocking regression was found.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
