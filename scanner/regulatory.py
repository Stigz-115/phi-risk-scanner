"""
Federal regulatory facts and enforcement history used across the app and
the stakeholder decks. Keep every dollar figure and date here so there is
one place to update (and one place a reviewer has to check).

Last reviewed: see LAST_REVIEWED. Directional sales guidance, not legal advice.
"""

LAST_REVIEWED = "2026-10-20"

# ── HIPAA civil money penalties (45 CFR 160.404, inflation-adjusted) ─────────
# Source: 91 FR 3665 (Jan 28, 2026) — https://www.govinfo.gov/content/pkg/FR-2026-01-28/html/2026-01688.htm
HIPAA_CMP = {
    "max_per_violation": 73_011,
    "annual_cap": 2_190_294,
    "tiers": [
        ("Did not know",                       "$145 - $73,011"),
        ("Reasonable cause",                   "$1,461 - $73,011"),
        ("Willful neglect, corrected",         "$14,602 - $73,011"),
        ("Willful neglect, not corrected",     "$73,011 - $2,190,294"),
    ],
    "source": "91 FR 3665 (Jan 2026)",
}

FTC_HBNR_MAX_PER_VIOLATION = 53_088   # 16 CFR 1.98 (2025 adjustment)

# ── Federal regulatory timeline (most recent last) ───────────────────────────
FEDERAL_TIMELINE = [
    ("HHS OCR tracking bulletin", "Dec 2022",
     "OCR said tracking technologies on authenticated pages (portals, scheduling) and on some "
     "unauthenticated pages can disclose PHI; vendors receiving it need a BAA. Updated Mar 2024."),
    ("HHS / FTC joint letters", "Jul 2023",
     "About 130 hospital systems and telehealth providers warned about pixel tracking."),
    ("FTC Health Breach Notification Rule", "Jul 2024",
     "Amended rule treats unauthorized sharing of health app data with advertisers as a breach. "
     "Civil penalties above $50,000 per violation."),
    ("AHA v. Becerra (N.D. Tex.)", "Jun 2024",
     "Court vacated the bulletin's position that an IP address plus a visit to a public "
     "condition-related page is PHI. HHS withdrew its appeal (Aug 2024). Guidance on "
     "authenticated pages and mobile apps still stands."),
    ("FTC v. Hims & Hers", "Jul 2026",
     "FTC, joined by California and Utah, alleges telehealth pixels shared treatment and "
     "prescription data with ad platforms. Shows enforcement now reaches unauthenticated "
     "consumer journeys through FTC Act Section 5 and state UDAP law."),
]

# Plain-language status line for the OCR guidance (used by GC / Privacy briefs).
OCR_STATUS = (
    "The 2022 OCR bulletin was partly vacated in June 2024 (AHA v. Becerra) for "
    "public, unauthenticated pages. It still applies to patient portals, scheduling "
    "flows, and apps, and the FTC and state AGs have filled the gap on public pages."
)

# ── Enforcement & settlements (amount, authority/year, description) ─────────
# Ordered for presentation: largest / most recent first.
ENFORCEMENT_CASES = [
    ("Kaiser Permanente", "$46M+",   "Class action - 2025/26",
     "Web and app trackers shared member search and navigation data with advertisers; "
     "13.4M members notified. Settlement up to $47.5M."),
    ("Sutter Health",     "$21.5M",  "Class action - 2026",
     "Pixel tracking on patient-facing web pages; preliminary approval granted."),
    ("Mass General Brigham", "$18.4M", "Class action - 2022",
     "Cookies and analytics on patient-facing sites shared data without consent."),
    ("Advocate Aurora",   "$12.225M","Class action - 2024",
     "Meta Pixel on MyChart and scheduling pages captured appointment and condition data."),
    ("Penn Medicine",     "Up to $9.25M", "Class action - 2026",
     "Pixel suit under Pennsylvania's wiretap act (WESCA); final approval pending."),
    ("BetterHelp",        "$7.8M",   "FTC - 2023",
     "Shared mental-health intake data with advertisers despite privacy promises."),
    ("Cerebral",          "$7M+",    "FTC - 2024",
     "Pixels exposed mental-health data of 3.2M users to ad platforms."),
    ("Healthline Media",  "$1.55M",  "CA AG (CCPA) - 2025",
     "Health-suggestive article titles shared with ad partners after users opted out."),
    ("GoodRx",            "$1.5M",   "FTC - 2023",
     "First Health Breach Notification Rule penalty: prescription data shared with Meta, Google."),
    ("NewYork-Presbyterian", "$300K", "NY AG - 2024",
     "Meta Pixel on public web pages disclosed health-related browsing."),
    ("Hims & Hers",       "Pending", "FTC + CA + UT - 2026",
     "Complaint alleges pixels sent treatment and prescription data to Meta, Snap and others."),
]

LARGEST_PIXEL_SETTLEMENT = ("$46M+", "Kaiser Permanente (2025/26)")

# Sources reviewers should re-check each quarter.
SOURCES = [
    "https://www.hhs.gov/hipaa/for-professionals/privacy/guidance/hipaa-online-tracking/index.html",
    "https://www.mcdermottlaw.com/insights/ocr-withdraws-appeal-in-aha-v-becerra/",
    "https://www.govinfo.gov/content/pkg/FR-2026-01-28/html/2026-01688.htm",
    "https://www.techtarget.com/healthtechsecurity/news/366635442/Kaiser-settles-class-action-web-tracking-lawsuit-for-46M",
    "https://www.bakerdonelson.com/ftc-targets-hims-hers-over-health-data-sharing-the-tracking-tools-are-now-part-of-the-case",
    "https://www.hipaajournal.com/advocate-aurora-health-settles-pixel-lawsuit-for-12-25-million/",
]

# ── Pharma / life sciences (non-HIPAA) ───────────────────────────────────────
# Manufacturers are usually not HIPAA covered entities. Consumer-facing brand
# data (condition pages, savings / copay sign-ups, HCP locators) falls under the
# FTC Act, state consumer health data laws and wiretap statutes instead. They
# act as business associates only for some hub and copay-support functions.
FTC_CIVIL_PENALTY_MAX = 53_088        # 16 CFR 1.98; FTC kept 2025 levels for 2026
CIPA_STATUTORY_DAMAGES = 5_000        # Cal. Penal Code 637.2, per violation

PHARMA_STATUS = (
    "Most pharma brands are not HIPAA covered entities, so OCR's tracking guidance rarely "
    "reaches their consumer sites. That is not a safe harbor: the FTC enforces health-data "
    "sharing under Section 5 and the Health Breach Notification Rule, state consumer health "
    "data laws (Washington, Nevada, Connecticut and others) apply in full, and wiretap suits "
    "target pixels on prescription and checkout pages."
)

PHARMA_FEDERAL_TIMELINE = [
    ("FTC v. GoodRx", "Feb 2023",
     "First Health Breach Notification Rule penalty: prescription and medication data shared "
     "with Meta and Google through pixels and SDKs, without a HIPAA nexus."),
    ("FTC v. BetterHelp", "Mar 2023",
     "$7.8M for sharing health questionnaire data with advertisers despite privacy promises."),
    ("FTC Health Breach Notification Rule", "Jul 2024",
     "Amended rule treats unauthorized sharing of health app data with advertisers as a breach. "
     "Civil penalties above $50,000 per violation."),
    ("FTC v. Hims & Hers", "Jul 2026",
     "FTC, joined by California and Utah, alleges pixels shared treatment and prescription "
     "data with ad platforms. Enforcement reaches consumer journeys with no HIPAA nexus."),
]

# Matters brought outside HIPAA (FTC, state AG); the closest analogues for a pharma brand.
PHARMA_CASE_NAMES = ["GoodRx", "BetterHelp", "Cerebral", "Healthline Media", "Hims & Hers"]
PHARMA_CASES = [c for c in ENFORCEMENT_CASES if c[0] in PHARMA_CASE_NAMES]
