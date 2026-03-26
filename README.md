# EcomAgent

> **AI-powered e-commerce automation platform. Open-source, self-hosted, bring your own LLM key.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.12-blue)](https://www.python.org)
[![React](https://img.shields.io/badge/react-19-blue)](https://react.dev)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)](https://fastapi.tiangolo.com)

EcomAgent automates the full Amazon FBA/FBM seller workflow — from product research to listing creation to competitor monitoring to ad optimization — in a single self-hosted platform. No subscriptions. No data sent to third parties.

## Why EcomAgent?

| | SaaS tools (Jungle Scout, Helium 10…) | **EcomAgent** |
|---|---|---|
| Price | $99–$499/month | **Free, open-source** |
| Data ownership | Stored on their servers | **Stays on your machine** |
| LLM | Locked-in black box | **Bring your own key** (OpenAI / Claude / Gemini / Ollama) |
| Platform support | Fixed | **Pluggable adapters** |
| Extensibility | None | **Fork & build** |

## Features

### AI Product Research
- Scrape Amazon Best Sellers / Movers & Shakers across 10+ categories
- LLM scoring on 3 dimensions: competition, profit potential, trend
- Filter by minimum overall score to surface the best opportunities
- Export results to CSV

### Listing Generator
- Input a keyword or ASIN — get a complete listing in seconds
- Generates: title, 5 bullet points, description, backend search terms, A+ content draft
- Character count validation against Amazon limits
- 6 language markets: EN / DE / FR / ES / IT / JP

### Review Analyzer
- Scrape all reviews for any ASIN (configurable page depth)
- LLM extracts: top pain points, praise points, improvement suggestions
- Keyword cloud with sentiment tagging
- Listing optimization recommendations derived from review insights

### Competitor Monitor
- Add any ASIN for periodic tracking (price, BSR rank, review count, stock)
- Configurable alert rules: price drop %, BSR shift %, review spike
- Automatic hourly snapshots via Celery Beat
- Price and BSR trend charts in the dashboard

### Ad Optimizer
- Connect Amazon Advertising API to pull campaign performance
- AI analysis of ACoS / ROAS / CTR per keyword
- Keyword bid recommendations (raise / lower / pause / negate)
- Budget reallocation suggestions with estimated monthly savings

## Architecture

```
┌─────────────┐      HTTP       ┌──────────────────────────────────────┐
│  React SPA  │ ◄────────────► │  FastAPI backend                     │
│ (Vite + TS) │                 │  ├── Platform Adapters (pluggable)   │
└─────────────┘                 │  │   ├── Amazon (SP-API + Playwright) │
                                │  │   └── Shopify (stub)              │
                                │  ├── AI Layer (LLM abstraction)      │
                                │  │   ├── OpenAI / Claude / Gemini    │
                                │  │   └── Ollama (local)              │
                                │  └── Modules                         │
                                │      ├── product_research            │
                                │      ├── listing_generator           │
                                │      ├── review_analyzer             │
                                │      ├── competitor_monitor          │
                                │      └── ad_optimizer                │
                                └─────────────┬────────────────────────┘
                                              │
                               ┌──────────────▼──────────────┐
                               │  Celery workers + Beat      │
                               │  (periodic monitor tasks)   │
                               └──────────┬──────────────────┘
                                          │
                          ┌───────────────▼───────────────┐
                          │  PostgreSQL    Redis           │
                          └───────────────────────────────┘
```

## Quick Start

### Prerequisites
- Docker + Docker Compose
- An LLM API key (OpenAI, Anthropic, Gemini) **or** Ollama running locally

### 1. Clone & configure

```bash
git clone https://github.com/your-username/ecom-agent
cd ecom-agent
cp .env.example .env
```

Edit `.env` and fill in at minimum:

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
```

### 2. Start all services

```bash
docker compose up -d
```

Services started:
- `http://localhost:3000` — Frontend UI
- `http://localhost:8000` — Backend API
- `http://localhost:8000/docs` — Swagger UI

### 3. Open the dashboard

Visit `http://localhost:3000` and start researching products.

## Configuration

All configuration lives in `.env`. See [`.env.example`](.env.example) for all options.

### LLM Providers

```env
LLM_PROVIDER=openai          # openai | anthropic | gemini | ollama
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o
```

### Amazon SP-API (optional — required for listing creation)

Apply for credentials at the [Amazon Selling Partner API developer portal](https://developer-docs.amazon.com/sp-api/).

```env
AMAZON_CLIENT_ID=amzn1.application-oa2-client...
AMAZON_CLIENT_SECRET=...
AMAZON_REFRESH_TOKEN=...
AMAZON_MARKETPLACE_ID=ATVPDKIKX0DER
```

### Amazon Advertising API (optional — required for Ad Optimizer)

Requires separate approval at [Amazon Advertising API](https://advertising.amazon.com/API/).

## Development

```bash
# Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

## Testing

EcomAgent uses a three-layer testing strategy. All layers must pass before any PR merges.

### Layer 1 — Unit + Integration

Core logic, data models, API endpoint contracts. No network calls.

```bash
cd backend
pytest tests/test_core.py -v
```

### Layer 2 — User-side Acceptance Tests

Validates what the user actually sees: correct response shapes, business rules (e.g. recommended products must score ≥ 6.0). LLM and scrapers are mocked.

```bash
cd backend
pytest tests/acceptance/ -v
```

### Layer 3 — Model Quality Evaluation

Checks that LLM output meets quality rules: bullet format, score-recommendation consistency, ACoS/ROAS logic. Runs against pre-defined mock outputs — no API calls needed.

```bash
cd backend
pytest tests/eval/ -v
```

### Run everything at once

```bash
cd backend
pytest tests/ -v        # excludes real_llm tests (CI-safe)
```

### Frontend tests

```bash
cd frontend
npm run test:run         # single pass
npm run test             # watch mode
```

### Real LLM tests (local dev only)

For end-to-end quality validation with a live model. Requires an OpenAI-compatible API key.

```bash
cp backend/.env.dev.example backend/.env.dev
# Edit .env.dev: set OPENAI_API_KEY and OPENAI_BASE_URL
source backend/.env.dev && pytest tests/real_llm/ -v -m real_llm -s
```

These tests are excluded from CI automatically (`pytest.ini` adds `-m "not real_llm"`).

## Adding a New Platform Adapter

1. Create `backend/app/adapters/my_platform/`
2. Implement `BasePlatformAdapter` from `app/adapters/base.py`
3. Register it in `app/adapters/__init__.py`

All 5 modules will automatically use the new platform.

## API Documentation

Full OpenAPI spec available at `http://localhost:8000/docs` when running.

Key endpoints:

| Endpoint | Method | Description |
|---|---|---|
| `/api/v1/product-research/research` | POST | Run category research |
| `/api/v1/product-research/score/{asin}` | GET | Score a single ASIN |
| `/api/v1/listing/generate` | POST | Generate listing from keyword |
| `/api/v1/listing/optimize` | POST | Optimize existing ASIN listing |
| `/api/v1/reviews/analyze` | POST | Analyze reviews for an ASIN |
| `/api/v1/monitor/add` | POST | Add ASIN to monitor |
| `/api/v1/monitor/snapshots/{asin}` | GET | Get snapshot history |
| `/api/v1/ads/optimize` | POST | Run ad optimization |

## Roadmap

- [ ] Shopify adapter
- [ ] eBay adapter
- [ ] TEMU adapter
- [ ] Supply chain sourcing (Alibaba / 1688 when API available)
- [ ] Multi-user support with per-user API key management
- [ ] Webhook alerts (Slack, email, Discord)
- [ ] CSV export for all modules

## Contributing

Contributions welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT — see [LICENSE](LICENSE).
