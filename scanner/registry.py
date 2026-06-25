"""
Tracker risk registry.
Each entry maps a tracker ID to its compliance risk profile.
Sources: HHS OCR Bulletin (Dec 2022), FTC enforcement actions,
class-action settlements, vendor DPA/BAA documentation.
"""

TRACKER_REGISTRY = {
    "meta_pixel": {
        "name": "Meta Pixel",
        "company": "Meta Platforms",
        "risk_level": "critical",
        "baa_available": False,
        "baa_notes": "Meta explicitly does not sign HIPAA Business Associate Agreements for advertising products.",
        "phi_capture": [
            "IP address",
            "Full referral URL (may include condition/service name)",
            "URL path parameters",
            "Form field values (appointment type, symptoms)",
            "Custom Audiences matched via hashed email/phone",
            "Browser fingerprint",
        ],
        "regulatory_mentions": [
            "HHS OCR Bulletin — December 2022 (explicitly named)",
            "FTC Action vs. BetterHelp — February 2023 ($7.8M settlement)",
            "FTC Action vs. GoodRx — February 2023 ($1.5M civil penalty)",
            "Class action: Blue Cross Blue Shield MA (2024)",
            "Class action: Cerebral (2023)",
            "DOJ/HHS joint letter to 130 healthcare orgs (July 2023)",
        ],
        "description": "Meta Pixel captures user behavior and sends it to Facebook/Instagram for ad targeting and measurement. It cannot be made HIPAA-compliant because Meta refuses BAAs.",
        "domains": ["connect.facebook.net", "facebook.net", "facebook.com/tr"],
        "inline_fingerprints": ["fbq(", "fbevents.js", "_fbq", "FB.init("],
    },

    "google_analytics": {
        "name": "Google Analytics 4",
        "company": "Google LLC",
        "risk_level": "high",
        "baa_available": True,
        "baa_notes": "BAA available via Google Cloud DPA, but NOT enabled by default. Requires explicit configuration in Google Cloud Console and IP anonymization. Standard GA4 implementation is non-compliant.",
        "phi_capture": [
            "IP address (anonymized only with explicit config)",
            "Full page URL (may include condition/treatment identifiers)",
            "Referral source",
            "Browser and device fingerprint",
            "Session and behavioral data",
            "Google Signals cross-device data (if enabled)",
        ],
        "regulatory_mentions": [
            "HHS OCR Bulletin — December 2022 (Google Analytics named)",
            "Austrian DPA ruling: GA illegal under GDPR (2022)",
            "French CNIL enforcement action vs. GA (2022)",
            "FTC warning letters context (2023)",
        ],
        "description": "GA4 is the world's most common analytics platform but its default configuration captures IP addresses and URL parameters that may constitute PHI on healthcare sites.",
        "domains": [
            "google-analytics.com",
            "analytics.google.com",
            "ssl.google-analytics.com",
        ],
        "inline_fingerprints": [
            "gtag('config', 'G-",
            "ga('create'",
            "ga('send'",
            "GoogleAnalyticsObject",
        ],
    },

    "google_tag_manager": {
        "name": "Google Tag Manager",
        "company": "Google LLC",
        "risk_level": "high",
        "baa_available": False,
        "baa_notes": "GTM is a tag delivery container — it does not collect data itself, but it deploys tags that do. Its presence means unknown third-party trackers may be firing without direct code visibility.",
        "phi_capture": [
            "Indirect — activates other tracking tags",
            "dataLayer contents may include PHI if improperly configured",
            "Unknown tags may fire without source code visibility",
        ],
        "regulatory_mentions": [
            "HHS OCR Bulletin — December 2022 (tracking tech delivery mechanism)",
            "Used to deploy named trackers in multiple enforcement cases",
        ],
        "description": "GTM acts as a container for other tracking scripts. Its presence means the actual tracker inventory may be larger than what's visible in source code. All tags inside GTM inherit its access to page data.",
        "domains": ["googletagmanager.com"],
        "inline_fingerprints": ["GTM-", "dataLayer.push(", "google_tag_manager"],
    },

    "tiktok_pixel": {
        "name": "TikTok Pixel",
        "company": "ByteDance / TikTok",
        "risk_level": "critical",
        "baa_available": False,
        "baa_notes": "TikTok does not offer HIPAA Business Associate Agreements. Data is routed to servers potentially subject to Chinese government access laws.",
        "phi_capture": [
            "IP address",
            "Full page URL",
            "Device fingerprint",
            "Form interaction events",
            "Custom audiences via hashed PII",
            "Email and phone number (hashed)",
        ],
        "regulatory_mentions": [
            "HHS/FTC joint letter to 130 healthcare orgs — July 2023 (TikTok named)",
            "Congressional scrutiny of TikTok data routing",
            "HHS OCR guidance on tracking technologies (2023 update)",
        ],
        "description": "TikTok Pixel tracks user behavior for ad attribution and targeting. No BAA is available, and data sovereignty concerns exist due to ByteDance's Chinese ownership.",
        "domains": ["analytics.tiktok.com", "business-api.tiktok.com", "tiktok.com/i18n/pixel"],
        "inline_fingerprints": ["ttq.load(", "ttq.track(", "TiktokAnalyticsObject", "tiktok_pixel"],
    },

    "linkedin_insight": {
        "name": "LinkedIn Insight Tag",
        "company": "Microsoft / LinkedIn",
        "risk_level": "high",
        "baa_available": False,
        "baa_notes": "LinkedIn advertising products are not covered under Microsoft's standard BAA. LinkedIn's DPA does not constitute a HIPAA Business Associate Agreement for ad tracking.",
        "phi_capture": [
            "IP address",
            "Full page URL",
            "LinkedIn member data (if user is logged in)",
            "Matched audiences via hashed email",
            "Device and browser fingerprint",
        ],
        "regulatory_mentions": [
            "HHS OCR guidance on third-party tracking (2022-2023)",
            "Covered under FTC warnings on healthcare data sharing",
        ],
        "description": "LinkedIn Insight Tag enables B2B ad targeting and conversion tracking by linking website visitors to LinkedIn profiles. Not BAA-eligible through standard agreements.",
        "domains": ["snap.licdn.com", "dc.ads.linkedin.com", "px.ads.linkedin.com"],
        "inline_fingerprints": ["_linkedin_partner_id", "_linkedin_data_partner_ids", "lintrk("],
    },

    "twitter_pixel": {
        "name": "X (Twitter) Pixel",
        "company": "X Corp (formerly Twitter)",
        "risk_level": "high",
        "baa_available": False,
        "baa_notes": "X Corp does not offer HIPAA BAAs for advertising products.",
        "phi_capture": [
            "IP address",
            "Full page URL and referrer",
            "Twitter user matching (if logged in)",
            "Event data (page views, conversions)",
        ],
        "regulatory_mentions": [
            "HHS OCR guidance on third-party tracking (2022-2023)",
            "Covered under FTC warnings on healthcare data sharing",
        ],
        "description": "Twitter/X Pixel tracks user activity for ad conversion measurement and audience building. No healthcare-compliant option exists.",
        "domains": ["static.ads-twitter.com", "t.co/i/adsct", "platform.twitter.com/oct.js"],
        "inline_fingerprints": ["twq(", "twq.push(", "twitter_pixel", "twttr.conversion"],
    },

    "pinterest_tag": {
        "name": "Pinterest Tag",
        "company": "Pinterest Inc.",
        "risk_level": "high",
        "baa_available": False,
        "baa_notes": "Pinterest does not offer HIPAA BAAs for its advertising tag.",
        "phi_capture": [
            "IP address",
            "Full page URL",
            "Pinterest user matching",
            "Conversion events",
            "Custom audiences via hashed email",
        ],
        "regulatory_mentions": [
            "HHS OCR guidance on third-party tracking technologies (2022-2023)",
        ],
        "description": "Pinterest Tag enables ad measurement and audience targeting. Not suitable for healthcare sites without substantial PHI risk.",
        "domains": ["ct.pinterest.com", "pintrk", "pinterest.com/ct.html"],
        "inline_fingerprints": ["pintrk(", "pinterest_conversion", "PinUtils"],
    },

    "snap_pixel": {
        "name": "Snap Pixel",
        "company": "Snap Inc.",
        "risk_level": "high",
        "baa_available": False,
        "baa_notes": "Snap Inc. does not offer HIPAA Business Associate Agreements.",
        "phi_capture": [
            "IP address",
            "Full page URL",
            "Snapchat user matching",
            "Device fingerprint",
            "Conversion events",
        ],
        "regulatory_mentions": [
            "HHS OCR guidance on third-party tracking technologies (2022-2023)",
        ],
        "description": "Snap Pixel tracks ad conversions and enables audience targeting on Snapchat. No compliant path for healthcare use.",
        "domains": ["sc-static.net", "tr.snapchat.com", "snap.com/pixel"],
        "inline_fingerprints": ["snaptr(", "snap_pixel", "snapchat_pixel"],
    },

    "microsoft_clarity": {
        "name": "Microsoft Clarity",
        "company": "Microsoft Corporation",
        "risk_level": "high",
        "baa_available": False,
        "baa_notes": "Microsoft Clarity is not covered under Microsoft's standard enterprise BAA. Session recording tools are specifically flagged in healthcare class-action litigation.",
        "phi_capture": [
            "Full session recordings (video-like replay of all interactions)",
            "All mouse movements, clicks, scrolls",
            "Keyboard input (may include form fields, search queries)",
            "Heatmap data",
            "Rage clicks and frustration signals",
        ],
        "regulatory_mentions": [
            "Session recording tools cited in Advocate Aurora Health class action (2022, $12.25M settlement)",
            "WI AG investigation of session recording tool misuse in healthcare",
            "HHS OCR guidance on capturing sensitive user interactions",
        ],
        "description": "Clarity records full user sessions — every click, scroll, and keystroke. On healthcare sites, this almost certainly captures PHI including symptoms, conditions, and appointment details.",
        "domains": ["clarity.ms", "c.clarity.ms"],
        "inline_fingerprints": ["clarity(", "clarity.ms", "MS_CLARITY"],
    },

    "microsoft_ads": {
        "name": "Microsoft Advertising (UET)",
        "company": "Microsoft Corporation",
        "risk_level": "high",
        "baa_available": True,
        "baa_notes": "Microsoft offers BAAs under enterprise agreements, but Bing Ads UET tags are not automatically covered. Requires explicit agreement and proper configuration.",
        "phi_capture": [
            "IP address",
            "Full page URL",
            "Bing user matching",
            "Conversion events",
            "Custom audiences",
        ],
        "regulatory_mentions": [
            "HHS OCR guidance on third-party ad tracking (2022-2023)",
        ],
        "description": "Microsoft's Universal Event Tracking tag enables Bing Ads conversion measurement and remarketing. BAA possible but not default.",
        "domains": ["bat.bing.com", "c.bing.com", "uet.bing.com"],
        "inline_fingerprints": ["uetq", "bat.bing.com", "UET("],
    },

    "hotjar": {
        "name": "Hotjar",
        "company": "Hotjar Ltd. (Contentsquare)",
        "risk_level": "high",
        "baa_available": False,
        "baa_notes": "Hotjar's DPA does not constitute a HIPAA BAA. Hotjar explicitly states it is not designed for HIPAA compliance. Session recordings on healthcare sites are extremely high risk.",
        "phi_capture": [
            "Full session recordings with keylogging",
            "Form field content (including medical history fields)",
            "Heatmaps showing interactions with health content",
            "Scroll depth and engagement on condition/treatment pages",
            "User feedback containing health information",
        ],
        "regulatory_mentions": [
            "Session recording tools cited in Advocate Aurora Health class action ($12.25M, 2022)",
            "Named in multiple healthcare privacy class actions as a session recorder",
            "HHS OCR guidance on tracking sensitive user interactions",
        ],
        "description": "Hotjar records user sessions and creates heatmaps. On healthcare websites, this captures an extremely detailed record of patient intent and health information seeking behavior.",
        "domains": ["static.hotjar.com", "hotjar.com", "vars.hotjar.com", "script.hotjar.com"],
        "inline_fingerprints": ["hjSetting", "hj(", "Hotjar", "_hjSettings"],
    },

    "fullstory": {
        "name": "FullStory",
        "company": "FullStory Inc.",
        "risk_level": "high",
        "baa_available": True,
        "baa_notes": "FullStory offers HIPAA BAAs under enterprise plans, but default installation captures all page text and form inputs. Must be explicitly configured in 'privacy mode' with data masking enabled.",
        "phi_capture": [
            "Full session recordings",
            "All text visible on screen (including health content)",
            "Form inputs (requires explicit masking config to suppress)",
            "Network requests",
            "Custom user properties",
        ],
        "regulatory_mentions": [
            "Session recording tools cited in Advocate Aurora Health class action",
            "HHS OCR guidance on capturing sensitive user interactions",
        ],
        "description": "FullStory records detailed session replays. While a BAA is available, default configuration captures PHI. Healthcare deployments require specific privacy-mode configuration.",
        "domains": ["fullstory.com", "edge.fullstory.com", "rs.fullstory.com"],
        "inline_fingerprints": ["FS.init(", "fullstory.com", "_fs_script", "window['_fs_"],
    },

    "heap": {
        "name": "Heap Analytics",
        "company": "Heap Inc. (Contentsquare)",
        "risk_level": "medium",
        "baa_available": True,
        "baa_notes": "Heap offers HIPAA-compliant plans with BAA. Requires enabling 'data redaction' for form inputs and configuring allowlists for sensitive pages.",
        "phi_capture": [
            "Automatic event capture (all clicks, form interactions)",
            "Form field values (without redaction config)",
            "User identity data if `.identify()` called with PII",
            "Session data and behavioral flows",
        ],
        "regulatory_mentions": [
            "HHS OCR guidance on auto-capture analytics tools",
        ],
        "description": "Heap auto-captures all user interactions without requiring manual event instrumentation. BAA available, but 'capture everything' approach requires careful redaction configuration on healthcare sites.",
        "domains": ["heapanalytics.com", "cdn.heapanalytics.com"],
        "inline_fingerprints": ["heap.load(", "heap.identify(", "heap.track(", "window.heap"],
    },

    "mixpanel": {
        "name": "Mixpanel",
        "company": "Mixpanel Inc.",
        "risk_level": "medium",
        "baa_available": True,
        "baa_notes": "Mixpanel offers HIPAA BAAs under enterprise agreements. Requires proper configuration to suppress PHI from event properties.",
        "phi_capture": [
            "Custom event properties (if PHI passed by developer)",
            "User identification data",
            "IP address (can be disabled)",
            "Behavioral event sequences",
        ],
        "regulatory_mentions": [
            "HHS OCR guidance on analytics platforms handling PHI",
        ],
        "description": "Mixpanel is an event-based analytics platform. BAA available, but PHI in event properties depends entirely on implementation. Risk varies significantly by configuration.",
        "domains": ["mixpanel.com", "cdn.mxpnl.com", "api.mixpanel.com"],
        "inline_fingerprints": ["mixpanel.init(", "mixpanel.track(", "mixpanel.identify("],
    },

    "amplitude": {
        "name": "Amplitude",
        "company": "Amplitude Inc.",
        "risk_level": "medium",
        "baa_available": True,
        "baa_notes": "Amplitude offers HIPAA BAAs under Growth and Enterprise plans. Requires configuration to exclude PHI from event properties and user data.",
        "phi_capture": [
            "Event properties (if PHI passed by developer)",
            "User properties",
            "IP address (configurable)",
            "Session replay (newer feature — may capture form data)",
        ],
        "regulatory_mentions": [
            "HHS OCR guidance on product analytics platforms",
        ],
        "description": "Amplitude is a product analytics platform. BAA is available and the platform is used by compliant healthcare companies, but proper configuration is required.",
        "domains": ["cdn.amplitude.com", "api.amplitude.com", "amplitude.com"],
        "inline_fingerprints": ["amplitude.init(", "amplitude.getInstance(", "amplitude.track("],
    },

    "segment": {
        "name": "Segment (Twilio)",
        "company": "Twilio Segment",
        "risk_level": "medium",
        "baa_available": True,
        "baa_notes": "Twilio Segment offers HIPAA BAAs under Business and Developer plans. However, Segment routes data to downstream destinations — each destination also needs its own BAA and compliance review.",
        "phi_capture": [
            "All tracked events and properties",
            "User identity (`.identify()` calls)",
            "Data routed to all connected destinations",
            "IP address",
        ],
        "regulatory_mentions": [
            "HHS OCR guidance on CDPs and data routing (2022-2023)",
        ],
        "description": "Segment is a Customer Data Platform that collects and routes events to hundreds of destinations. BAA available, but each downstream destination is an independent compliance risk.",
        "domains": ["cdn.segment.com", "api.segment.io", "cdn.segment.io"],
        "inline_fingerprints": ["analytics.load(", "analytics.identify(", "analytics.track(", "cdn.segment"],
    },

    "hubspot": {
        "name": "HubSpot Tracking",
        "company": "HubSpot Inc.",
        "risk_level": "high",
        "baa_available": False,
        "baa_notes": "HubSpot explicitly states it is not a HIPAA Business Associate and does not sign BAAs for its marketing and CRM tools. HubSpot's website clearly states healthcare companies should not store PHI in HubSpot.",
        "phi_capture": [
            "Contact behavioral tracking across web sessions",
            "Form submissions (including health inquiry forms)",
            "Email engagement tracking",
            "CRM contact data enrichment",
            "Chat and support conversation data",
        ],
        "regulatory_mentions": [
            "HHS OCR guidance on CRM and marketing automation platforms",
            "HubSpot's own documentation acknowledges it is not HIPAA-compliant",
        ],
        "description": "HubSpot tracks website visitors, links behavior to CRM contacts, and captures form submissions. HubSpot publicly states it is not a HIPAA Business Associate — healthcare use is high risk.",
        "domains": ["js.hs-scripts.com", "js.hsforms.net", "hs-banner.com", "hubspot.com", "hsappstatic.net"],
        "inline_fingerprints": ["_hsq.push(", "HubSpotConversations", "hbspt.forms", "hsCtaTracking"],
    },

    "intercom": {
        "name": "Intercom",
        "company": "Intercom Inc.",
        "risk_level": "medium",
        "baa_available": False,
        "baa_notes": "Intercom does not offer HIPAA BAAs as a standard product. Healthcare customers are advised not to collect PHI in Intercom. No standard compliant path exists.",
        "phi_capture": [
            "Chat conversation content (may include symptoms, diagnoses)",
            "User identity and behavioral data",
            "Email and contact information",
            "Support ticket content",
        ],
        "regulatory_mentions": [
            "HHS OCR guidance on customer support and chat tools",
        ],
        "description": "Intercom provides customer messaging and support chat. Chat conversations on healthcare sites routinely contain PHI (symptoms, appointment details, billing info) with no compliant storage path.",
        "domains": ["widget.intercom.io", "js.intercomcdn.com", "api.intercom.io"],
        "inline_fingerprints": ["intercomSettings", "Intercom(", "Intercom('boot'"],
    },

    "adobe_analytics": {
        "name": "Adobe Analytics",
        "company": "Adobe Inc.",
        "risk_level": "medium",
        "baa_available": True,
        "baa_notes": "Adobe offers HIPAA BAAs under enterprise agreements. Adobe Experience Cloud has a formal HIPAA compliance program. Configuration and data governance setup required.",
        "phi_capture": [
            "Full analytics event stream",
            "eVar and prop data (if PHI included by developer)",
            "Visitor ID and cross-session tracking",
            "Integration with Adobe Audience Manager (may share PHI)",
        ],
        "regulatory_mentions": [
            "HHS OCR guidance on enterprise analytics suites",
        ],
        "description": "Adobe Analytics is used by many large health systems. BAA available, but implementation complexity means PHI leakage is common in practice.",
        "domains": ["omtrdc.net", "adobedtm.com", "demdex.net", "2o7.net", "omniture.com"],
        "inline_fingerprints": ["s.t()", "AppMeasurement", "adobeDataLayer", "omniture"],
    },

    "marketo": {
        "name": "Marketo Munchkin",
        "company": "Adobe Inc. (Marketo)",
        "risk_level": "medium",
        "baa_available": True,
        "baa_notes": "Marketo/Adobe offers BAAs under enterprise agreements. Munchkin tracking script links web behavior to Marketo lead records — requires careful data governance.",
        "phi_capture": [
            "Web visit history linked to known lead records",
            "Form submissions captured in Marketo",
            "Email engagement tracking",
            "Lead scoring based on health content engagement",
        ],
        "regulatory_mentions": [
            "HHS OCR guidance on marketing automation and lead tracking",
        ],
        "description": "Marketo Munchkin links healthcare website visits to CRM lead records. Engagement with health condition pages can create PHI-like records in Marketo's database.",
        "domains": ["munchkin.marketo.net", "marketo.net", "mktocdn.com"],
        "inline_fingerprints": ["Munchkin.init(", "mkto_resp", "munchkin"],
    },

    "google_ads": {
        "name": "Google Ads Remarketing",
        "company": "Google LLC",
        "risk_level": "high",
        "baa_available": True,
        "baa_notes": "BAA theoretically available via Google Cloud DPA, but Google Ads remarketing audiences built from healthcare site visits are specifically prohibited by Google's own healthcare advertising policies AND by HHS OCR guidance.",
        "phi_capture": [
            "Remarketing audience lists (users who visited specific health pages)",
            "Conversion events",
            "Custom intent audiences",
            "Similar audiences built from health site visitors",
        ],
        "regulatory_mentions": [
            "HHS OCR Bulletin — December 2022 (Google tracking named)",
            "Google's own Sensitive Categories advertising policy prohibits health condition targeting",
            "FTC complaints involving healthcare remarketing",
        ],
        "description": "Google Ads conversion and remarketing tags create audiences from healthcare site visitors — a practice HHS OCR has flagged as likely PHI disclosure, regardless of BAA status.",
        "domains": ["googleadservices.com", "googlesyndication.com", "g.doubleclick.net"],
        "inline_fingerprints": ["gtag('config', 'AW-", "google_conversion", "google_remarketing_only"],
    },

    "criteo": {
        "name": "Criteo",
        "company": "Criteo SA",
        "risk_level": "high",
        "baa_available": False,
        "baa_notes": "Criteo does not offer HIPAA BAAs. Criteo's retargeting technology builds behavioral profiles across the web and is incompatible with healthcare privacy requirements.",
        "phi_capture": [
            "Cross-site behavioral profile",
            "Product/service interest data (health conditions inferred)",
            "Hashed email for identity matching",
            "IP address and device fingerprint",
        ],
        "regulatory_mentions": [
            "HHS OCR guidance on cross-site tracking and retargeting",
            "CNIL enforcement action vs. Criteo (France, €40M fine, 2023)",
        ],
        "description": "Criteo is a retargeting platform that tracks users across thousands of websites. No healthcare-compliant option exists. CNIL's 2023 €40M fine signals increasing regulatory pressure.",
        "domains": ["static.criteo.net", "cat.fr.criteo.com", "dis.criteo.com"],
        "inline_fingerprints": ["criteo", "Criteo.DisplayAd", "window.criteo_q"],
    },
}


RISK_COLORS = {
    "critical": "#FF2D55",
    "high": "#FF8C00",
    "medium": "#FFD60A",
    "low": "#00E676",
    "clean": "#00FFB2",
}

RISK_LABELS = {
    "critical": "CRITICAL",
    "high": "HIGH",
    "medium": "MEDIUM",
    "low": "LOW",
    "clean": "CLEAN",
}

RISK_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3, "clean": 4}


def compute_overall_risk(findings: list) -> str:
    if not findings:
        return "clean"
    levels = [f["risk_level"] for f in findings]
    return sorted(levels, key=lambda x: RISK_ORDER.get(x, 99))[0]
