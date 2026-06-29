"""
State privacy exposure data + scoring logic.
Each state is scored across five risk dimensions (0-3 each, max 15).
"""

# ── Scoring dimensions ────────────────────────────────────────────────────────
# health_specificity : 0=none, 1=general sensitive data, 2=health-specific, 3=digital health specific
# private_right      : 0=none, 1=limited, 2=moderate, 3=broad (incl. pixel/tracking)
# enforcement        : 0=none, 1=proposed/pending, 2=active AG, 3=active AG + settlements
# penalty_exposure   : 0=none, 1=<$10K/viol, 2=$10K-$50K/viol, 3=>$50K or uncapped
# tracker_coverage   : 0=none, 1=implied, 2=explicit pixels/cookies, 3=explicit + health data

STATE_DATA = {
    "WA": {
        "name": "Washington",
        "law": "My Health MY Data Act",
        "enacted": "2023",
        "effective": "Mar 2024",
        "health_specificity": 3,
        "private_right": 3,
        "enforcement": 3,
        "penalty_exposure": 3,
        "tracker_coverage": 3,
        "summary": "Broadest state health privacy law in the US. Covers any entity collecting consumer health data, not just HIPAA-covered entities. Explicitly covers geolocation and pixel tracking inferring health conditions. Broad private right of action.",
        "key_risk": "Private right of action; plaintiffs attorneys actively filing suits.",
        "freshpaint_help": "Freshpaint's proxy layer prevents health data from reaching ad pixels without BAA-covered routing.",
    },
    "TX": {
        "name": "Texas",
        "law": "Texas Health Information Privacy Act (TX THIPA)",
        "enacted": "2023",
        "effective": "Sep 2023",
        "health_specificity": 3,
        "private_right": 0,
        "enforcement": 2,
        "penalty_exposure": 2,
        "tracker_coverage": 2,
        "summary": "Extends health data protections beyond HIPAA-covered entities to any business collecting health data on Texans. AG enforcement; no private right of action currently.",
        "key_risk": "Applies to digital health apps, telehealth platforms, and hospital patient portals.",
        "freshpaint_help": "Freshpaint ensures health data is not shared with third-party trackers outside a BAA framework.",
    },
    "CA": {
        "name": "California",
        "law": "CCPA / CPRA",
        "enacted": "2018/2020",
        "effective": "Jan 2023 (CPRA)",
        "health_specificity": 2,
        "private_right": 2,
        "enforcement": 3,
        "penalty_exposure": 3,
        "tracker_coverage": 2,
        "summary": "Health information is sensitive personal data under CPRA. Requires opt-in consent for sale/sharing. CPPA actively enforcing. Healthcare entities face layered HIPAA + CCPA obligations.",
        "key_risk": "CPPA enforcement actions; $7,500/intentional violation. Class action exposure.",
        "freshpaint_help": "Freshpaint's consent layer and server-side routing help satisfy opt-in requirements before data reaches ad platforms.",
    },
    "CT": {
        "name": "Connecticut",
        "law": "CT Data Privacy Act (CTDPA)",
        "enacted": "2022",
        "effective": "Jul 2023",
        "health_specificity": 2,
        "private_right": 0,
        "enforcement": 2,
        "penalty_exposure": 2,
        "tracker_coverage": 2,
        "summary": "Health data is sensitive; processing requires opt-in consent. Covers controllers targeting CT residents. AG has exclusive enforcement authority.",
        "key_risk": "Opt-in requirement for health data; $5,000/willful violation.",
        "freshpaint_help": "Freshpaint's consent management ensures health data processing is gated on explicit user consent.",
    },
    "CO": {
        "name": "Colorado",
        "law": "Colorado Privacy Act (CPA)",
        "enacted": "2021",
        "effective": "Jul 2023",
        "health_specificity": 2,
        "private_right": 0,
        "enforcement": 2,
        "penalty_exposure": 2,
        "tracker_coverage": 2,
        "summary": "Health data classified as sensitive; opt-in consent required. AG and district attorneys can enforce. Rulemaking has clarified health data tracking obligations.",
        "key_risk": "Rulemaking specifically addressed health-inferred data from browsing behavior.",
        "freshpaint_help": "Freshpaint prevents health-inferring browsing data from being shared with third parties without consent.",
    },
    "VA": {
        "name": "Virginia",
        "law": "Virginia Consumer Data Protection Act (VCDPA)",
        "enacted": "2021",
        "effective": "Jan 2023",
        "health_specificity": 2,
        "private_right": 0,
        "enforcement": 2,
        "penalty_exposure": 2,
        "tracker_coverage": 1,
        "summary": "Health data is sensitive personal data; opt-in required. AG enforcement only. $7,500/intentional violation. Similar framework to GDPR in structure.",
        "key_risk": "Sensitive data processing opt-in; healthcare entities already navigating HIPAA face dual compliance.",
        "freshpaint_help": "Freshpaint provides auditable consent records and ensures sensitive health data routing compliance.",
    },
    "OR": {
        "name": "Oregon",
        "law": "Oregon Consumer Privacy Act (OCPA)",
        "enacted": "2023",
        "effective": "Jul 2024",
        "health_specificity": 2,
        "private_right": 0,
        "enforcement": 2,
        "penalty_exposure": 2,
        "tracker_coverage": 2,
        "summary": "Health data and data revealing health conditions are sensitive categories. Opt-in consent required. AG enforcement; $7,500/violation.",
        "key_risk": "Covers health condition inferences from digital behavior — directly relevant to healthcare ad tracking.",
        "freshpaint_help": "Freshpaint blocks health condition inferences from reaching ad pixels.",
    },
    "MT": {
        "name": "Montana",
        "law": "Montana Consumer Data Privacy Act (MCDPA)",
        "enacted": "2023",
        "effective": "Oct 2024",
        "health_specificity": 2,
        "private_right": 0,
        "enforcement": 1,
        "penalty_exposure": 2,
        "tracker_coverage": 1,
        "summary": "Health data is sensitive; opt-in required. Montana AG enforcement. Early enforcement phase — limited precedent so far.",
        "key_risk": "Opt-in consent for health data processing; evolving enforcement.",
        "freshpaint_help": "Freshpaint's consent-gated routing handles opt-in requirements automatically.",
    },
    "FL": {
        "name": "Florida",
        "law": "Florida Digital Bill of Rights (FDBR)",
        "enacted": "2023",
        "effective": "Jul 2024",
        "health_specificity": 2,
        "private_right": 0,
        "enforcement": 1,
        "penalty_exposure": 3,
        "tracker_coverage": 2,
        "summary": "Applies to large controllers (>$1B revenue, specific thresholds). Health data is sensitive. Penalties up to $50,000/violation. AG enforcement.",
        "key_risk": "High penalty exposure for large healthcare systems and national telehealth brands.",
        "freshpaint_help": "Freshpaint provides a compliant analytics layer for large health systems operating in Florida.",
    },
    "NY": {
        "name": "New York",
        "law": "NY SHIELD Act + Proposed Health Data Privacy Act",
        "enacted": "2019 (SHIELD); proposed 2023",
        "effective": "Current SHIELD; Health Act pending",
        "health_specificity": 2,
        "private_right": 1,
        "enforcement": 2,
        "penalty_exposure": 2,
        "tracker_coverage": 1,
        "summary": "NY SHIELD Act covers security obligations. A dedicated NY Health Data Privacy Act is advancing in legislature that would mirror WA's My Health MY Data Act with private right of action.",
        "key_risk": "Pending legislation may create broad private right of action — largest US healthcare market.",
        "freshpaint_help": "Proactive Freshpaint deployment positions NY-based health entities ahead of forthcoming legislation.",
    },
    "IL": {
        "name": "Illinois",
        "law": "Illinois BIPA + Proposed IHPPA",
        "enacted": "2008 (BIPA)",
        "effective": "Active",
        "health_specificity": 1,
        "private_right": 3,
        "enforcement": 3,
        "penalty_exposure": 3,
        "tracker_coverage": 1,
        "summary": "BIPA covers biometric data with aggressive private right of action. Separate health privacy act proposed. IL courts have awarded massive class-action settlements. High litigation state.",
        "key_risk": "BIPA class actions; plaintiffs attorneys very active. Proposed IHPPA would expand to digital health tracking.",
        "freshpaint_help": "Freshpaint avoids biometric data capture; server-side proxy reduces class action exposure.",
    },
    "MN": {
        "name": "Minnesota",
        "law": "Minnesota Consumer Data Privacy Act (MCDPA)",
        "enacted": "2024",
        "effective": "Jul 2025",
        "health_specificity": 2,
        "private_right": 0,
        "enforcement": 1,
        "penalty_exposure": 2,
        "tracker_coverage": 2,
        "summary": "One of the newer comprehensive state privacy laws. Health data is sensitive; opt-in required. AG enforcement. Still in early implementation phase.",
        "key_risk": "Opt-in consent for health data. Healthcare entities with MN patients must comply.",
        "freshpaint_help": "Freshpaint consent layer handles opt-in for sensitive health data processing.",
    },
    "NV": {
        "name": "Nevada",
        "law": "Nevada Privacy of Information Collected on Internet (SB 220 / SB 260)",
        "enacted": "2021",
        "effective": "Oct 2021",
        "health_specificity": 1,
        "private_right": 0,
        "enforcement": 1,
        "penalty_exposure": 1,
        "tracker_coverage": 1,
        "summary": "Opt-out right for sale of covered information. Health data has additional protections under SB 260. Limited scope compared to comprehensive frameworks.",
        "key_risk": "Opt-out mechanisms required; health data sale restrictions.",
        "freshpaint_help": "Freshpaint's data routing prevents third-party data sales outside consent.",
    },
    "UT": {
        "name": "Utah",
        "law": "Utah Consumer Privacy Act (UCPA)",
        "enacted": "2022",
        "effective": "Dec 2023",
        "health_specificity": 1,
        "private_right": 0,
        "enforcement": 1,
        "penalty_exposure": 1,
        "tracker_coverage": 1,
        "summary": "Controller/processor framework; sensitive data opt-out (not opt-in). Less protective than other state laws. Narrow exemptions.",
        "key_risk": "Opt-out required for health data sale/sharing. Narrower exposure for HIPAA-covered entities.",
        "freshpaint_help": "Freshpaint provides opt-out mechanisms compliant with UCPA requirements.",
    },
    "IN": {
        "name": "Indiana",
        "law": "Indiana Consumer Data Protection Act (INCDPA)",
        "enacted": "2023",
        "effective": "Jan 2026",
        "health_specificity": 1,
        "private_right": 0,
        "enforcement": 1,
        "penalty_exposure": 2,
        "tracker_coverage": 1,
        "summary": "Comprehensive privacy law with sensitive data protections. Health data opt-in required. AG enforcement with cure period. Takes effect January 2026.",
        "key_risk": "Effective Jan 2026 — healthcare entities should prepare now.",
        "freshpaint_help": "Freshpaint deployment ahead of effective date ensures Day 1 compliance.",
    },
    "TN": {
        "name": "Tennessee",
        "law": "Tennessee Information Protection Act (TIPA)",
        "enacted": "2023",
        "effective": "Jul 2025",
        "health_specificity": 1,
        "private_right": 0,
        "enforcement": 1,
        "penalty_exposure": 2,
        "tracker_coverage": 1,
        "summary": "Sensitive data (including health) requires opt-in. AG enforcement. Cure period. $15,000/violation.",
        "key_risk": "Health data opt-in; large healthcare systems operating in TN face dual HIPAA + TIPA obligations.",
        "freshpaint_help": "Freshpaint's consent layer satisfies TIPA opt-in requirements for health data.",
    },
    "IA": {
        "name": "Iowa",
        "law": "Iowa Consumer Data Protection Act (ICDPA)",
        "enacted": "2023",
        "effective": "Jan 2025",
        "health_specificity": 1,
        "private_right": 0,
        "enforcement": 1,
        "penalty_exposure": 1,
        "tracker_coverage": 1,
        "summary": "Sensitive data opt-out framework. Less stringent than other state laws. HIPAA-covered entities have broad exemptions.",
        "key_risk": "Limited exposure for HIPAA-covered entities; digital health apps face more risk.",
        "freshpaint_help": "Freshpaint's opt-out data routing satisfies Iowa requirements.",
    },
    "NJ": {
        "name": "New Jersey",
        "law": "New Jersey Data Privacy Act (NJDPA)",
        "enacted": "2024",
        "effective": "Jan 2025",
        "health_specificity": 2,
        "private_right": 0,
        "enforcement": 2,
        "penalty_exposure": 2,
        "tracker_coverage": 2,
        "summary": "Comprehensive privacy law effective Jan 2025. Health data is sensitive; opt-in required. AG enforcement. Covers large NJ healthcare market.",
        "key_risk": "NJ is a major healthcare state (pharma corridor); opt-in for health data now active.",
        "freshpaint_help": "Freshpaint ensures health data opt-in compliance for NJ-based and NJ-targeting healthcare entities.",
    },
    "MA": {
        "name": "Massachusetts",
        "law": "Proposed MA Privacy Act (pending)",
        "enacted": "Pending",
        "effective": "TBD",
        "health_specificity": 2,
        "private_right": 1,
        "enforcement": 1,
        "penalty_exposure": 2,
        "tracker_coverage": 1,
        "summary": "Comprehensive privacy legislation advancing in legislature. Strong health data protections expected given MA's healthcare industry concentration. Harvard-affiliated hospital systems under scrutiny.",
        "key_risk": "Major hospital systems (Mass General, Dana-Farber) already facing OCR investigations — state law would add layer.",
        "freshpaint_help": "Proactive Freshpaint deployment addresses current OCR scrutiny and upcoming state law.",
    },
    "AZ": {
        "name": "Arizona",
        "law": "No comprehensive law (monitoring)",
        "enacted": "—",
        "effective": "—",
        "health_specificity": 0,
        "private_right": 0,
        "enforcement": 0,
        "penalty_exposure": 0,
        "tracker_coverage": 0,
        "summary": "No state privacy law. HIPAA and FTC Act apply. Arizona legislature has introduced privacy bills that have not advanced.",
        "key_risk": "Federal OCR and FTC enforcement remain applicable.",
        "freshpaint_help": "Freshpaint ensures HIPAA compliance regardless of state-level gaps.",
    },
}

# States with no law (render on map as low risk)
NO_LAW_STATES = [
    "AK", "AL", "AR", "AZ", "GA", "HI", "ID", "KS", "KY", "LA",
    "ME", "MI", "MS", "MO", "NE", "NH", "NM", "NC", "ND", "OH",
    "OK", "PA", "RI", "SC", "SD", "VT", "WV", "WI", "WY", "DC",
    "MD",
]


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

    raw = sum(d[dim] * w for dim, w in DIMENSION_WEIGHTS.items())
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
        d = STATE_DATA.get(abbr, {})
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
