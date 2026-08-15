#!/usr/bin/env python3
"""Verify the branch-owned production transport-security settings."""
from pathlib import Path
import sys

production = (Path(__file__).resolve().parents[1] / "config/environments/production.rb").read_text(encoding="utf-8")
required_fragments = {
    "SSL-terminating proxy is trusted": "config.assume_ssl = true",
    "HTTPS is enforced without a secret fallback": "config.force_ssl = true",
    "HSTS is configured": "hsts:",
    "HSTS applies to subdomains": "subdomains: true",
    "HSTS has a one-year lifetime": "expires: 1.year",
}

failures = [label for label, fragment in required_fragments.items() if fragment not in production]
if failures:
    print("Production hardening validation failed:", file=sys.stderr)
    for failure in failures:
        print(f"- Missing: {failure}", file=sys.stderr)
    raise SystemExit(1)

print("Production hardening source validation passed.")
