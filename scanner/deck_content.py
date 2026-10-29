"""
Format-neutral content model for the stakeholder decks.

build_briefs(data) returns one Brief per persona. Each brief is a list of
sections made of typed blocks; scanner/deck_pdf.py and scanner/deck_pptx.py
render the same model, so PDF and PowerPoint never drift apart.

Block types (tuples):
    ("text",    str)
    ("bullets", [str, ...])
    ("kv",      [(label, value), ...])
    ("stats",   [(value, label, tone), ...])      tone: bad | warn | good | accent
    ("table",   {"cols": [...], "widths": [...], "rows": [[...], ...]})
    ("callout", str)
    ("flow",    [str, ...])                        simple vertical architecture flow

Facts come from scanner/regulatory.py (federal) and scanner/state_privacy.py
(states); edit those, not this file, when the law changes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from scanner import regulatory as reg
from scanner.state_privacy import laws_for_states

# ── Personas ──────────────────────────────────────────────────────────────────
PERSONAS = {
    "exec": {
        "title": "CEO / Executive Sponsor",
        "short": "EXECUTIVE",
        "accent": (0, 200, 150),
        "focus": "Executive Summary",
        "headline": ("Keep marketing performance.", "Remove the privacy liability."),
        "blurb": "One-page case: exposure, cost of inaction, and what each stakeholder gets",
    },
    "cmo": {
        "title": "Chief Marketing Officer",
        "short": "CMO",
        "accent": (0, 170, 130),
        "focus": "Marketing Performance & Analytics",
        "headline": ("Keep full marketing visibility.", "Eliminate HIPAA risk."),
        "blurb": "ROAS degradation, attribution loss, remarketing, trackers on your site",
    },
    "cfo": {
        "title": "Chief Financial Officer",
        "short": "CFO",
        "accent": (232, 99, 10),
        "focus": "Financial Risk & ROI",
        "headline": ("Quantify the liability.", "Justify the investment."),
        "blurb": "Penalty exposure, settlements, cost of going dark, ROI and payback",
    },
    "gc": {
        "title": "General Counsel / Chief Compliance Officer",
        "short": "GC / CCO",
        "accent": (212, 43, 74),
        "focus": "Legal & Regulatory Compliance",
        "headline": ("Build a defensible", "compliance position."),
        "blurb": "Federal status after AHA v. Becerra, your state laws, enforcement record",
    },
    "privacy": {
        "title": "Privacy Officer / CISO",
        "short": "PRIVACY / SECURITY",
        "accent": (140, 90, 230),
        "focus": "Risk Assessment, Vendors & Audit Readiness",
        "headline": ("Close the tracking-vendor gap", "in your risk analysis."),
        "blurb": "Vendor/BAA inventory, controls checklist, state obligations, audit evidence",
    },
    "cto": {
        "title": "CTO / VP Engineering",
        "short": "CTO / IT",
        "accent": (26, 139, 255),
        "focus": "Technical Implementation & Security",
        "headline": ("One integration.", "No new infrastructure."),
        "blurb": "Architecture, implementation plan, tags to replace, security posture",
    },
}
PERSONA_ORDER = ["exec", "cmo", "cfo", "gc", "privacy", "cto"]

TONES = {
    "bad":    (200, 40, 60),
    "warn":   (215, 110, 20),
    "good":   (0, 165, 125),
    "accent": None,           # use persona accent
}

PHARMA = "Pharma / Life Sciences"

ORG_PROFILES = {
    "Digital Health / DTC":       {"roas_mult": 1.30, "attr_mult": 1.20, "label": "high pixel dependency"},
    "Telehealth":                 {"roas_mult": 1.35, "attr_mult": 1.25, "label": "high pixel dependency"},
    "Specialty Practice / Group": {"roas_mult": 1.10, "attr_mult": 1.05, "label": "medium pixel dependency"},
    "Hospital / Health System":   {"roas_mult": 0.90, "attr_mult": 1.10, "label": "lower pixel dependency"},
    "Payer / Insurance":          {"roas_mult": 1.05, "attr_mult": 1.30, "label": "attribution-heavy"},
    # Branded DTC: the conversion (a filled Rx) happens offline, so attribution
    # matters more than bidding signals, which platform health-ad rules already limit.
    PHARMA:                       {"roas_mult": 1.00, "attr_mult": 1.35, "label": "attribution-heavy, offline Rx conversion"},
}

# Pharma brands are usually not HIPAA covered entities; these replace HIPAA framing.
PHARMA_PERSONA_OVERRIDES = {
    "cmo":     {"headline": ("Keep full marketing visibility.", "Cut health-data privacy risk.")},
    "gc":      {"blurb": "FTC Section 5 and HBNR, your state health-data laws, enforcement record"},
    "privacy": {"headline": ("Close the tracking-vendor gap", "in your health-data program."),
                "blurb": "Vendor inventory, consent controls, state obligations, audit evidence"},
}

# Default model inputs. Verticals listed in ORG_BASELINES override some of them.
DEFAULT_BASELINE = {
    "monthly_spend":       50_000,
    "google_pct":          40,
    "meta_pct":            30,
    "remarketing_pct":     25,
    "patient_ltv":         2_500,
    "cpl":                 250,
    "cpl_degradation_pct": 40,
    "lead_to_patient_pct": 20,
    "roas_deg_pct":        20,
    "attr_waste_pct":      15,
    "remarketing_lift":    200,
    "freshpaint_cost":     40_000,
    "freshpaint_cost_min": 15_000,
    "freshpaint_cost_max": 200_000,
}

# Directional benchmarks for a branded pharma DTC program.
ORG_BASELINES = {
    PHARMA: {
        "monthly_spend":       250_000,  # per-brand digital DTC budget
        "google_pct":          35,       # branded + unbranded search
        "meta_pct":            20,       # rest goes to programmatic, endemic health sites, CTV
        "remarketing_pct":     10,       # Google and Meta restrict health-condition remarketing
        "patient_ltv":         6_000,    # annual net revenue per persistent patient (specialty runs far higher)
        "cpl":                 150,      # copay card / savings program enrollment
        "lead_to_patient_pct": 30,       # enrollment to first fill
        "attr_waste_pct":      20,       # Rx conversion happens offline, hard to tie back to media
        "remarketing_lift":    150,
        "freshpaint_cost":     200_000,  # pharma pricing floor
        "freshpaint_cost_min": 200_000,
        "freshpaint_cost_max": 500_000,
    },
}


def org_baseline(org_type: str) -> dict:
    return {**DEFAULT_BASELINE, **ORG_BASELINES.get(org_type, {})}


@dataclass
class Section:
    title: str
    blocks: list = field(default_factory=list)


@dataclass
class Brief:
    key: str
    persona: dict
    sections: list


# ── Helpers ───────────────────────────────────────────────────────────────────
def calc_roi(monthly_spend: float, org_type: str, freshpaint_cost: float = 40_000) -> dict:
    p = ORG_PROFILES.get(org_type, ORG_PROFILES["Hospital / Health System"])
    b = org_baseline(org_type)
    ann = monthly_spend * 12
    pixel_fraction = (b["google_pct"] + b["meta_pct"]) / 100
    lift = b["remarketing_lift"] / 100
    roas = ann * pixel_fraction * (b["roas_deg_pct"] / 100) * p["roas_mult"]
    attr = ann * (b["attr_waste_pct"] / 100) * p["attr_mult"]
    rmkt = ann * (b["remarketing_pct"] / 100) * lift / (1 + lift)
    total = roas + attr + rmkt
    return {
        "annual_spend": ann,
        "roas_loss": roas,
        "attr_loss": attr,
        "rmkt_loss": rmkt,
        "total": total,
        "roi": total / freshpaint_cost if freshpaint_cost else 0,
        "payback": freshpaint_cost / (total / 12) if total else 0,
        "freshpaint_cost": freshpaint_cost,
    }


def money(v: float) -> str:
    if abs(v) >= 1_000_000:
        return f"${v / 1_000_000:.1f}M"
    if abs(v) >= 10_000:
        return f"${v / 1_000:.0f}K"
    return f"${v:,.0f}"


def payback_str(months: float) -> str:
    if months < 1:
        return f"{months * 30:.0f} days"
    return f"{months:.1f} months" if months < 12 else f"{months / 12:.1f} years"


def summarize_scan(result) -> dict | None:
    """Convert a scanner.scanner.ScanResult into the plain dict the decks use."""
    if result is None:
        return None
    if getattr(result, "error", None):
        return {"url": result.url, "error": result.error, "trackers": []}
    trackers = [{
        "name": f.name, "company": f.company, "risk": f.risk_level,
        "baa": bool(f.baa_available),
    } for f in result.findings]
    order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    trackers.sort(key=lambda t: order.get(t["risk"], 9))
    return {
        "url": result.url,
        "when": result.scan_timestamp,
        "overall": result.overall_risk,
        "trackers": trackers,
        "n_no_baa": sum(1 for t in trackers if not t["baa"]),
        "n_high": sum(1 for t in trackers if t["risk"] in ("critical", "high")),
    }


def _scan_ok(scan) -> bool:
    return bool(scan) and not scan.get("error")


def _tracker_table(scan: dict, limit: int = 10) -> tuple:
    rows = [[t["name"], t["company"], "Yes" if t["baa"] else "No", t["risk"].title()]
            for t in scan["trackers"][:limit]]
    return ("table", {"cols": ["Tracker found", "Vendor", "BAA available", "Risk"],
                      "widths": [34, 30, 16, 20], "rows": rows})


def _state_context(states: list[str]) -> dict:
    laws = laws_for_states(states)
    in_effect = [l for l in laws if l.get("status") == "in_effect"]
    return {
        "laws": laws,
        "in_effect": in_effect,
        "coming": [l for l in laws if l.get("status") == "enacted_not_effective"],
        "pending": [l for l in laws if l.get("status") == "pending" and l["score"] > 0],
        "sueable": [l for l in laws if l.get("private_right", 0) >= 2],
        "top": laws[0] if laws and laws[0]["score"] > 0 else None,
    }


# ── Persona builders ──────────────────────────────────────────────────────────
def _exec(d: dict) -> list:
    m, co, scan, sc, ph = d["metrics"], d["company"], d.get("scan"), d["state_ctx"], d["pharma"]
    sections = []

    if ph and _scan_ok(scan) and scan["trackers"]:
        situation = (
            f"A scan of {scan['url']} found {len(scan['trackers'])} third-party tracking "
            "technologies. Each one can send visitor data from condition, savings-program and "
            "prescription pages to an ad or analytics platform."
        )
    elif _scan_ok(scan) and scan["trackers"]:
        situation = (
            f"A scan of {scan['url']} found {len(scan['trackers'])} third-party tracking "
            f"technologies, {scan['n_no_baa']} from vendors that do not sign a BAA. "
            f"Each one can transmit visitor data from health-related pages to an ad or analytics platform."
        )
    elif _scan_ok(scan):
        situation = (
            f"A static scan of {scan['url']} did not detect common third-party pixels. Tags loaded "
            "through a tag manager or after page load can still send health data, so a full audit is recommended."
        )
    elif ph:
        situation = (
            f"Like most pharma brands, {co} relies on ad and analytics tags to reach patients and drive "
            "savings-program enrollment. The same tags can send condition and prescription interest to "
            "Meta, Google and others."
        )
    else:
        situation = (
            f"Like most healthcare organizations, {co} relies on ad and analytics tags to grow patient "
            "volume. The same tags can send health-related browsing data to Meta, Google and others."
        )
    sections.append(Section("The situation", [
        ("text", situation),
        ("text", "Removing the tags makes the risk go away, but it also blinds marketing. "
                 "Freshpaint removes the risk without the blind spot."),
    ]))

    stats = [(money(m["total"]) + "/yr", "Cost of going dark", "bad")]
    if sc["top"]:
        stats.append((f"{sc['top']['score']}/100", f"Top state exposure ({sc['top']['abbr']})", "warn"))
    stats += [
        (reg.LARGEST_PIXEL_SETTLEMENT[0], "Largest pixel settlement", "bad"),
        (f"{m['roi']:.1f}x", "ROI on Freshpaint", "good"),
    ]
    sections.append(Section("At a glance", [("stats", stats)]))

    why = [
        "Federal: HIPAA rarely covers a pharma brand's consumer sites, so the FTC enforces instead: "
        f"Section 5 and the Health Breach Notification Rule, up to ${reg.FTC_CIVIL_PENALTY_MAX:,} per violation "
        "(GoodRx, BetterHelp, Hims & Hers)." if ph else
        "Federal: the FTC and state AGs now pursue pixels on public pages (FTC v. Hims & Hers, 2026), "
        "and OCR's guidance still covers patient portals and scheduling.",
        f"Litigation: healthcare pixel class actions keep settling, led by Kaiser Permanente at "
        f"{reg.LARGEST_PIXEL_SETTLEMENT[0]}.",
    ]
    if sc["laws"]:
        why.insert(1, (
            f"States: {len(sc['in_effect'])} of the {len(sc['laws'])} states you serve have privacy laws in effect"
            + (f", {len(sc['sueable'])} with a private right to sue" if sc["sueable"] else "")
            + (f", and {len(sc['coming'])} more take effect soon" if sc["coming"] else "") + "."
        ))
    sections.append(Section("Why now", [("bullets", why)]))

    sections.append(Section("What each stakeholder gets", [("kv", [
        ("Marketing (CMO)", "Conversion signals keep flowing to Google, Meta and analytics; no lost optimization."),
        ("Finance (CFO)",   f"{money(m['total'])}/yr of marketing efficiency protected; payback in {payback_str(m['payback'])}."),
        ("Legal (GC)",      "Health data is stripped before any vendor receives it, and consent is enforced."
                            if ph else "PHI is stripped before any vendor receives it, under a signed BAA."),
        ("Privacy / CISO",  ("One governed vendor" if ph else "One BAA-covered vendor")
                            + " replaces many; consent and audit evidence in one place."),
        ("Engineering",     "One script replaces individual pixels; no new infrastructure to run."),
    ])]))
    sections.append(Section("Recommended next step", [("callout",
        f"Agree on a 30-minute working session with marketing, legal and IT to review {co}'s tracker "
        "inventory and a deployment plan. Freshpaint brings the scan results and "
        + ("draft data processing terms." if ph else "a draft BAA."))]))
    return sections


def _cmo(d: dict) -> list:
    m, co, scan, ph = d["metrics"], d["company"], d.get("scan"), d["pharma"]
    data = "health data" if ph else "PHI"
    sections = [
        Section("The marketing performance risk", [
            ("text", ("Pharma brands" if ph else "Healthcare organizations") + " that remove tracking pixels without replacing them lose three "
                     "compounding revenue levers at once: ad algorithms stop learning, budget flows to the wrong "
                     "channels, and remarketing audiences expire."),
            ("stats", [
                (money(m["roas_loss"]) + "/yr", "ROAS signal degradation", "bad"),
                (money(m["attr_loss"]) + "/yr", "Attribution blindness", "warn"),
                (money(m["rmkt_loss"]) + "/yr", "Remarketing audience loss", "warn"),
            ]),
        ]),
        Section("What going dark looks like", [("bullets", [
            "Smart Bidding and Advantage+ need steady conversion volume; without it they fall back to broad "
            "targeting and acquisition costs rise.",
            "Last-click replaces multi-touch, so budget drifts to brand search and away from "
            + ("unbranded condition and savings-program campaigns." if ph else "service-line campaigns."),
            "Remarketing lists expire within 30-90 days, and lookalike seeds stop refreshing.",
            "A/B tests on landing pages and creative lose statistical validity.",
        ])]),
    ]
    if _scan_ok(scan) and scan["trackers"]:
        sections.append(Section(f"Trackers on {co}'s site today", [
            ("text", f"Scan of {scan['url']} ({scan['when']}). Each tag below can be routed through Freshpaint "
                     f"so campaigns keep their signal without sending {data}."),
            _tracker_table(scan, limit=8),
        ]))
    sections += [
        Section("What Freshpaint restores", [
            ("text", "Freshpaint intercepts tracking events, strips "
                     + ("health data" if ph else "protected health information")
                     + ", and forwards clean conversion data to the platforms you already use."),
            ("kv", [
                ("Google Ads / Meta", "Conversion signals flow normally; bidding keeps learning."),
                ("Attribution",       "Multi-touch attribution maintained across channels."),
                ("Remarketing",       "Audiences built on sanitized behavioral data."),
                ("Analytics",         f"GA4, Mixpanel and Amplitude receive events with {data} removed."),
                ("Savings program",   "Copay-card sign-ups and HCP-locator searches tracked as clean conversions.")
                if ph else
                ("EHR attribution",   "Optional: tie appointments and revenue back to campaigns."),
            ]),
        ]),
        Section("Customer performance benchmarks", [("stats", [
            ("20%+",     "ROAS lift after deployment", "good"),
            ("100%",     "Attribution coverage kept", "good"),
            ("2-4x",     "Remarketing advantage kept", "good"),
            ("<2 weeks", "Typical full deployment", "good"),
        ])]),
        Section("Recommended next step", [("callout",
            f"Review the PHI risk scan for {co} together and pick the two campaigns where losing signal would "
            "hurt most. Freshpaint configures those first, so performance is protected from day one.")]),
    ]
    return sections


def _cfo(d: dict) -> list:
    m, co, ph = d["metrics"], d["company"], d["pharma"]
    cmp = reg.HIPAA_CMP
    cases = [[n, a, auth] for n, a, auth, _ in (reg.PHARMA_CASES if ph else reg.ENFORCEMENT_CASES[:7])]
    if ph:
        exposure = Section("The liability exposure", [
            ("text", "Most pharma brands sit outside HIPAA, but sharing health data through tracking tags is "
                     "still enforced: by the FTC under Section 5 and the Health Breach Notification Rule, by state "
                     "attorneys general, and through class actions under consumer health data and wiretap laws. "
                     "Penalties count per violation, so every page, tag and visitor can multiply the total."),
            ("stats", [
                (money(reg.FTC_CIVIL_PENALTY_MAX), "FTC civil penalty per violation (max)", "bad"),
                (money(reg.CIPA_STATUTORY_DAMAGES), "CA wiretap (CIPA) damages per violation", "bad"),
                (reg.LARGEST_PIXEL_SETTLEMENT[0], "Largest health pixel settlement", "bad"),
            ]),
        ])
    else:
        exposure = Section("The liability exposure", [
            ("text", "Impermissible disclosure of PHI to a tracking vendor is a HIPAA violation, and every page, "
                     "tag and visitor can multiply the count. Separate exposure comes from the FTC, state attorneys "
                     "general and class actions under wiretap and privacy statutes."),
            ("stats", [
                (money(cmp["max_per_violation"]), "OCR penalty per violation (max)", "bad"),
                (money(cmp["annual_cap"]), "Annual cap per provision", "bad"),
                (reg.LARGEST_PIXEL_SETTLEMENT[0], "Largest pixel class settlement", "bad"),
            ]),
        ])
    return [
        exposure,
        Section("Recent enforcement and settlements", [
            ("table", {"cols": ["Organization", "Amount", "Authority / year"],
                       "widths": [40, 25, 35], "rows": cases}),
        ]),
        Section("The cost of going dark", [
            ("text", f"Based on {co}'s ad spend of {money(m['annual_spend'])}/year, removing non-compliant "
                     "trackers without replacing them produces these annual efficiency losses:"),
            ("stats", [
                (money(m["roas_loss"]), "Lost ROAS efficiency", "warn"),
                (money(m["attr_loss"]), "Attribution waste", "warn"),
                (money(m["rmkt_loss"]), "Remarketing loss", "warn"),
                (money(m["total"]),     "Total annual impact", "bad"),
            ]),
        ]),
        Section("Investment vs. cost of inaction", [
            ("stats", [
                (money(m["freshpaint_cost"]) + "/yr", "Freshpaint investment", "good"),
                (f"{m['roi']:.1f}x",                   "ROI vs. going dark", "good"),
                (payback_str(m["payback"]),            "Payback period", "good"),
                (money(m["total"] - m["freshpaint_cost"]), "Net annual benefit", "good"),
            ]),
            ("text", "This ROI counts only marketing efficiency. It excludes the cost of an investigation, "
                     "breach notification, a class-action defense or settlement, and reputational impact."),
        ]),
        Section("Recommended next step", [("callout",
            "Request a customized risk assessment and pricing proposal. Freshpaint is a fixed annual "
            "subscription with no infrastructure overhead, and "
            + ("data processing terms are included." if ph else "the BAA is included."))]),
    ]


def _gc(d: dict) -> list:
    sc, co, ph = d["state_ctx"], d["company"], d["pharma"]
    timeline = reg.PHARMA_FEDERAL_TIMELINE if ph else reg.FEDERAL_TIMELINE
    sections = [
        Section("Federal landscape: where things stand", [
            ("callout", reg.PHARMA_STATUS if ph else reg.OCR_STATUS),
            ("table", {"cols": ["Development", "Date", "What it means"], "widths": [24, 11, 65],
                       "rows": [[n, dt, desc] for n, dt, desc in timeline]}),
        ]),
    ]
    if sc["laws"]:
        rows = []
        for l in sc["laws"]:
            if l["score"] == 0 and l.get("status") == "none":
                rows.append([f"{l['abbr']} - {l['name']}", "No comprehensive law", "-", "-", "-"])
                continue
            rows.append([
                f"{l['abbr']} - {l['law']}",
                f"{l['status_label']} ({l.get('effective', '-')})",
                l.get("hipaa_exemption", "-"),
                "Yes" if l.get("private_right", 0) >= 2 else "No",
                f"{l['score']}/100",
            ])
        sections.append(Section(f"State laws where {co} operates", [
            ("text", "HIPAA exemptions rarely help a pharma brand. They cover HIPAA covered entities or PHI, "
                     "and consumer-facing brand data is usually neither, so plan as if each law below applies in full."
                     if ph else
                     "Entity-level exemptions remove HIPAA-covered entities from a law entirely. Data-level "
                     "exemptions cover only PHI, so a hospital's non-PHI website and marketing data is still in scope."),
            ("table", {"cols": ["State / law", "Status", "HIPAA exemption", "Private suit", "Exposure"],
                       "widths": [33, 22, 23, 10, 12], "rows": rows}),
        ]))
    sections += [
        Section("Enforcement record", [
            ("table", {"cols": ["Matter", "Amount", "Forum", "Conduct"], "widths": [18, 12, 18, 52],
                       "rows": [[n, a, f, desc] for n, a, f, desc in
                                (reg.PHARMA_CASES if ph else reg.ENFORCEMENT_CASES[:8])]}),
        ]),
        Section("Freshpaint's defensible compliance position", [("kv", [
            ("Contract terms",    "Data processing terms for consumer health data, plus a BAA wherever the brand "
                                  "handles PHI as a business associate (hub or copay support).")
            if ph else
            ("Signed BAA",        "Freshpaint signs a Business Associate Agreement covering data processed through the platform."),
            ("Health-data sanitization", "Events are scrubbed of health data before transmission to any third-party destination.")
            if ph else
            ("PHI sanitization",  "Events are scrubbed of PHI before transmission to any third-party destination."),
            ("Audit trail",       "Logs of what was collected, sanitized and routed: documentary evidence for an inquiry."),
            ("Consent-aware",     "Routing can honor consent and opt-out signals required by state laws."),
            ("No raw data off-ramp" if ph else "No PHI off-ramp",
             "Ad and analytics platforms receive only sanitized events, never raw "
             + ("health data." if ph else "PHI.")),
        ])]),
        Section("Recommended next step", [("callout",
            "Request Freshpaint's legal package: " + ("data processing terms" if ph else "BAA template")
            + ", SOC 2 Type II report, security questionnaire "
            "responses, and an architecture diagram for your compliance file.")]),
    ]
    return sections


def _privacy(d: dict) -> list:
    sc, scan, co, ph = d["state_ctx"], d.get("scan"), d["company"], d["pharma"]
    sections = []
    if ph and _scan_ok(scan) and scan["trackers"]:
        sections.append(Section("Tracking-vendor inventory", [
            ("text", f"Static scan of {scan['url']} ({scan['when']}). Each vendor below is a recipient you must "
                     "disclose and control under state consumer health data laws. Tags loaded dynamically through "
                     "a tag manager may not appear here; include them in your data inventory too."),
            _tracker_table(scan, limit=10),
        ]))
    elif _scan_ok(scan) and scan["trackers"]:
        sections.append(Section("Tracking-vendor inventory", [
            ("text", f"Static scan of {scan['url']} ({scan['when']}). {scan['n_no_baa']} of "
                     f"{len(scan['trackers'])} vendors do not offer a BAA. Tags loaded dynamically through a tag "
                     "manager may not appear here; include them in your risk analysis too."),
            _tracker_table(scan, limit=10),
        ]))
    elif ph:
        sections.append(Section("Tracking-vendor inventory", [
            ("text", "Most pharma brands cannot produce a current list of every tag firing across brand, "
                     "unbranded and HCP sites. Start with a scan of each public site, then add tags managed in "
                     "GTM, savings-program and HCP-locator flows, and mobile SDKs."),
        ]))
    else:
        sections.append(Section("Tracking-vendor inventory", [
            ("text", "Most health systems cannot produce a current list of every tag firing on their sites and "
                     "apps. Start with a PHI risk scan of your public site, then add tags managed in GTM, "
                     "portal and scheduling flows, and mobile SDKs."),
        ]))
    checklist = [
        "Data inventory maps every tracking technology to the consumer health data it can receive, "
        "and the consumer health data privacy policy (WA, NV) lists those recipients.",
        "Health data reaches ad vendors only with consent (opt-in required in WA, NV, CT and others).",
    ] if ph else [
        "HIPAA risk analysis (45 CFR 164.308) names every tracking technology and the data it can receive.",
        "Each vendor that receives PHI has a signed BAA, or is blocked from receiving PHI.",
    ]
    sections.append(Section("Controls checklist", [("bullets", checklist + [
        "Consent and Global Privacy Control signals are honored before data leaves the browser.",
        "No geofencing or location targeting near health facilities (banned in WA, NV, CT, MD and others).",
        "Breach-assessment playbook covers disclosure through pixels and SDKs"
        + (", including the FTC Health Breach Notification Rule where a brand app or tool applies." if ph else "."),
        "Quarterly re-scan; tags drift as marketing adds campaigns.",
    ])]))
    if sc["laws"]:
        n_opt_in = sum(1 for l in sc["laws"] if l.get("health_specificity", 0) >= 2 and l.get("status") == "in_effect")
        n_sale = sum(1 for l in sc["laws"] if l.get("tracker_coverage", 0) >= 3)
        sections.append(Section("State obligations at a glance", [("stats", [
            (str(n_opt_in), "States requiring opt-in for health data", "warn"),
            (str(n_sale), "Health inference, sale or geofence rules", "warn"),
            (str(len(sc["sueable"])), "States allowing private suits", "bad"),
            (str(len(sc["coming"]) + len(sc["pending"])), "Coming soon or pending", "accent"),
        ])]))
    sections += [
        Section("How Freshpaint supports your program", [("kv", [
            ("Data inventory" if ph else "Risk analysis", "A documented data flow for every tracking destination."),
            ("Vendor risk",     ("One governed vendor" if ph else "One BAA-covered vendor")
                                + " sits in front of many ad and analytics tools."),
            ("Consent",         "Consent and opt-out signals applied server-side, consistently."),
            ("Audit evidence",  "Logs of collection, sanitization and routing for audits or inquiries."),
            ("Security",        "SOC 2 Type II, encryption in transit and at rest, SSO and MFA."),
        ])]),
        Section("Recommended next step", [("callout",
            f"Schedule a vendor-risk review: Freshpaint maps {co}'s current tags, identifies which receive "
            + ("health data, " if ph else "PHI, ") +
            "and provides security documentation for your third-party risk process.")]),
    ]
    return sections


def _cto(d: dict) -> list:
    scan, co, ph = d.get("scan"), d["company"], d["pharma"]
    sections = [
        Section("How Freshpaint works", [
            ("text", "Freshpaint is an event routing layer, not a replacement analytics platform. A single script "
                     "replaces individual pixels; events are sanitized on HIPAA-compliant infrastructure and "
                     "forwarded to your existing destinations."),
            ("flow", [
                "Visitor's browser",
                "Freshpaint SDK  (replaces individual pixels)",
                "Freshpaint HIPAA infrastructure  ("
                + ("health data" if ph else "PHI") + " stripped, consent applied)",
                "Google Ads  |  Meta CAPI  |  GA4  |  CDP / warehouse  |  " + ("CRM" if ph else "EHR"),
            ]),
        ]),
        Section("Implementation plan", [
            ("stats", [
                ("1-3 days",  "Basic tracking deployed", "accent"),
                ("1-2 weeks", "Full attribution configured", "accent"),
                ("0",         "New infrastructure to run", "good"),
                ("100+",      "Native integrations", "accent"),
            ]),
            ("kv", [
                ("Day 1",    "Replace pixel tags with one Freshpaint tag via GTM or direct install."),
                ("Day 1-2",  "Define allowlists of safe event properties; everything else is blocked by default."),
                ("Week 1",   "Connect destinations: Google Ads, Meta, analytics and CDP accounts."),
                ("Week 2",   "Optional: connect CRM or savings-program data for closed-loop attribution."
                             if ph else "Optional: connect EHR/scheduling for closed-loop attribution."),
            ]),
        ]),
    ]
    if _scan_ok(scan) and scan["trackers"]:
        sections.append(Section(f"Tags to migrate on {co}'s site", [_tracker_table(scan, limit=10)]))
    sections += [
        Section("Security and compliance posture", [("kv", [
            ("SOC 2 Type II",    "Annual third-party audit; report available under NDA."),
            ("HIPAA BAA",        "Available where the brand handles PHI (hub, copay support); executed at signature."
                                 if ph else "Executed at contract signature."),
            ("Data residency",   "PHI-bearing events processed on US infrastructure."),
            ("Encryption",       "TLS 1.2+ in transit; AES-256 at rest."),
            ("Access controls",  "Role-based access, SSO/SAML, MFA, admin audit log."),
            ("Pen testing",      "Annual third-party penetration test."),
        ])]),
        Section("Integration compatibility", [("kv", [
            ("Ad platforms",   "Google Ads, Meta CAPI, LinkedIn, TikTok, Microsoft Ads"),
            ("Analytics",      "GA4, Adobe Analytics, Mixpanel, Amplitude, Heap"),
            ("CDPs",           "Segment, mParticle, Tealium, RudderStack"),
            ("CRM",            "Salesforce, HubSpot, Marketo"),
            ("EHR",            "Epic (FHIR R4), athenahealth, Oracle Health"),
            ("Warehouse",      "Snowflake, BigQuery, Redshift, Databricks"),
        ])]),
        Section("Recommended next step", [("callout",
            "Book a technical architecture review. Freshpaint's team maps your current tag configuration, "
            "identifies PHI exposure points, and delivers a deployment plan within five business days.")]),
    ]
    return sections


_BUILDERS = {"exec": _exec, "cmo": _cmo, "cfo": _cfo, "gc": _gc, "privacy": _privacy, "cto": _cto}


def prepare(data: dict) -> dict:
    d = dict(data)
    d.setdefault("company", "Your Organization")
    d.setdefault("states", [])
    if "metrics" not in d:
        d["metrics"] = calc_roi(d.get("monthly_spend", 50_000),
                                d.get("org_type", "Hospital / Health System"),
                                d.get("freshpaint_cost", 40_000))
    d["pharma"] = d.get("org_type") == PHARMA
    d["state_ctx"] = _state_context(d["states"])
    d["date_str"] = date.today().strftime("%B %Y")
    return d


def build_brief(key: str, data: dict) -> Brief:
    d = data if "state_ctx" in data else prepare(data)
    persona = PERSONAS[key]
    if d["pharma"]:
        persona = {**persona, **PHARMA_PERSONA_OVERRIDES.get(key, {})}
    return Brief(key=key, persona=persona, sections=_BUILDERS[key](d))


def build_briefs(data: dict, personas: list[str] | None = None) -> list[Brief]:
    d = prepare(data)
    keys = [k for k in PERSONA_ORDER if k in (personas or PERSONA_ORDER)]
    return [build_brief(k, d) for k in keys]
