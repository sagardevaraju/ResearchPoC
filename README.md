# ResearchPoC

Executable proof-of-concept for a geopolitical risk + supply-chain GenAI copilot. It uses synthetic WMS/TMS data to simulate a US trade block on China and recommends alternate sourcing.

## What this demo includes
- **Live Geopolitical News Scraping** - Real-time news from UN, BBC, Reuters RSS feeds
- **Severity Score Calculation** - Mathematical formulation for shipment impact assessment
- Trade-block risk alerts for China-origin shipments with impact scores
- Alternate sourcing recommendations (Vietnam, Mexico, India, Malaysia)
- WMS/TMS Q&A for delays, supplier performance, and lead times (RAG over synthetic data)
- **Enhanced Security** - CSRF protection, input validation, security headers
- Dashboard UI with live news refresh capability

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Then open `http://localhost:8000`.

## New Features

### 1. Live Geopolitical News Scraping
Click the "Refresh Live News" button in the dashboard to fetch real-time geopolitical news from:
- UN News (Trade)
- BBC World News
- Reuters World News

News articles are automatically analyzed for geopolitical risk keywords and severity.

### 2. Shipment Impact Severity Score
Each risk alert now includes a calculated impact score (0-1) based on:
- **Geopolitical Severity** (40% weight)
- **Delay Factor** (30% weight)
- **Supplier Performance** (20% weight)
- **Route Risk** (10% weight)

See [SEVERITY_SCORE.md](SEVERITY_SCORE.md) for detailed mathematical formulation.

### 3. Security Improvements
- CSRF protection on all forms
- Input validation (max 500 chars)
- Security headers (X-Frame-Options, CSP, etc.)
- Debug mode disabled by default
- Secret key management via environment variables

See [SECURITY_IMPROVEMENTS.md](SECURITY_IMPROVEMENTS.md) for complete security documentation.

## Environment Variables

Create a `.env` file:
```bash
SECRET_KEY=<your-secret-key>
FLASK_DEBUG=False
LOCAL_LLM_BASE_URL=http://127.0.0.1:8085
LOCAL_LLM_MODEL=mistral
LOCAL_LLM_TIMEOUT=20
```

Generate a secret key:
```bash
python -c "import os; print(os.urandom(32).hex())"
```

## Data sources
Synthetic data lives in `data/` and is safe to modify for new scenarios.

## Production Deployment

For production deployment:
1. Use a production WSGI server (gunicorn)
2. Set up HTTPS with nginx reverse proxy
3. Configure firewall and rate limiting
4. See [SECURITY_IMPROVEMENTS.md](SECURITY_IMPROVEMENTS.md) for detailed checklist
