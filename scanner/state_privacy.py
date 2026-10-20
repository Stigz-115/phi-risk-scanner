"""
State privacy exposure data + scoring logic.

State data lives in scanner/data/state_laws.json (single source of truth for
the State Privacy page AND the stakeholder decks). It is refreshed through the
monthly legislation-watch workflow — see docs/LEGISLATION_UPDATES.md.

Each state is scored across five risk dimensions (0-3 each).
"""

import json
from datetime import date
from pathlib import Path

_DATA_DIR = Path(__file__).parent / "data"
STATE_LAWS_PATH = _DATA_DIR / "state_laws.json"
WATCH_PATH = _DATA_DIR / "legislation_watch.json"

DIMENSIONS = ["health_specificity", "private_right", "enforcement", "penalty_exposure", "tracker_coverage"]

STATUS_LABELS = {
    "in_effect": "In effect",
    "enacted_not_effective": "Enacted - not yet effective",
    "pending": "Pending legislation",
    "none": "No active law",
}


def _load_state_file() -> dict:
    with open(STATE_LAWS_PATH, encoding="utf-8") as f:
        return json.load(f)


_RAW = _load_state_file()
META = _RAW.get("_meta", {})
ALL_STATES = _RAW["states"]
LAST_REVIEWED = META.get("last_reviewed", "unknown")


def _has_exposure(rec: dict) -> bool:
    return rec.get("status", "none") != "none" or any(rec.get(d, 0) for d in DIMENSIONS)


# States with a law, pending bill, or other scored exposure (e.g. wiretap litigation)
STATE_DATA = {abbr: rec for abbr, rec in ALL_STATES.items() if _has_exposure(rec)}

# States with no law (render on map as no-law)
NO_LAW_STATES = sorted(abbr for abbr in ALL_STATES if abbr not in STATE_DATA)


def days_since_review(today: date | None = None) -> int | None:
    try:
        reviewed = date.fromisoformat(LAST_REVIEWED)
    except ValueError:
        return None
    return ((today or date.today()) - reviewed).days


def load_watch() -> dict:
    """Latest output of scripts/check_legislation.py (empty dict if never run)."""
    try:
        with open(WATCH_PATH, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def laws_for_states(abbrs: list[str]) -> list[dict]:
    """Records for the given states, highest exposure first (used by the decks)."""
    out = []
    for abbr in abbrs:
        rec = ALL_STATES.get(abbr)
        if not rec:
            continue
        s = score_state(abbr)
        out.append({"abbr": abbr, **rec, **s,
                    "status_label": STATUS_LABELS.get(rec.get("status", "none"), "")})
    out.sort(key=lambda r: r["score"], reverse=True)
    return out


# ── Scoring ───────────────────────────────────────────────────────────────────
DIMENSION_WEIGHTS = {
    "health_specificity": 1.5,
    "private_right":      2.0,
    "enforcement":        1.5,
    "penalty_exposure":   1.5,
    "tracker_coverage":   1.5,
}

MAX_RAW = sum(3 * w for w in DIMENSION_WEIGHTS.values())  # 12.0


def score_state(abbr: str) -> dict:
    """Return numeric score (0–100) and tier for a state."""
    d = STATE_DATA.get(abbr)
    if d is None:
        return {"score": 0, "tier": "None", "tier_label": "No Active Law", "color": "#1E2533"}

    raw = sum(d.get(dim, 0) * w for dim, w in DIMENSION_WEIGHTS.items())
    if raw == 0:
        label = "Pending Bill - Watch" if d.get("status") == "pending" else "No Active Law"
        return {"score": 0, "tier": "None", "tier_label": label, "color": "#1E2533"}
    pct = int(round((raw / MAX_RAW) * 100))

    if pct >= 80:
        tier, label, color = "critical", "Critical", "#D42B4A"
    elif pct >= 55:
        tier, label, color = "high", "High", "#E8630A"
    elif pct >= 30:
        tier, label, color = "moderate", "Moderate", "#E8B80A"
    else:
        tier, label, color = "low", "Low", "#2A6049"

    return {"score": pct, "tier": tier, "tier_label": label, "color": color}


def score_all_states() -> dict:
    """Return {abbr: score_dict} for every known state."""
    result = {}
    for abbr in list(STATE_DATA.keys()) + NO_LAW_STATES:
        result[abbr] = score_state(abbr)
    return result


def aggregate_exposure(selected_states: list[str]) -> dict:
    """
    Given a list of state abbreviations, compute an aggregate exposure report.
    Returns: {total_score, tier, tier_label, breakdown, critical, high, moderate, low, none}
    """
    if not selected_states:
        return {"total_score": 0, "tier": "none", "tier_label": "No States Selected", "breakdown": []}

    breakdown = []
    for abbr in selected_states:
        s = score_state(abbr)
        d = ALL_STATES.get(abbr, {})
        breakdown.append({
            "abbr":       abbr,
            "name":       d.get("name", abbr),
            "law":        d.get("law", "No Active Law"),
            "effective":  d.get("effective", "—"),
            "score":      s["score"],
            "tier":       s["tier"],
            "tier_label": s["tier_label"],
            "color":      s["color"],
            "key_risk":   d.get("key_risk", "Federal HIPAA and FTC Act apply."),
            "freshpaint": d.get("freshpaint_help", "Freshpaint ensures baseline HIPAA compliance."),
            "private_right": d.get("private_right", 0),
            "health_specificity": d.get("health_specificity", 0),
            "tracker_coverage": d.get("tracker_coverage", 0),
            "status_label": STATUS_LABELS.get(d.get("status", "none"), "No active law"),
            "penalty":     d.get("penalty", "—"),
            "hipaa_exemption": d.get("hipaa_exemption", "—"),
        })

    breakdown.sort(key=lambda x: x["score"], reverse=True)

    scores = [b["score"] for b in breakdown]
    # Weighted aggregate: top-3 highest scores weighted more
    top = sorted(scores, reverse=True)[:3]
    rest = sorted(scores, reverse=True)[3:]
    agg = (sum(top) * 1.5 + sum(rest)) / max(1, (len(top) * 1.5 + len(rest)))
    agg = min(100, int(round(agg)))

    tiers = [b["tier"] for b in breakdown]
    if "critical" in tiers:
        tier, label = "critical", "Critical Exposure"
    elif "high" in tiers:
        tier, label = "high", "High Exposure"
    elif "moderate" in tiers:
        tier, label = "moderate", "Moderate Exposure"
    elif "low" in tiers:
        tier, label = "low", "Low Exposure"
    else:
        tier, label = "none", "Minimal Exposure"

    return {
        "total_score": agg,
        "tier":        tier,
        "tier_label":  label,
        "breakdown":   breakdown,
        "n_critical":  tiers.count("critical"),
        "n_high":      tiers.count("high"),
        "n_moderate":  tiers.count("moderate"),
        "n_low":       tiers.count("low"),
        "n_none":      tiers.count("None"),
        "n_private_right": sum(1 for b in breakdown if b["private_right"] >= 2),
        "top_risk":    breakdown[0] if breakdown else None,
    }
