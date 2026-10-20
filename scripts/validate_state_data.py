#!/usr/bin/env python3
"""Validate scanner/data/state_laws.json. Exit 1 on any problem."""

import json
import sys
from datetime import date
from pathlib import Path

PATH = Path(__file__).resolve().parents[1] / "scanner" / "data" / "state_laws.json"
DIMS = ["health_specificity", "private_right", "enforcement", "penalty_exposure", "tracker_coverage"]
STATUSES = {"in_effect", "enacted_not_effective", "pending", "none"}
EXPECTED = set("""AL AK AZ AR CA CO CT DE DC FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH
NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY""".split())
REQUIRED_WHEN_SCORED = ["law", "summary", "key_risk", "freshpaint_help"]


def main() -> int:
    data = json.loads(PATH.read_text(encoding="utf-8"))
    errors, warnings = [], []
    states = data.get("states", {})

    missing = EXPECTED - set(states)
    extra = set(states) - EXPECTED
    if missing:
        errors.append(f"missing states: {sorted(missing)}")
    if extra:
        errors.append(f"unknown state codes: {sorted(extra)}")

    for abbr, rec in states.items():
        if "name" not in rec:
            errors.append(f"{abbr}: missing name")
        if rec.get("status") not in STATUSES:
            errors.append(f"{abbr}: status must be one of {sorted(STATUSES)}")
        for d in DIMS:
            v = rec.get(d)
            if not isinstance(v, int) or not 0 <= v <= 3:
                errors.append(f"{abbr}: {d} must be an integer 0-3 (got {v!r})")
        scored = any(rec.get(d, 0) for d in DIMS)
        if scored:
            for f in REQUIRED_WHEN_SCORED:
                if not rec.get(f):
                    errors.append(f"{abbr}: scored state is missing '{f}'")
            if not rec.get("sources"):
                warnings.append(f"{abbr}: no sources listed")
        if rec.get("status") == "in_effect" and not rec.get("effective"):
            errors.append(f"{abbr}: in_effect but no effective date")

    reviewed = data.get("_meta", {}).get("last_reviewed")
    try:
        age = (date.today() - date.fromisoformat(reviewed)).days
        if age > 45:
            warnings.append(f"_meta.last_reviewed is {age} days old ({reviewed})")
    except (TypeError, ValueError):
        errors.append("_meta.last_reviewed must be an ISO date (YYYY-MM-DD)")

    for w in warnings:
        print(f"warning: {w}")
    for e in errors:
        print(f"ERROR: {e}")
    print(f"{len(states)} states checked: {len(errors)} errors, {len(warnings)} warnings")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
