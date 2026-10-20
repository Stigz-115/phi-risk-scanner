# PHI Risk Scanner — Freshpaint pre-sales toolkit

Streamlit app (`streamlit run app.py`; on Streamlit Cloud the main file is `app.py`) with five tools:

| Page | What it does |
|---|---|
| PHI Risk Scanner (`pages/1_PHI_Risk_Scanner.py`) | Scans a healthcare site for third-party trackers and PHI risk |
| ROI Calculator | Cost of "going dark" vs. Freshpaint |
| Stakeholder Deck Builder | Persona briefs (Executive, CMO, CFO, GC/CCO, Privacy/CISO, CTO) as PDFs and a PowerPoint deck; optionally cites trackers found on the prospect's site |
| State Privacy Scorecard | 50 states + DC scored on health-data / tracking exposure |
| Competitive Comparison | Freshpaint vs. GA4, Segment, mParticle, OneTrust, GTM server-side, Heap/Mixpanel, Ours Privacy, Piwik PRO |

## Where the facts live

- `scanner/data/state_laws.json` — state laws (single source for the scorecard **and** the decks)
- `scanner/regulatory.py` — federal guidance status, HIPAA penalty amounts, enforcement cases
- `scanner/competitors.py` — competitor scores, objections and counters

## Keeping state law current

A GitHub Action checks LegiScan on the 1st of every month and opens a review PR.
Setup and reviewer steps: [docs/LEGISLATION_UPDATES.md](docs/LEGISLATION_UPDATES.md).

## Deck builder internals

`scanner/deck_content.py` defines what each brief says as format-neutral blocks;
`scanner/deck_pdf.py` (fpdf2) and `scanner/deck_pptx.py` (python-pptx) render it.
Edit copy in one place and both outputs change.
