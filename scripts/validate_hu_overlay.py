#!/usr/bin/env python3
"""Validate the reviewed Hungarian localisation overlay before deployment."""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
OVERLAY = ROOT / "config/locales/hu-HU/edemocracy_hu.yml"
REGISTRATION_SUCCESS = ROOT / "app/views/users/registrations/success.html.erb"
VERIFY_ACCOUNT_COMPONENT = ROOT / "app/components/account/verify_account_component.html.erb"
PLACEHOLDER = re.compile(r"%\{[^}]+\}")

REQUIRED_KEYS = {
    "i18n.language.name": "Magyar",
    "helpers.select.prompt": "Kérjük, válasszon",
    "devise_views.users.registrations.success.verification_title": "Következő lépés: személyazonosság ellenőrzése",
    "devise_views.users.registrations.success.verification_instructions": None,
    "account.show.verify_my_account": "Fiókom ellenőrzése",
    "verification.step_1": "Lakóhely",
    "verification.step_2": "Megerősítő kód",
    "verification.step_3": "Végső ellenőrzés",
    "verification.residence.new.document_type.spanish_id": "Személyi igazolvány",
    "verification.residence.new.accept_terms_text": None,
    "layouts.footer.participation_text": None,
    "pages.help.proposals.description": None,
    "pages.accessibility.compatibility.description": None,
}


def lookup(data: dict[str, Any], dotted_key: str) -> Any:
    value: Any = data
    for part in dotted_key.split("."):
        if not isinstance(value, dict) or part not in value:
            raise KeyError(dotted_key)
        value = value[part]
    return value


def main() -> int:
    data = yaml.safe_load(OVERLAY.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or list(data) != ["hu"]:
        print("Overlay must be a YAML mapping with exactly one top-level `hu` key.", file=sys.stderr)
        return 1

    hungarian = data["hu"]
    failures: list[str] = []
    for dotted_key, expected in REQUIRED_KEYS.items():
        try:
            value = lookup(hungarian, dotted_key)
        except KeyError:
            failures.append(f"missing required key: {dotted_key}")
            continue
        if not isinstance(value, str) or not value.strip():
            failures.append(f"required key has no Hungarian text: {dotted_key}")
        elif expected and value != expected:
            failures.append(f"unexpected value for {dotted_key}: {value!r}")

    consent = lookup(hungarian, "verification.residence.new.accept_terms_text")
    if PLACEHOLDER.findall(consent) != ["%{terms_url}"]:
        failures.append("consent copy must retain exactly the %{terms_url} link placeholder")
    if "__MASZK_" in consent:
        failures.append("consent copy contains an unresolved mask placeholder")

    document_help = lookup(hungarian, "verification.residence.new.document_number_help_text")
    if "DNI" in document_help or "Személyi igazolvány" not in document_help:
        failures.append("document help must name the Hungarian identity card, not DNI")

    participation = lookup(hungarian, "layouts.footer.participation_text")
    if "azt a város" in participation:
        failures.append("footer tagline contains the recorded Hungarian case error")

    help_copy = lookup(hungarian, "pages.help.proposals.description")
    if "elfogadja és végrehajtja" in help_copy:
        failures.append("help copy makes the unsupported implementation promise")

    registration_template = REGISTRATION_SUCCESS.read_text(encoding="utf-8")
    if "devise_views.users.registrations.success.verification_title" not in registration_template:
        failures.append("registration-success page does not show the identity-verification next step")

    verify_account_component = VERIFY_ACCOUNT_COMPONENT.read_text(encoding="utf-8")
    if "verification_path" not in verify_account_component:
        failures.append("account verification component is not wired to the verification route")

    if failures:
        print("Hungarian overlay validation failed:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    print("Hungarian overlay validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
