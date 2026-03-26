# Changelog

All notable changes to EcomAgent are documented here.

Format: [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versioning: [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.1.0] — 2026-03-26

### Added
- **Three-layer TDD infrastructure** — acceptance tests, model quality eval tests, and unit tests now required before any merge
- `tests/acceptance/test_user_scenarios.py` — 10 user-facing scenario tests covering all 5 modules (mocks both adapter and LLM layers)
- `tests/eval/test_model_quality.py` — 13 model output quality tests checking format, consistency, and business logic rules
- `tests/real_llm/test_real_llm_quality.py` — 4 real LLM tests (excluded from CI, local dev only)
- `tests/conftest.py` — shared session-scoped `client` fixture and `real_llm_provider` fixture
- `pytest.ini` — marker registration; `real_llm` tests auto-excluded in CI
- `.env.dev.example` — local dev config template for OpenAI-compatible API (no keys committed)

### Fixed
- Acceptance test patch paths: `researcher` → `engine` (module file was misnamed in patches)
- Acceptance tests now mock the adapter layer (`get_best_sellers`, `get_reviews`, `get_ad_campaigns`) so they work without a live Amazon connection
- Bullet format regex updated to allow digits, hyphens, and Unicode symbols (e.g. `HEAT RESISTANT UP TO 600°F:`)
- `OpenAIProvider.__init__` now accepts `base_url` parameter for OpenAI-compatible API endpoints

### Changed
- Removed duplicated env setup and `client` fixtures from individual test files (now handled by `tests/conftest.py`)

---

## [1.0.0] — 2026-03-25

### Added
- **AI Product Research** — Score Amazon Best Sellers with LLM across competition, profit, trend dimensions
- **Listing Generator** — Generate complete Amazon listings in 6 languages from keyword or ASIN
- **Review Analyzer** — Extract pain points, praise, improvement suggestions from customer reviews
- **Competitor Monitor** — Periodic price/BSR/review tracking with configurable alerts (Celery Beat)
- **Ad Optimizer** — PPC campaign analysis and keyword bid recommendations via Amazon Advertising API
- **Pluggable Platform Adapters** — Amazon (SP-API + Playwright) implemented; Shopify stub included
- **LLM Abstraction Layer** — Supports OpenAI, Anthropic, Gemini, Ollama (switch via env var)
- **Docker Compose** one-command startup (backend + worker + beat + frontend + PostgreSQL + Redis)
- React + TypeScript frontend with dark-mode dashboard, all 5 module pages
