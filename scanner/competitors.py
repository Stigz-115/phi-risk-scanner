"""
Competitive comparison data for Freshpaint vs. common alternatives.
Each feature is scored: 2 = full, 1 = partial/limited, 0 = no.
"""

# ── Feature definitions ───────────────────────────────────────────────────────
FEATURES = [
    # (key, label, category, description, weight)
    ("hipaa_baa",       "HIPAA BAA Included",           "Compliance",   "Vendor signs a Business Associate Agreement covering your analytics data.", 3),
    ("phi_redaction",   "Automatic PHI Redaction",       "Compliance",   "System intercepts and strips PHI before it leaves your environment — no manual tagging required.", 3),
    ("hc_first",        "Built for Healthcare",          "Compliance",   "Product and support team designed specifically for HIPAA-regulated entities.", 2),
    ("ocr_defensible",  "OCR/FTC Defensible Posture",    "Compliance",   "Architecture that satisfies OCR's 2022 pixel guidance and FTC enforcement position.", 3),
    ("state_laws",      "State Privacy Law Coverage",    "Compliance",   "Addresses WA My Health MY Data, TX THIPA, CA CCPA health provisions, and similar.", 2),
    ("google_capi",     "Google Ads Signal Preservation","Marketing",    "Maintains Google Enhanced Conversions / server-side tagging after removing client-side pixels.", 2),
    ("meta_capi",       "Meta CAPI Integration",         "Marketing",    "Server-side Conversions API so Meta campaigns keep optimization signals post-pixel removal.", 2),
    ("attribution",     "Cross-Channel Attribution",     "Marketing",    "Accurate attribution across paid, organic, and direct — without PHI exposure.", 2),
    ("ga4_compat",      "GA4 / Adobe Compatible",        "Analytics",    "Works alongside existing analytics tools; does not require replacing them.", 1),
    ("cdp_compat",      "CDP / Warehouse Compatible",    "Analytics",    "Routes clean events to Segment, mParticle, Snowflake, BigQuery, etc.", 1),
    ("ehr_int",         "EHR Integration",               "Analytics",    "Native connectors to Epic, Cerner, athenahealth for clinical data enrichment.", 2),
    ("consent_mgmt",    "Consent Management Layer",      "Governance",   "Built-in patient consent capture and enforcement before any data leaves.", 2),
    ("audit_trail",     "Compliance Audit Trail",        "Governance",   "Immutable logs of what data was collected, transformed, and routed — for compliance reviews.", 2),
    ("no_code",         "No-Code Implementation",        "Operations",   "Marketing/analytics teams can configure without engineering involvement.", 1),
    ("time_to_value",   "Fast Time-to-Value",            "Operations",   "Days to deploy, not months. Minimal internal engineering resources required.", 2),
    ("support",         "Healthcare Compliance Support", "Operations",   "Dedicated support team familiar with HIPAA, OCR guidance, and healthcare marketing.", 2),
]

FEATURE_KEYS  = [f[0] for f in FEATURES]
FEATURE_CATS  = sorted(set(f[2] for f in FEATURES))

# ── Competitor profiles ───────────────────────────────────────────────────────
# Score: 2=yes, 1=partial, 0=no
COMPETITORS = {
    "freshpaint": {
        "name":      "Freshpaint",
        "category":  "Healthcare Analytics Proxy",
        "tagline":   "The only platform built exclusively to make healthcare marketing analytics HIPAA-compliant.",
        "color":     "#00FFB2",
        "logo_char": "FP",
        "pricing":   "$25K–$150K/yr",
        "deploy":    "Days",
        "baa":       "Included",
        "ideal_for": "Any HIPAA-covered entity running digital advertising",
        "scores": {
            "hipaa_baa":      2,
            "phi_redaction":  2,
            "hc_first":       2,
            "ocr_defensible": 2,
            "state_laws":     2,
            "google_capi":    2,
            "meta_capi":      2,
            "attribution":    2,
            "ga4_compat":     2,
            "cdp_compat":     2,
            "ehr_int":        2,
            "consent_mgmt":   2,
            "audit_trail":    2,
            "no_code":        2,
            "time_to_value":  2,
            "support":        2,
        },
        "win_reasons": [],
        "honest_gaps": "Higher cost than DIY; requires BAA process with Freshpaint.",
    },
    "ga4": {
        "name":      "Google Analytics 4",
        "category":  "Web Analytics",
        "tagline":   "Google's flagship analytics platform — powerful, but not designed for HIPAA.",
        "color":     "#E37400",
        "logo_char": "G4",
        "pricing":   "Free / GA360 from ~$50K/yr",
        "deploy":    "Hours",
        "baa":       "Not Available",
        "ideal_for": "Non-regulated businesses; ecommerce; content sites",
        "scores": {
            "hipaa_baa":      0,
            "phi_redaction":  0,
            "hc_first":       0,
            "ocr_defensible": 0,
            "state_laws":     0,
            "google_capi":    1,
            "meta_capi":      0,
            "attribution":    1,
            "ga4_compat":     2,
            "cdp_compat":     1,
            "ehr_int":        0,
            "consent_mgmt":   1,
            "audit_trail":    0,
            "no_code":        2,
            "time_to_value":  2,
            "support":        0,
        },
        "win_reasons": ["Free tier available", "Familiar UI for marketing teams", "Fast setup", "Rich reporting"],
        "honest_gaps": "No BAA available. OCR has cited GA4 pixel use in enforcement actions. Cannot be used for HIPAA analytics without Freshpaint or equivalent proxy.",
        "key_objection": "We already use GA4",
        "counter": "GA4 cannot sign a BAA. Every event it receives — including page URLs like /cancer-screening or /mental-health — is sent to Google servers without PHI protection. Freshpaint proxies those events, strips PHI, and forwards clean data to GA4 so you keep your existing reports and dashboards.",
    },
    "segment": {
        "name":      "Segment (Twilio)",
        "category":  "Customer Data Platform",
        "tagline":   "Leading CDP — offers a BAA, but PHI redaction is manual and limited.",
        "color":     "#52BD95",
        "logo_char": "SG",
        "pricing":   "$120/mo (Team) → enterprise",
        "deploy":    "Weeks",
        "baa":       "Available (Business plan+)",
        "ideal_for": "Mid-market and enterprise with dedicated data engineering teams",
        "scores": {
            "hipaa_baa":      2,
            "phi_redaction":  1,
            "hc_first":       0,
            "ocr_defensible": 1,
            "state_laws":     1,
            "google_capi":    1,
            "meta_capi":      1,
            "attribution":    1,
            "ga4_compat":     2,
            "cdp_compat":     2,
            "ehr_int":        0,
            "consent_mgmt":   1,
            "audit_trail":    1,
            "no_code":        1,
            "time_to_value":  1,
            "support":        0,
        },
        "win_reasons": ["BAA available", "Strong CDP ecosystem", "Good developer tools", "Wide destination library"],
        "honest_gaps": "Segment's BAA does not cover data in transit through client-side JS. PHI redaction requires manual configuration per event — easy to misconfigure. No healthcare-specific support.",
        "key_objection": "Segment offers a BAA",
        "counter": "Segment's BAA covers data at rest in their systems — but client-side JS still fires before Segment receives the event. That unprotected transmission is exactly what OCR cited in the 2022 bulletin. Freshpaint's server-side proxy intercepts data before it leaves the browser.",
    },
    "mparticle": {
        "name":      "mParticle",
        "category":  "Customer Data Platform",
        "tagline":   "Enterprise CDP with a BAA option — but the same client-side exposure gap.",
        "color":     "#6C5CE7",
        "logo_char": "MP",
        "pricing":   "Enterprise (~$60K–$200K+/yr)",
        "deploy":    "Weeks–months",
        "baa":       "Available (Enterprise)",
        "ideal_for": "Large enterprises with dedicated data engineering",
        "scores": {
            "hipaa_baa":      2,
            "phi_redaction":  1,
            "hc_first":       0,
            "ocr_defensible": 1,
            "state_laws":     1,
            "google_capi":    1,
            "meta_capi":      1,
            "attribution":    1,
            "ga4_compat":     1,
            "cdp_compat":     2,
            "ehr_int":        0,
            "consent_mgmt":   1,
            "audit_trail":    1,
            "no_code":        0,
            "time_to_value":  0,
            "support":        0,
        },
        "win_reasons": ["Strong enterprise CDP", "BAA available", "Robust data quality tools", "Good mobile SDK"],
        "honest_gaps": "Same client-side exposure gap as Segment. Heavy implementation — typically 3–6 months. No healthcare-specific product direction. Overkill for most healthcare marketing use cases.",
        "key_objection": "We use mParticle for our CDP",
        "counter": "mParticle and Freshpaint are complementary, not competitive. Freshpaint proxies events server-side, strips PHI, then forwards clean events to mParticle. You keep your CDP investment and fix the compliance gap simultaneously.",
    },
    "onetrust": {
        "name":      "OneTrust",
        "category":  "Consent & Privacy Management",
        "tagline":   "Consent management and privacy ops — not a HIPAA analytics solution.",
        "color":     "#1877F2",
        "logo_char": "OT",
        "pricing":   "$15K–$100K+/yr",
        "deploy":    "Weeks",
        "baa":       "Not Applicable",
        "ideal_for": "GDPR/CCPA consent management; privacy program management",
        "scores": {
            "hipaa_baa":      0,
            "phi_redaction":  0,
            "hc_first":       1,
            "ocr_defensible": 1,
            "state_laws":     2,
            "google_capi":    0,
            "meta_capi":      0,
            "attribution":    0,
            "ga4_compat":     1,
            "cdp_compat":     1,
            "ehr_int":        0,
            "consent_mgmt":   2,
            "audit_trail":    2,
            "no_code":        1,
            "time_to_value":  1,
            "support":        1,
        },
        "win_reasons": ["Strong consent management", "State privacy law support", "Privacy program tooling", "GRC integrations"],
        "honest_gaps": "OneTrust manages consent decisions — it does not intercept or redact PHI in analytics data. A cookie banner does not protect you from OCR's pixel enforcement. These products solve different problems.",
        "key_objection": "We have OneTrust / a cookie banner",
        "counter": "OneTrust manages consent preference records — it doesn't stop trackers from firing or strip PHI from events. OCR's enforcement actions have explicitly stated that consent banners do not satisfy HIPAA requirements for pixel tracking. Freshpaint operates at a different layer: intercepting the data itself.",
    },
    "gtm_server": {
        "name":      "GTM Server-Side (DIY)",
        "category":  "Self-Managed Infrastructure",
        "tagline":   "Server-side tagging you build and own — no BAA, no healthcare expertise built in.",
        "color":     "#DB4437",
        "logo_char": "SS",
        "pricing":   "$0 license + $50K–$200K build cost + ongoing ops",
        "deploy":    "3–9 months",
        "baa":       "N/A — you own the infrastructure",
        "ideal_for": "Large enterprises with dedicated engineering teams and no HIPAA requirements",
        "scores": {
            "hipaa_baa":      0,
            "phi_redaction":  1,
            "hc_first":       0,
            "ocr_defensible": 1,
            "state_laws":     1,
            "google_capi":    2,
            "meta_capi":      2,
            "attribution":    1,
            "ga4_compat":     2,
            "cdp_compat":     1,
            "ehr_int":        0,
            "consent_mgmt":   1,
            "audit_trail":    0,
            "no_code":        0,
            "time_to_value":  0,
            "support":        0,
        },
        "win_reasons": ["No licensing cost", "Full control over data", "Google/Meta signal preservation possible"],
        "honest_gaps": "No vendor BAA — legal risk sits entirely with your organization. PHI redaction logic must be custom-built and maintained. Regulatory knowledge not included. Most healthcare orgs underestimate build complexity and ongoing maintenance. One misconfiguration = OCR exposure.",
        "key_objection": "We'll build server-side tagging ourselves",
        "counter": "Server-side tagging infrastructure costs $50K–$200K to build and requires ongoing engineering maintenance. More importantly, building it doesn't give you a BAA — which means legal risk stays with your organization. Freshpaint delivers the same server-side signal preservation with a BAA included, deployed in days not months.",
    },
    "heap": {
        "name":      "Heap / Mixpanel",
        "category":  "Product Analytics",
        "tagline":   "Excellent product analytics — not designed for HIPAA or healthcare marketing.",
        "color":     "#FF5154",
        "logo_char": "HP",
        "pricing":   "Free → $3.6K–$36K+/yr",
        "deploy":    "Hours–days",
        "baa":       "Available (Enterprise tier)",
        "ideal_for": "SaaS product teams; non-regulated digital products",
        "scores": {
            "hipaa_baa":      1,
            "phi_redaction":  0,
            "hc_first":       0,
            "ocr_defensible": 0,
            "state_laws":     0,
            "google_capi":    0,
            "meta_capi":      0,
            "attribution":    1,
            "ga4_compat":     1,
            "cdp_compat":     1,
            "ehr_int":        0,
            "consent_mgmt":   0,
            "audit_trail":    0,
            "no_code":        2,
            "time_to_value":  2,
            "support":        0,
        },
        "win_reasons": ["Auto-capture reduces tagging burden", "Strong funnel/retention analytics", "Easy setup"],
        "honest_gaps": "BAA available at enterprise tier but auto-capture by design collects everything — including PHI. No PHI redaction layer. Not designed for healthcare marketing attribution use cases.",
        "key_objection": "We use Heap/Mixpanel for analytics",
        "counter": "Heap/Mixpanel are product analytics tools — great for understanding user flows in your app. Freshpaint solves a different problem: HIPAA-compliant marketing attribution and ad platform signal preservation. They're complementary; Freshpaint can route clean events to Mixpanel.",
    },
    "ours_privacy": {
        "name":      "Ours Privacy",
        "category":  "HIPAA CDP & Server-Side Tag Manager",
        "tagline":   "Closest look-alike: a BAA-covered CDP that strips PHI before ad platforms — with key features gated to Enterprise.",
        "color":     "#F5A524",
        "logo_char": "OP",
        "pricing":   "Quote only; tiers by monthly tracked users (Essential ≤50K → Enterprise+)",
        "deploy":    "Days (vendor claim; EHR add-on 4–6 weeks)",
        "baa":       "Included on all tiers",
        "ideal_for": "Digital health / DTC brands wanting an all-in-one HIPAA marketing stack",
        "scores": {
            "hipaa_baa":      2,
            "phi_redaction":  2,
            "hc_first":       2,
            "ocr_defensible": 2,
            "state_laws":     1,
            "google_capi":    2,
            "meta_capi":      2,
            "attribution":    2,
            "ga4_compat":     2,
            "cdp_compat":     2,
            "ehr_int":        1,
            "consent_mgmt":   1,
            "audit_trail":    2,
            "no_code":        2,
            "time_to_value":  2,
            "support":        2,
        },
        "win_reasons": [
            "Same core architecture (BAA + PHI stripping + server-side routing)",
            "Bundles consent, A/B testing, session replay, heatmaps (mostly add-ons)",
            "Momentum: $15M Series A (Aug 2026), 200+ customers claimed",
            "Runs a dedicated 'Freshpaint alternative' migration program",
        ],
        "honest_gaps": "Integrated consent manager, EHR integrations, programmatic/DSP destinations and SSO are Enterprise-only; "
                       "analytics, A/B testing and session replay are add-ons; Essential allows only one destination beyond "
                       "GA4/Google Ads/Meta. No public pricing. Founded 2024 with limited third-party reviews; EHR connectivity "
                       "runs through a partner. US-only hosting.",
        "key_objection": "Ours Privacy does what Freshpaint does, plus consent, A/B testing and session replay",
        "counter": "On architecture they're comparable — don't argue that. Win on total cost and fit: ask the prospect for an "
                   "all-in Ours quote at the tier that includes the features they want (integrated consent, EHR, SSO and extra "
                   "destinations sit at Enterprise; analytics, testing and replay are add-ons). Then compare Freshpaint's "
                   "track record, customer references in their segment, and depth of healthcare destinations. Use Freshpaint's "
                   "own verified pricing and integration list — don't guess at theirs.",
        "last_verified": "2026-10-20",
        "sources": ["https://oursprivacy.com/pricing", "https://security.oursprivacy.com/",
                    "https://www.fiercehealthcare.com/health-tech/hipaa-compliant-marketing-platform-ours-privacy-lands-15m"],
    },
    "piwik_pro": {
        "name":      "Piwik PRO",
        "category":  "Privacy-First Analytics Suite",
        "tagline":   "A BAA-covered GA4 replacement with consent and tag management — thin on ad-platform activation.",
        "color":     "#3B6CF6",
        "logo_char": "PP",
        "pricing":   "Healthcare Enterprise by quote (Business from ~€35/mo has no clear BAA)",
        "deploy":    "Days to first insights; weeks for a full GA replacement",
        "baa":       "Enterprise / Healthcare Enterprise",
        "ideal_for": "Health systems replacing GA4 for analytics, or needing EU / private-cloud hosting",
        "scores": {
            "hipaa_baa":      2,
            "phi_redaction":  1,
            "hc_first":       1,
            "ocr_defensible": 1,
            "state_laws":     1,
            "google_capi":    1,
            "meta_capi":      0,
            "attribution":    1,
            "ga4_compat":     1,
            "cdp_compat":     1,
            "ehr_int":        0,
            "consent_mgmt":   2,
            "audit_trail":    1,
            "no_code":        1,
            "time_to_value":  1,
            "support":        2,
        },
        "win_reasons": [
            "Full analytics UI under a BAA (familiar to former Universal Analytics users)",
            "Hosting choice: US, EU, or private cloud on Azure",
            "Consent, tag manager, analytics and CDP from one vendor; ISO 27001 + SOC 2",
            "Hospital references (e.g., Michigan Medicine, Boston Medical)",
        ],
        "honest_gaps": "Analytics-first, not an ad-signal product: no native Meta Conversions API, Google Ads limited to offline "
                       "click (GCLID) conversion uploads, and no automatic PHI stripping — customers must keep health terms out "
                       "of conversion names themselves. No EHR or warehouse connectors. Audit log covers logins and admin "
                       "changes, not data flows.",
        "key_objection": "We're replacing GA4 with Piwik PRO, so we're covered",
        "counter": "Piwik PRO covers analytics under a BAA — but paid media is where most pixel risk and most revenue sit. "
                   "Ask how they'll feed Meta without a native Conversions API, and how Google Ads optimizes on GCLID-only "
                   "uploads. Position Freshpaint as the layer that keeps ad platforms learning without PHI. If the buyer "
                   "truly needs EU or private-cloud analytics hosting, concede that point; Piwik PRO is strong there.",
        "last_verified": "2026-10-20",
        "sources": ["https://piwik.pro/hipaa/", "https://piwik.pro/pricing/",
                    "https://help.piwik.pro/support/cdp/send-conversion-data-to-google-ads-without-phi/"],
    },
}

COMPETITOR_KEYS = list(COMPETITORS.keys())
COMPETITOR_NAMES = {k: v["name"] for k, v in COMPETITORS.items()}

SCORE_LABEL = {2: "Yes", 1: "Partial", 0: "No"}
SCORE_COLOR = {2: "#00FFB2", 1: "#E8B80A", 0: "#D42B4A"}
SCORE_ICON  = {2: "✓", 1: "◐", 0: "✗"}


def compare(competitor_keys: list[str]) -> dict:
    """Return a comparison dict: features × [freshpaint, *competitors]."""
    all_keys = ["freshpaint"] + [k for k in competitor_keys if k != "freshpaint"]
    result = []
    for feat_key, label, category, desc, weight in FEATURES:
        row = {
            "key": feat_key, "label": label, "category": category,
            "desc": desc, "weight": weight,
            "scores": {k: COMPETITORS[k]["scores"][feat_key] for k in all_keys},
        }
        result.append(row)
    return {"keys": all_keys, "rows": result}


def freshpaint_advantages(competitor_key: str) -> list[str]:
    """Return list of features where Freshpaint scores higher than competitor."""
    comp = COMPETITORS[competitor_key]
    fp   = COMPETITORS["freshpaint"]
    return [
        FEATURES[[f[0] for f in FEATURES].index(k)][1]
        for k in FEATURE_KEYS
        if fp["scores"][k] > comp["scores"][k]
    ]
