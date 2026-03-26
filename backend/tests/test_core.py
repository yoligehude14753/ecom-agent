"""
Unit tests for EcomAgent backend modules.
Run with: pytest tests/ -v
"""
from __future__ import annotations

import dataclasses
import json
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

# ─── Models ───────────────────────────────────────────────────────────────────

def test_product_score_dataclass():
    from app.modules.product_research.models import ProductScore
    score = ProductScore(
        asin="B01TEST123",
        title="Test Product",
        price=29.99,
        bsr_rank=500,
        bsr_category="electronics",
        review_count=150,
        rating=4.3,
        competition_score=6.0,
        profit_potential_score=7.5,
        trend_score=5.0,
        overall_score=6.5,
        ai_analysis="This is a good product.",
        recommended=True,
        tags=["low competition", "mid price"],
    )
    assert score.asin == "B01TEST123"
    assert score.recommended is True
    assert len(score.tags) == 2
    d = dataclasses.asdict(score)
    assert d["overall_score"] == 6.5


def test_generated_listing_dataclass():
    from app.modules.listing_generator.models import GeneratedListing
    listing = GeneratedListing(
        asin_reference="B01TEST123",
        marketplace="amazon.com",
        language="en",
        title="Premium Water Bottle",
        bullet_points=["DURABLE: 18/8 stainless steel", "LEAKPROOF: Triple seal lid", "KEEPS COLD: 24 hours", "BPA FREE: Safe materials", "WIDE MOUTH: Easy to fill"],
        description="The best water bottle ever.",
        search_terms=["water bottle", "stainless steel bottle"],
        subject_matter=["durability", "insulation", "eco-friendly", "design", "convenience"],
        a_plus_draft="Our bottle keeps your drinks perfect all day.",
        seo_score=8.5,
        character_counts={"title": 22, "description": 30, "search_terms": 37},
    )
    assert len(listing.bullet_points) == 5
    assert listing.seo_score == 8.5


def test_review_analysis_dataclass():
    from app.modules.review_analyzer.models import ReviewAnalysis
    analysis = ReviewAnalysis(
        asin="B01TEST123",
        total_reviews=100,
        avg_rating=4.2,
        sentiment_breakdown={"positive": 70, "negative": 20, "neutral": 10},
        top_pain_points=["lid leaks", "cap hard to open"],
        top_praise_points=["keeps drinks cold", "great size"],
        improvement_suggestions=["improve lid seal", "better grip"],
        common_keywords=[{"word": "cold", "count": 45, "sentiment": "positive"}],
        rating_distribution={"1": 5, "2": 5, "3": 10, "4": 30, "5": 50},
        verified_purchase_ratio=0.85,
        summary="Overall positive reviews with minor lid concerns.",
        listing_recommendations=["Highlight cold retention in title"],
    )
    assert analysis.total_reviews == 100
    assert analysis.verified_purchase_ratio == 0.85


def test_competitor_snapshot_dataclass():
    from app.modules.competitor_monitor.models import CompetitorSnapshot
    snap = CompetitorSnapshot(
        asin="B01TEST123",
        title="Test",
        price=24.99,
        bsr_rank=1000,
        bsr_category="electronics",
        review_count=200,
        rating=4.5,
        timestamp="2026-03-25T12:00:00Z",
    )
    assert snap.alert_triggered is False
    assert snap.is_in_stock is True


def test_ad_optimization_report_dataclass():
    from app.modules.ad_optimizer.models import AdOptimizationReport, KeywordRecommendation
    rec = KeywordRecommendation(
        keyword="water bottle",
        current_bid=0.50,
        recommended_bid=0.65,
        impressions=10000,
        clicks=200,
        ctr=2.0,
        conversions=10,
        spend=100.0,
        sales=300.0,
        acos=33.3,
        action="raise",
        reason="High conversion rate, under-bidding",
    )
    report = AdOptimizationReport(
        profile_id="test-profile",
        campaign_count=3,
        total_spend=500.0,
        total_sales=1500.0,
        overall_acos=33.3,
        overall_roas=3.0,
        keyword_recommendations=[rec],
        budget_recommendations=[],
        negative_keyword_suggestions=["free", "cheap"],
        executive_summary="Performance is above average.",
        estimated_monthly_savings=50.0,
        estimated_monthly_sales_increase=200.0,
    )
    assert report.overall_roas == 3.0
    assert len(report.keyword_recommendations) == 1


# ─── Platform Adapter base contract ───────────────────────────────────────────

def test_amazon_adapter_platform_name():
    from app.adapters.amazon.adapter import AmazonAdapter
    adapter = AmazonAdapter()
    assert adapter.platform_name == "amazon"


def test_get_adapter_factory():
    from app.adapters import get_adapter
    from app.adapters.amazon.adapter import AmazonAdapter
    adapter = get_adapter("amazon")
    assert isinstance(adapter, AmazonAdapter)


def test_get_adapter_unknown_raises():
    from app.adapters import get_adapter
    with pytest.raises(ValueError, match="Unknown platform"):
        get_adapter("unknown_platform_xyz")


# ─── LLM abstraction ──────────────────────────────────────────────────────────

def test_llm_message_dataclass():
    from app.ai.base import LLMMessage
    msg = LLMMessage(role="user", content="hello")
    assert msg.role == "user"


@pytest.mark.asyncio
async def test_base_llm_complete_wrapper():
    """complete() should build messages and call chat()."""
    from app.ai.base import BaseLLMProvider, LLMMessage, LLMResponse

    class MockProvider(BaseLLMProvider):
        async def chat(self, messages, temperature=0.7, max_tokens=4096):
            assert messages[-1].role == "user"
            assert messages[-1].content == "test prompt"
            return LLMResponse(content="mock response", model="mock", prompt_tokens=10, completion_tokens=5, total_tokens=15)

        async def stream(self, messages, temperature=0.7, max_tokens=4096):
            yield "token"

    provider = MockProvider()
    result = await provider.complete("test prompt", system="you are helpful")
    assert result == "mock response"


# ─── Alert rules engine ───────────────────────────────────────────────────────

def test_alert_no_previous():
    from app.modules.competitor_monitor.monitor import _check_alerts
    from app.modules.competitor_monitor.models import CompetitorSnapshot
    snap = CompetitorSnapshot(asin="X", title="T", price=20.0, bsr_rank=100, bsr_category="e", review_count=50, rating=4.0, timestamp="2026-01-01T00:00:00Z")
    triggered, reason = _check_alerts(snap, None, {"price_drop_pct": 10})
    assert triggered is False
    assert reason == ""


def test_alert_price_drop_triggers():
    from app.modules.competitor_monitor.monitor import _check_alerts
    from app.modules.competitor_monitor.models import CompetitorSnapshot
    prev = CompetitorSnapshot(asin="X", title="T", price=100.0, bsr_rank=100, bsr_category="e", review_count=50, rating=4.0, timestamp="2026-01-01T00:00:00Z")
    curr = CompetitorSnapshot(asin="X", title="T", price=80.0, bsr_rank=100, bsr_category="e", review_count=50, rating=4.0, timestamp="2026-01-02T00:00:00Z")
    triggered, reason = _check_alerts(curr, prev, {"price_drop_pct": 15})
    assert triggered is True
    assert "20.0%" in reason


def test_alert_price_drop_below_threshold():
    from app.modules.competitor_monitor.monitor import _check_alerts
    from app.modules.competitor_monitor.models import CompetitorSnapshot
    prev = CompetitorSnapshot(asin="X", title="T", price=100.0, bsr_rank=100, bsr_category="e", review_count=50, rating=4.0, timestamp="2026-01-01T00:00:00Z")
    curr = CompetitorSnapshot(asin="X", title="T", price=95.0, bsr_rank=100, bsr_category="e", review_count=50, rating=4.0, timestamp="2026-01-02T00:00:00Z")
    triggered, reason = _check_alerts(curr, prev, {"price_drop_pct": 15})
    assert triggered is False


def test_alert_bsr_change_triggers():
    from app.modules.competitor_monitor.monitor import _check_alerts
    from app.modules.competitor_monitor.models import CompetitorSnapshot
    prev = CompetitorSnapshot(asin="X", title="T", price=20.0, bsr_rank=1000, bsr_category="e", review_count=50, rating=4.0, timestamp="2026-01-01T00:00:00Z")
    curr = CompetitorSnapshot(asin="X", title="T", price=20.0, bsr_rank=500, bsr_category="e", review_count=50, rating=4.0, timestamp="2026-01-02T00:00:00Z")
    triggered, reason = _check_alerts(curr, prev, {"bsr_change_pct": 40})
    assert triggered is True
    assert "BSR" in reason


# ─── API endpoints (no DB / LLM needed) ───────────────────────────────────────
# The shared `client` fixture is provided by tests/conftest.py


def test_health_endpoint(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_categories_endpoint(client):
    resp = client.get("/api/v1/product-research/categories")
    assert resp.status_code == 200
    data = resp.json()
    assert "categories" in data
    assert "electronics" in data["categories"]
    assert len(data["categories"]) >= 10


def test_languages_endpoint(client):
    resp = client.get("/api/v1/listing/languages")
    assert resp.status_code == 200
    data = resp.json()
    assert "languages" in data
    assert "en" in data["languages"]
    assert "de" in data["languages"]


def test_monitor_add_and_list(client):
    resp = client.post("/api/v1/monitor/add", json={
        "asin": "B0TEST00001",
        "label": "test",
        "alert_rules": {"price_drop_pct": 10},
    })
    assert resp.status_code == 200
    assert resp.json()["status"] == "added"

    # skip list test since it requires Redis
    resp2 = client.delete("/api/v1/monitor/remove/B0TEST00001")
    assert resp2.status_code == 200


def test_listing_generate_missing_keyword(client):
    resp = client.post("/api/v1/listing/generate", json={})
    assert resp.status_code == 422  # pydantic validation error


def test_reviews_analyze_missing_asin(client):
    resp = client.post("/api/v1/reviews/analyze", json={})
    assert resp.status_code == 422


def test_research_missing_category(client):
    resp = client.post("/api/v1/product-research/research", json={})
    assert resp.status_code == 422
