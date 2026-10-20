# Keeping state privacy data current

State law data lives in one file, `scanner/data/state_laws.json`. The State Privacy
scorecard **and** the stakeholder decks (GC, Privacy Officer, Executive briefs) both
read from it, so one edit updates everything.

## How the monthly update works

1. On the 1st of every month, the **Monthly legislation watch** GitHub Action
   (`.github/workflows/legislation-watch.yml`) runs `scripts/check_legislation.py`.
2. The script searches LegiScan across all 50 states + DC for health-data, consumer-privacy,
   geofencing, pixel/tracking and sensitive-data-sale bills, and compares them with last month.
3. It opens a pull request titled *"Legislation watch: YYYY-MM state privacy review"* containing:
   - an updated `scanner/data/legislation_watch.json` (the app shows these bills in a
     "Legislation watch" panel on the State Privacy page), and
   - a table of new or changed bills, with **Action** flags on bills that were enrolled,
     signed or vetoed, and **possible new law** flags where a state we list as having no law
     (or only a pending bill) just passed one.
4. A reviewer works through the checklist in the PR:
   - update the affected state records in `state_laws.json` (status, effective date, the
     five 0-3 scores, penalty, HIPAA exemption, summary, sources);
   - bump `_meta.last_reviewed` to today, **even if nothing changed**;
   - merge. Streamlit Cloud redeploys automatically.

The app shows "review overdue" in amber when `last_reviewed` is more than 45 days old,
so a skipped month is visible to reps.

The bot never edits `state_laws.json` itself. Scores are judgment calls, and the GC brief
is read by lawyers, so a human signs off on every change.

## One-time setup

1. **LegiScan key.** Register for a free API key at <https://legiscan.com/legiscan>.
   A run uses roughly 30-200 calls, far below the free monthly allowance.
2. **Add the secret.** GitHub → repo → *Settings → Secrets and variables → Actions →
   New repository secret*: name `LEGISCAN_API_KEY`.
3. **Allow Actions to open PRs.** *Settings → Actions → General → Workflow permissions*:
   select "Read and write permissions" and tick
   "Allow GitHub Actions to create and approve pull requests".
4. **Create the label** `legislation-watch` (optional; the action creates it if missing).
5. **Test it.** *Actions → Monthly legislation watch → Run workflow*.

## Running locally

```bash
export LEGISCAN_API_KEY=...
python scripts/check_legislation.py --report report.md
python scripts/validate_state_data.py
```

## Scoring rubric (0-3 each)

| Dimension | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| health_specificity | none | general sensitive data | health data is sensitive, opt-in | standalone consumer health data law |
| private_right | none | limited | moderate (statute or wiretap claims) | broad, covers health/tracking |
| enforcement | none | new law, no actions | active AG / regulator | active + public health/tracking settlements |
| penalty_exposure | none | < $10K / violation | $10K-$50K | > $50K, per-record, or statutory damages |
| tracker_coverage | none | implied | explicit targeted ads / cookies | explicit + health inference, geofencing or sale bans |

Federal facts (HIPAA penalty amounts, OCR guidance status, enforcement cases) live in
`scanner/regulatory.py`. Review them quarterly; LegiScan does not track federal agency actions.
