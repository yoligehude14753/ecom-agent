# Changelog

All notable changes to EcomAgent are documented here.

Format: [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versioning: [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
