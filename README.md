# ResearchPoC

Executable proof-of-concept for a geopolitical risk + supply-chain GenAI copilot. It uses synthetic WMS/TMS data to simulate a US trade block on China and recommends alternate sourcing.

## What this demo includes
- Geopolitical news ingest (synthetic)
- Trade-block risk alerts for China-origin shipments
- Alternate sourcing recommendations (Vietnam, Mexico, India, Malaysia)
- WMS/TMS Q&A for delays, supplier performance, and lead times (RAG over synthetic data)
- Dashboard UI

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Then open `http://localhost:8000`.

## Data sources
Synthetic data lives in `data/` and is safe to modify for new scenarios.
