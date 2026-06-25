"""
Page scanner — fetches a URL and detects known tracking technologies.
Uses static HTML analysis: script src domains + inline fingerprints.
Does not execute JavaScript; dynamic trackers loaded after page load
may not be detected.
"""

import time
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

try:
    import tldextract
    _HAS_TLDEXTRACT = True
except ImportError:
    _HAS_TLDEXTRACT = False

from scanner.registry import TRACKER_REGISTRY, compute_overall_risk

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;"
        "q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
    "Sec-Ch-Ua": '"Chromium";v="125", "Google Chrome";v="125", "Not-A.Brand";v="99"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"macOS"',
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "DNT": "1",
}

GTM_ID_RE = re.compile(r"GTM-[A-Z0-9]+")
GA4_ID_RE = re.compile(r"G-[A-Z0-9]+")
AW_ID_RE  = re.compile(r"AW-[0-9]+")


@dataclass
class TrackerFinding:
    tracker_id: str
    name: str
    company: str
    risk_level: str
    baa_available: bool
    baa_notes: str
    phi_capture: list
    regulatory_mentions: list
    description: str
    detected_via: str        # "script_src" | "inline_fingerprint" | "pixel_img"
    detected_snippet: str    # the URL or inline fragment that triggered detection


@dataclass
class ScanResult:
    url: str
    canonical_url: str
    scan_timestamp: str
    duration_seconds: float
    findings: list = field(default_factory=list)
    overall_risk: str = "clean"
    gtm_container_ids: list = field(default_factory=list)
    ga4_ids: list = field(default_factory=list)
    total_external_scripts: int = 0
    total_inline_scripts: int = 0
    error: str = None
    status_code: int = None


def _extract_registered_domain(url: str) -> str:
    """Return the registered domain (e.g., 'connect.facebook.net')."""
    if _HAS_TLDEXTRACT:
        ext = tldextract.extract(url)
        if ext.domain and ext.suffix:
            return f"{ext.domain}.{ext.suffix}"
    parsed = urlparse(url)
    host = parsed.netloc or parsed.path
    parts = host.split(".")
    return ".".join(parts[-2:]) if len(parts) >= 2 else host


def _full_domain(url: str) -> str:
    """Return the full hostname."""
    parsed = urlparse(url)
    return parsed.netloc.lower()


def _url_matches_tracker(url: str, tracker: dict) -> bool:
    url_lower = url.lower()
    for domain in tracker.get("domains", []):
        if domain.lower() in url_lower:
            return True
    return False


def _inline_matches_tracker(text: str, tracker: dict) -> str | None:
    for fp in tracker.get("inline_fingerprints", []):
        if fp in text:
            return fp
    return None


def _normalize_url(url: str) -> str:
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url


def scan_url(url: str, timeout: int = 12) -> ScanResult:
    url = _normalize_url(url)
    start = time.time()
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    result = ScanResult(url=url, canonical_url=url, scan_timestamp=timestamp, duration_seconds=0)

    # ── Fetch the page ──────────────────────────────────────────────────────
    session = requests.Session()
    session.headers.update(_HEADERS)

    try:
        resp = session.get(
            url,
            timeout=timeout,
            allow_redirects=True,
            verify=True,
        )
        result.canonical_url = resp.url
        result.status_code = resp.status_code

        if resp.status_code == 403:
            # Retry once without Sec-* headers (some WAFs reject them from non-browsers)
            stripped = {k: v for k, v in _HEADERS.items() if not k.startswith("Sec-")}
            resp2 = session.get(url, headers=stripped, timeout=timeout, allow_redirects=True, verify=True)
            if resp2.status_code < 400:
                resp = resp2
                result.status_code = resp.status_code
            else:
                result.error = (
                    "HTTP 403 — the server is blocking automated requests (Cloudflare or WAF). "
                    "Try a different page on the same domain (e.g. /about or /services) "
                    "or check a page that doesn't sit behind bot protection."
                )
                result.duration_seconds = round(time.time() - start, 2)
                return result

        elif resp.status_code >= 400:
            result.error = (
                f"Server returned HTTP {resp.status_code}. "
                "The page may require authentication or be unavailable."
            )
            result.duration_seconds = round(time.time() - start, 2)
            return result

        content_type = resp.headers.get("Content-Type", "")
        if "html" not in content_type.lower():
            result.error = (
                f"URL returned non-HTML content ({content_type}). "
                "Please enter a standard web page URL."
            )
            result.duration_seconds = round(time.time() - start, 2)
            return result

        html = resp.text

    except requests.exceptions.SSLError:
        result.error = "SSL certificate error. Try the http:// version of the URL."
        result.duration_seconds = round(time.time() - start, 2)
        return result
    except requests.exceptions.ConnectionError:
        result.error = "Could not connect to the server. Check that the URL is correct and publicly accessible."
        result.duration_seconds = round(time.time() - start, 2)
        return result
    except requests.exceptions.Timeout:
        result.error = f"The server did not respond within {timeout} seconds."
        result.duration_seconds = round(time.time() - start, 2)
        return result
    except Exception as e:
        result.error = f"Scan error: {str(e)}"
        result.duration_seconds = round(time.time() - start, 2)
        return result
    finally:
        session.close()

    # ── Parse HTML ──────────────────────────────────────────────────────────
    try:
        soup = BeautifulSoup(html, "lxml")
    except Exception:
        soup = BeautifulSoup(html, "html.parser")

    detected_tracker_ids: set = set()
    findings: list[TrackerFinding] = []

    # ── Pass 1: External script src tags ────────────────────────────────────
    script_tags = soup.find_all("script", src=True)
    result.total_external_scripts = len(script_tags)

    for tag in script_tags:
        src = tag.get("src", "")
        if not src:
            continue
        for tid, tracker in TRACKER_REGISTRY.items():
            if tid in detected_tracker_ids:
                continue
            if _url_matches_tracker(src, tracker):
                findings.append(
                    TrackerFinding(
                        tracker_id=tid,
                        name=tracker["name"],
                        company=tracker["company"],
                        risk_level=tracker["risk_level"],
                        baa_available=tracker["baa_available"],
                        baa_notes=tracker["baa_notes"],
                        phi_capture=tracker["phi_capture"],
                        regulatory_mentions=tracker["regulatory_mentions"],
                        description=tracker["description"],
                        detected_via="script_src",
                        detected_snippet=src[:120],
                    )
                )
                detected_tracker_ids.add(tid)

    # ── Pass 2: Inline script content ───────────────────────────────────────
    inline_scripts = soup.find_all("script", src=False)
    result.total_inline_scripts = len(inline_scripts)

    all_inline = " ".join(tag.get_text() for tag in inline_scripts)

    # Extract GTM container IDs
    result.gtm_container_ids = list(set(GTM_ID_RE.findall(all_inline)))
    result.ga4_ids = list(set(GA4_ID_RE.findall(all_inline) + AW_ID_RE.findall(all_inline)))

    for tid, tracker in TRACKER_REGISTRY.items():
        if tid in detected_tracker_ids:
            continue
        match = _inline_matches_tracker(all_inline, tracker)
        if match:
            findings.append(
                TrackerFinding(
                    tracker_id=tid,
                    name=tracker["name"],
                    company=tracker["company"],
                    risk_level=tracker["risk_level"],
                    baa_available=tracker["baa_available"],
                    baa_notes=tracker["baa_notes"],
                    phi_capture=tracker["phi_capture"],
                    regulatory_mentions=tracker["regulatory_mentions"],
                    description=tracker["description"],
                    detected_via="inline_fingerprint",
                    detected_snippet=f'Inline script contains: "{match}"',
                )
            )
            detected_tracker_ids.add(tid)

    # ── Pass 3: Tracking pixels (1×1 img tags) ──────────────────────────────
    img_tags = soup.find_all("img")
    for tag in img_tags:
        src = tag.get("src", "")
        if not src:
            continue
        for tid, tracker in TRACKER_REGISTRY.items():
            if tid in detected_tracker_ids:
                continue
            if _url_matches_tracker(src, tracker):
                findings.append(
                    TrackerFinding(
                        tracker_id=tid,
                        name=tracker["name"],
                        company=tracker["company"],
                        risk_level=tracker["risk_level"],
                        baa_available=tracker["baa_available"],
                        baa_notes=tracker["baa_notes"],
                        phi_capture=tracker["phi_capture"],
                        regulatory_mentions=tracker["regulatory_mentions"],
                        description=tracker["description"],
                        detected_via="pixel_img",
                        detected_snippet=src[:120],
                    )
                )
                detected_tracker_ids.add(tid)

    # ── Pass 4: noscript blocks (GTM noscript iframe) ───────────────────────
    noscript_content = " ".join(
        tag.get_text() + str(tag) for tag in soup.find_all("noscript")
    )
    for tid, tracker in TRACKER_REGISTRY.items():
        if tid in detected_tracker_ids:
            continue
        if _url_matches_tracker(noscript_content, tracker):
            findings.append(
                TrackerFinding(
                    tracker_id=tid,
                    name=tracker["name"],
                    company=tracker["company"],
                    risk_level=tracker["risk_level"],
                    baa_available=tracker["baa_available"],
                    baa_notes=tracker["baa_notes"],
                    phi_capture=tracker["phi_capture"],
                    regulatory_mentions=tracker["regulatory_mentions"],
                    description=tracker["description"],
                    detected_via="noscript_block",
                    detected_snippet="Detected in noscript fallback block",
                )
            )
            detected_tracker_ids.add(tid)

    # ── Sort by risk severity ────────────────────────────────────────────────
    risk_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    findings.sort(key=lambda f: risk_order.get(f.risk_level, 99))

    result.findings = [vars(f) for f in findings]
    result.overall_risk = compute_overall_risk(result.findings)
    result.duration_seconds = round(time.time() - start, 2)
    return result
