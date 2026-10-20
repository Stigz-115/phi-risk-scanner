#!/usr/bin/env python3
"""
Monthly legislation watch.

Searches LegiScan for state bills relevant to health-data privacy and pixel
tracking, compares them with the previous run, and writes:

  * scanner/data/legislation_watch.json  — machine-readable snapshot (shown in the app)
  * a Markdown report (path given by --report) — used as the PR body

It never edits scanner/data/state_laws.json. A human reviews the PR, updates
state_laws.json where a bill has actually changed the law, and bumps
_meta.last_reviewed. See docs/LEGISLATION_UPDATES.md.

Usage:
    LEGISCAN_API_KEY=... python scripts/check_legislation.py --report report.md
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
WATCH_PATH = ROOT / "scanner" / "data" / "legislation_watch.json"
STATE_LAWS_PATH = ROOT / "scanner" / "data" / "state_laws.json"

API = "https://api.legiscan.com/"

# Searches run against all states, current session. Keep this list short:
# each query costs 1 API call per page of 50 results.
QUERIES = [
    '"consumer health data"',
    '"health data" AND privacy',
    '"consumer data privacy"',
    '"personal data" AND controller AND processor',
    'geofence OR geofencing',
    '"tracking technology" OR pixel',
    '"reproductive health" AND data',
    '"sensitive data" AND sale',
    '"precise geolocation" AND sale',
]
MAX_PAGES_PER_QUERY = 3
MIN_RELEVANCE = 60          # LegiScan relevance score, 0-100
MAX_DETAIL_CALLS = 150      # cap getBill calls per run (free tier is ample)

STATUS = {0: "Pre-filed", 1: "Introduced", 2: "Passed one chamber", 3: "Enrolled",
          4: "Passed / Signed", 5: "Vetoed", 6: "Failed"}
HIGH_PRIORITY_STATUS = {3, 4, 5}


class LegiScanError(RuntimeError):
    pass


def call(op: str, key: str, **params) -> dict:
    params = {"key": key, "op": op, **params}
    for attempt in range(3):
        try:
            r = requests.get(API, params=params, timeout=30)
            r.raise_for_status()
            data = r.json()
        except (requests.RequestException, ValueError) as e:
            if attempt == 2:
                raise LegiScanError(f"{op} failed: {e}") from e
            time.sleep(2 * (attempt + 1))
            continue
        if data.get("status") != "OK":
            msg = (data.get("alert") or {}).get("message", "unknown error")
            raise LegiScanError(f"{op} returned error: {msg}")
        time.sleep(0.7)   # stay well under the 100-calls/minute guidance
        return data
    raise LegiScanError(f"{op} failed")


def search_all(key: str) -> dict[int, dict]:
    """bill_id -> search hit (title, state, number, change_hash, last action...)."""
    hits: dict[int, dict] = {}
    for q in QUERIES:
        for page in range(1, MAX_PAGES_PER_QUERY + 1):
            res = call("getSearch", key, state="ALL", year=2, query=q, page=page)["searchresult"]
            summary = res.get("summary", {})
            rows = [v for k, v in res.items() if k != "summary"]
            for row in rows:
                if int(row.get("relevance", 0)) < MIN_RELEVANCE:
                    continue
                bid = int(row["bill_id"])
                prev = hits.get(bid)
                if prev:
                    prev["queries"].append(q)
                    continue
                hits[bid] = {
                    "bill_id": bid,
                    "state": row.get("state"),
                    "number": row.get("bill_number"),
                    "title": row.get("title", "").strip(),
                    "change_hash": row.get("change_hash"),
                    "last_action": row.get("last_action", ""),
                    "last_action_date": row.get("last_action_date", ""),
                    "url": row.get("url", ""),
                    "relevance": int(row.get("relevance", 0)),
                    "queries": [q],
                }
            if page >= int(summary.get("page_total", 1) or 1):
                break
    return hits


def enrich(key: str, bill: dict) -> dict:
    b = call("getBill", key, id=bill["bill_id"])["bill"]
    status = int(b.get("status", 0) or 0)
    bill.update({
        "status": status,
        "status_label": STATUS.get(status, str(status)),
        "status_date": b.get("status_date", ""),
        "session": (b.get("session") or {}).get("session_name", ""),
        "url": b.get("state_link") or bill.get("url", ""),
        "legiscan_url": b.get("url", bill.get("url", "")),
    })
    return bill


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def priority(bill: dict, state_laws: dict) -> tuple:
    current = state_laws.get(bill["state"], {}).get("status", "none")
    new_law_signal = bill.get("status") in (3, 4) and current in ("none", "pending")
    return (
        0 if new_law_signal else 1,
        0 if bill.get("status") in HIGH_PRIORITY_STATUS else 1,
        -bill.get("relevance", 0),
    )


def render_report(changed: list[dict], removed: int, total: int, state_laws: dict,
                  last_reviewed: str, run_date: str) -> str:
    lines = [
        f"## Monthly legislation watch — {run_date}",
        "",
        f"Tracking **{total}** relevant bills across all states. "
        f"**{len(changed)}** are new or changed since the last run"
        + (f"; {removed} dropped out of search results." if removed else "."),
        f"State law data was last reviewed **{last_reviewed}**.",
        "",
        "### Reviewer checklist",
        "- [ ] Read every bill marked **Action** below",
        "- [ ] Update `scanner/data/state_laws.json` for bills that changed the law "
        "(status, effective date, scores, penalty, summary, sources)",
        "- [ ] Bump `_meta.last_reviewed` in `scanner/data/state_laws.json` to today, even if nothing changed",
        "- [ ] `python scripts/validate_state_data.py` passes",
        "",
    ]
    if not changed:
        lines += ["_No tracked bill moved this month._", ""]
        return "\n".join(lines)

    lines += ["| | State | Bill | Status | Last action | Title |",
              "|---|---|---|---|---|---|"]
    for b in changed:
        current = state_laws.get(b["state"], {}).get("status", "none")
        flag = ""
        if b.get("status") in (3, 4) and current in ("none", "pending"):
            flag = "**Action: possible new law**"
        elif b.get("status") in HIGH_PRIORITY_STATUS:
            flag = "**Action**"
        title = b["title"].replace("|", "/")
        if len(title) > 90:
            title = title[:87] + "..."
        action = f"{b.get('last_action_date', '')}: {b.get('last_action', '')}".replace("|", "/")
        lines.append(
            f"| {flag} | {b['state']} | [{str(b['number']).replace('|', '/')}]({b.get('legiscan_url') or b.get('url')}) "
            f"| {b.get('status_label', '')} | {action} | {title} |"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", default="legislation_report.md", help="Markdown report output path")
    args = ap.parse_args()

    key = os.environ.get("LEGISCAN_API_KEY", "").strip()
    if not key:
        print("LEGISCAN_API_KEY is not set. Add it as a repository secret.", file=sys.stderr)
        return 2

    state_file = load_json(STATE_LAWS_PATH)
    state_laws = state_file.get("states", {})
    last_reviewed = state_file.get("_meta", {}).get("last_reviewed", "unknown")
    previous = load_json(WATCH_PATH).get("bills", {})

    hits = search_all(key)
    changed: list[dict] = []
    detail_calls = 0
    for bid, hit in hits.items():
        prev = previous.get(str(bid))
        if prev and prev.get("change_hash") == hit["change_hash"]:
            # unchanged: carry forward the detail we already have
            hit.update({k: prev[k] for k in ("status", "status_label", "status_date", "session", "legiscan_url")
                        if k in prev})
            continue
        if detail_calls < MAX_DETAIL_CALLS:
            enrich(key, hit)
            detail_calls += 1
        changed.append(hit)

    changed.sort(key=lambda b: priority(b, state_laws))
    removed = len(set(previous) - {str(b) for b in hits})
    now = datetime.now(timezone.utc)

    snapshot = {
        "generated_at": now.isoformat(timespec="seconds"),
        "source": "LegiScan API (getSearch / getBill)",
        "queries": QUERIES,
        "total_tracked": len(hits),
        "changed": changed,
        "bills": {str(k): v for k, v in sorted(hits.items())},
    }
    WATCH_PATH.write_text(json.dumps(snapshot, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")

    report = render_report(changed, removed, len(hits), state_laws, last_reviewed, now.strftime("%B %Y"))
    Path(args.report).write_text(report, encoding="utf-8")
    print(f"Tracked {len(hits)} bills; {len(changed)} new/changed; {detail_calls} detail calls.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except LegiScanError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
