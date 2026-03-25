---
name: EcomAgent
description: >
  Use this skill when you need to build an AI-powered e-commerce automation platform
  that handles the full Amazon FBA/FBM seller workflow: product research, listing generation,
  competitor monitoring, review analysis, and ad optimization. Applies to cross-border e-commerce
  projects targeting Amazon, Shopify, eBay, or other marketplaces.
version: 1.0.0
author: EcomAgent Contributors
tags: [ecommerce, amazon, fba, ai, automation, python, fastapi, react]
---

# EcomAgent Skill

## Overview

EcomAgent is an open-source AI e-commerce automation platform. This skill guides you through:

1. **Architecture decisions** for pluggable multi-platform e-commerce automation
2. **Module patterns** for the 5 core automation modules
3. **LLM integration patterns** for e-commerce use cases
4. **Amazon API integration** (SP-API + Advertising API)
5. **Scraping strategies** for Amazon data (anti-bot, rate limiting, proxies)

## Core Architecture Pattern

```
Platform Adapter (pluggable) → Business Module → LLM Layer → Response
```

Each platform (Amazon, Shopify, eBay) implements `BasePlatformAdapter` with:
- `get_product(id)` → `ProductListing`
- `search_products(keyword)` → `list[ProductListing]`
- `get_best_sellers(category)` → `list[ProductListing]`
- `get_reviews(id)` → `list[ReviewItem]`
- `create_listing(data)` → `dict`
- `get_ad_campaigns()` → `list[AdCampaign]`

## LLM Prompt Patterns for E-commerce

### Product Scoring Prompt
```
Analyze this Amazon product and score it for a new FBA seller.
Return JSON: {competition_score, profit_potential_score, trend_score, overall_score, recommended, tags, analysis}

Scoring rules:
- competition_score: BSR < 1000 = high competition (2-4). Reviews < 200 = low (7-9).
- profit_potential: Price $15-60 sweet spot = high (7-9). Consider FBA fees ~35%.
- recommended: true if overall_score >= 6.5 AND price $15-80
```

### Listing Generation Prompt
```
Create Amazon listing. Rules:
- Title: max 200 chars, primary keyword + brand + key features
- Bullet points: exactly 5, max 500 chars each, CAPS benefit label
- Description: max 2000 chars, storytelling
- Search terms: NOT in title, max 250 chars total
Return JSON: {title, bullet_points, description, search_terms, subject_matter, a_plus_draft, seo_score}
```

### Review Analysis Prompt
```
Analyze Amazon reviews. Return JSON:
{sentiment_breakdown, top_pain_points[5], top_praise_points[5],
improvement_suggestions[5], common_keywords[15], summary, listing_recommendations[5]}
```

## Key Technical Decisions

### Playwright Anti-Bot
- Randomize User-Agent from pool of real browser agents
- Add init script to hide `navigator.webdriver`
- Random sleep between actions (1.5-3s)
- Support proxy rotation via `SCRAPER_PROXY_URL`

### Amazon SP-API Auth
- LWA (Login with Amazon) OAuth flow
- Cache access token with 60s buffer before expiry
- Refresh token is long-lived, stored in `.env`

### Celery for Async Tasks
- Use `bind=True` on tasks that need retries
- `asyncio.run()` to bridge async code inside sync Celery tasks
- Store monitor configs and snapshots in Redis (no DB dependency for monitoring)

### React Query Pattern
- `useMutation` for all LLM-powered operations (they're slow, not cacheable)
- `useQuery` with `refetchInterval` for monitor list (auto-refresh)
- Error handling: show inline error messages, never crash the page

## Module Quick Reference

| Module | File | Key function |
|--------|------|-------------|
| Product Research | `modules/product_research/engine.py` | `research_category(category, limit, min_score)` |
| Listing Generator | `modules/listing_generator/generator.py` | `generate_listing(keyword, details, language)` |
| Review Analyzer | `modules/review_analyzer/analyzer.py` | `analyze_reviews(asin, max_pages)` |
| Competitor Monitor | `modules/competitor_monitor/monitor.py` | `take_snapshot(monitored_asin)` |
| Ad Optimizer | `modules/ad_optimizer/optimizer.py` | `optimize_ads(platform, target_acos)` |

## Extending EcomAgent

### Add a new platform
1. Create `backend/app/adapters/{platform}/`
2. Implement `BasePlatformAdapter`
3. Register in `app/adapters/__init__.py`

### Add a new module
1. Create `backend/app/modules/{module_name}/`
2. Add models.py (dataclasses), main logic file, `__init__.py`
3. Add FastAPI router in `backend/app/api/v1/{module}.py`
4. Register router in `backend/app/api/__init__.py`
5. Add React page in `frontend/src/pages/`
6. Register route in `frontend/src/App.tsx`
7. Add nav item in `frontend/src/components/Layout.tsx`

## Environment Variables Reference

```env
LLM_PROVIDER=openai|anthropic|gemini|ollama
DATABASE_URL=postgresql+asyncpg://...
REDIS_URL=redis://...
AMAZON_CLIENT_ID=...          # SP-API
AMAZON_REFRESH_TOKEN=...      # SP-API
AMAZON_ADS_CLIENT_ID=...      # Advertising API
SCRAPER_PROXY_URL=...         # Optional rotating proxy
SCRAPER_HEADLESS=true
```
