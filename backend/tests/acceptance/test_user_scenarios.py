"""
User-scenario acceptance tests for EcomAgent.

Tests are written from the USER's perspective:
  - Each test is named after a real user intent ("user wants to discover products")
  - Assertions verify what the user SEES in the UI, not internal implementation
  - LLM and scrapers are mocked; the test validates pipeline output structure + business rules

The shared `client` fixture and env setup are in tests/conftest.py.
Run with: pytest tests/acceptance/ -v
"""
from __future__ import annotations

import json
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

# ─── Mock LLM response payloads (what a real LLM would return) ────────────────
# These mirror the exact JSON structure that modules parse and return to the UI.

MOCK_PRODUCTS = json.dumps({
    "products": [
        {
            "asin": "B0MOCK001",
            "title": "Premium Stainless Steel Water Bottle 32oz",
            "price": 24.99,
            "bsr_rank": 450,
            "bsr_category": "sports",
            "review_count": 3200,
            "rating": 4.6,
            "competition_score": 5.5,
            "profit_potential_score": 8.2,
            "trend_score": 7.0,
            "overall_score": 7.8,
            "ai_analysis": "Strong profit potential due to low competition and high demand trend. Differentiation through color variants recommended.",
            "recommended": True,
            "tags": ["low competition", "trending", "high margin"],
        },
        {
            "asin": "B0MOCK002",
            "title": "Phone Case for iPhone 15 Slim Clear",
            "price": 9.99,
            "bsr_rank": 120,
            "bsr_category": "electronics",
            "review_count": 15000,
            "rating": 4.1,
            "competition_score": 9.2,
            "profit_potential_score": 3.0,
            "trend_score": 5.5,
            "overall_score": 4.2,
            "ai_analysis": "Extremely saturated market. Entry barrier is high and margin is thin.",
            "recommended": False,
            "tags": ["high competition", "low margin"],
        },
    ]
})

MOCK_LISTING = json.dumps({
    "title": "Premium Stainless Steel Water Bottle 32oz - BPA Free, Insulated, Leakproof",
    "bullet_points": [
        "KEEPS DRINKS COLD 24 HOURS: Double-wall vacuum insulation maintains beverage temperature all day",
        "BPA FREE & SAFE: Made from 18/8 food-grade stainless steel, absolutely no metallic taste",
        "LEAKPROOF LID: Triple-seal cap guarantees zero leaks in your bag or car",
        "WIDE MOUTH DESIGN: Fits ice cubes, easy to fill, clean, and drink from",
        "LIFETIME WARRANTY: We stand behind every bottle with hassle-free replacement",
    ],
    "description": "Stay hydrated anywhere with our premium stainless steel water bottle. Engineered for active lifestyles, this bottle keeps drinks cold for 24 hours and hot for 12 hours.",
    "search_terms": ["insulated water bottle", "stainless steel water bottle 32oz", "bpa free water bottle"],
    "subject_matter": ["hydration", "insulation", "eco-friendly", "sports", "outdoor"],
    "a_plus_draft": "### Why Our Bottle?\nEngineered for the active lifestyle with superior insulation technology.",
    "seo_score": 8.7,
    "character_counts": {"title": 75, "description": 201, "search_terms": 85},
})

MOCK_REVIEW_ANALYSIS = json.dumps({
    "total_reviews": 3200,
    "avg_rating": 4.6,
    "sentiment_breakdown": {"positive": 82, "negative": 10, "neutral": 8},
    "top_pain_points": ["lid sometimes leaks after extended use", "paint chips over time"],
    "top_praise_points": ["excellent insulation", "durable build", "great size"],
    "improvement_suggestions": [
        "reinforce lid sealing mechanism",
        "use more durable exterior coating",
    ],
    "common_keywords": [
        {"word": "insulation", "count": 890, "sentiment": "positive"},
        {"word": "leaks", "count": 210, "sentiment": "negative"},
    ],
    "rating_distribution": {"1": 3, "2": 2, "3": 5, "4": 20, "5": 70},
    "verified_purchase_ratio": 0.91,
    "summary": "Buyers consistently praise the insulation quality but 10% report lid issues after heavy use.",
    "listing_recommendations": [
        "Add 'improved leak-proof lid' to bullet points",
        "Address lid durability in description FAQ section",
    ],
})

MOCK_AD_REPORT = json.dumps({
    "profile_id": "test-profile-001",
    "campaign_count": 3,
    "total_spend": 450.0,
    "total_sales": 1800.0,
    "overall_acos": 25.0,
    "overall_roas": 4.0,
    "keyword_recommendations": [
        {
            "keyword": "insulated water bottle",
            "current_bid": 0.45,
            "recommended_bid": 0.62,
            "impressions": 12000,
            "clicks": 360,
            "ctr": 3.0,
            "conversions": 22,
            "spend": 162.0,
            "sales": 548.0,
            "acos": 29.6,
            "action": "raise",
            "reason": "Above-average CVR (6.1%) with room to capture more impressions at a higher bid",
        },
        {
            "keyword": "free water bottle",
            "current_bid": 0.30,
            "recommended_bid": 0.0,
            "impressions": 5000,
            "clicks": 200,
            "ctr": 4.0,
            "conversions": 0,
            "spend": 60.0,
            "sales": 0.0,
            "acos": 999.0,
            "action": "pause",
            "reason": "Zero conversions after 200 clicks — add as negative keyword to stop wasted spend",
        },
    ],
    "budget_recommendations": [],
    "negative_keyword_suggestions": ["free", "diy", "used"],
    "executive_summary": "Overall ROAS is healthy at 4.0x. Two immediate actions can reduce wasted spend by $60/month.",
    "estimated_monthly_savings": 60.0,
    "estimated_monthly_sales_increase": 180.0,
})


# ─── Test client ─────────────────────────────────────────────────────────────
# Provided by tests/conftest.py (session-scoped, shared across all test suites)


# ═══════════════════════════════════════════════════════════════════════════════
# ACC-01: 选品场景
# User intent: "I want to find high-potential products in the Sports category"
# ═══════════════════════════════════════════════════════════════════════════════

@patch("app.adapters.amazon.adapter.AmazonAdapter.get_best_sellers")
@patch("app.modules.product_research.engine.get_llm_provider")
def test_acc01_product_discovery_returns_scored_list(mock_llm, mock_scraper, client):
    """
    User selects a category and runs research.
    Should see a list of products with AI scores and clear recommended/not labels.
    """
    from app.adapters.base import ProductListing
    mock_scraper.return_value = [
        ProductListing(asin="B0MOCK001", title="Premium Stainless Steel Water Bottle 32oz",
                       brand="MockBrand", price=24.99, currency="USD", bsr_rank=450,
                       bsr_category="sports", review_count=3200, rating=4.6),
        ProductListing(asin="B0MOCK002", title="Phone Case for iPhone 15 Slim Clear",
                       brand="MockBrand", price=9.99, currency="USD", bsr_rank=120,
                       bsr_category="electronics", review_count=15000, rating=4.1),
    ]
    mock_provider = MagicMock()
    mock_provider.complete = AsyncMock(return_value=json.dumps({
        "competition_score": 5.5, "profit_potential_score": 8.2, "trend_score": 7.0,
        "overall_score": 7.8, "recommended": True,
        "tags": ["low competition", "trending"],
        "analysis": "Strong profit potential due to low competition and high demand trend.",
    }))
    mock_llm.return_value = mock_provider

    resp = client.post("/api/v1/product-research/research", json={
        "category": "sports",
        "max_products": 20,
    })

    assert resp.status_code == 200, f"Research endpoint failed: {resp.text}"
    data = resp.json()

    # API returns `results` key (not `products`)
    assert "results" in data, f"Response must have 'results' key, got keys: {list(data.keys())}"
    assert len(data["results"]) > 0, "User should see at least one product"

    required_fields = {"asin", "title", "overall_score", "recommended", "ai_analysis"}
    for product in data["results"]:
        missing = required_fields - set(product.keys())
        assert not missing, f"Product {product.get('asin')} is missing fields: {missing}"

    for product in data["results"]:
        if product["recommended"]:
            assert product["overall_score"] >= 6.0, (
                f"Recommended product {product['asin']} has score {product['overall_score']} — should be >= 6.0"
            )

    for product in data["results"]:
        assert len(product["ai_analysis"]) >= 20, (
            f"ai_analysis for {product['asin']} is too short"
        )


@patch("app.adapters.amazon.adapter.AmazonAdapter.get_best_sellers")
@patch("app.modules.product_research.engine.get_llm_provider")
def test_acc01_non_recommended_products_have_lower_score(mock_llm, mock_scraper, client):
    """
    Products not marked as recommended should have lower overall scores.
    """
    from app.adapters.base import ProductListing
    mock_scraper.return_value = [
        ProductListing(asin="B0MOCK002", title="Phone Case for iPhone 15",
                       brand="MockBrand", price=9.99, currency="USD", bsr_rank=120,
                       bsr_category="electronics", review_count=15000, rating=4.1),
    ]
    mock_provider = MagicMock()
    mock_provider.complete = AsyncMock(return_value=json.dumps({
        "competition_score": 9.2, "profit_potential_score": 3.0, "trend_score": 5.5,
        "overall_score": 4.2, "recommended": False,
        "tags": ["high competition"], "analysis": "Extremely saturated market. New entrants will struggle.",
    }))
    mock_llm.return_value = mock_provider

    resp = client.post("/api/v1/product-research/research", json={"category": "electronics"})
    assert resp.status_code == 200

    for product in resp.json()["results"]:
        if not product["recommended"]:
            assert product["overall_score"] < 7.0, (
                f"Non-recommended product {product['asin']} has high score {product['overall_score']}"
            )


# ═══════════════════════════════════════════════════════════════════════════════
# ACC-02: Listing 生成场景
# User intent: "I want a ready-to-upload Amazon listing for 'water bottle'"
# ═══════════════════════════════════════════════════════════════════════════════

@patch("app.modules.listing_generator.generator.get_llm_provider")
def test_acc02_listing_generation_is_amazon_compliant(mock_llm, client):
    """
    User enters a keyword and marketplace.
    Should get a listing that passes Amazon's structural requirements.
    """
    mock_provider = MagicMock()
    mock_provider.complete = AsyncMock(return_value=MOCK_LISTING)
    mock_llm.return_value = mock_provider

    resp = client.post("/api/v1/listing/generate", json={
        "keyword": "stainless steel water bottle",
        "marketplace": "amazon.com",
        "language": "en",
    })

    assert resp.status_code == 200, f"Listing generation failed: {resp.text}"
    data = resp.json()

    # Amazon title limit: 200 characters
    assert len(data["title"]) <= 200, (
        f"Title is {len(data['title'])} chars — exceeds Amazon's 200-char limit"
    )

    # Amazon requires exactly 5 bullet points
    assert len(data["bullet_points"]) == 5, (
        f"Got {len(data['bullet_points'])} bullets — Amazon requires exactly 5"
    )

    # Each bullet must be substantive
    for i, bullet in enumerate(data["bullet_points"]):
        assert len(bullet) >= 20, (
            f"Bullet {i + 1} is too short ('{bullet}') — user won't find it useful"
        )

    # Description must exist and be non-trivial
    assert len(data.get("description", "")) >= 50, "Description is missing or too short"

    # Search terms must be present (backend keywords for Amazon)
    assert len(data.get("search_terms", [])) >= 1, "Search terms are required"

    # SEO score is shown in UI so user can judge listing quality
    assert "seo_score" in data, "SEO score must be present"
    assert 0 <= data["seo_score"] <= 10, f"SEO score {data['seo_score']} is outside [0, 10]"


def test_acc02_listing_missing_keyword_returns_validation_error(client):
    """User submits empty form — should get a clear validation error, not a 500."""
    resp = client.post("/api/v1/listing/generate", json={})
    assert resp.status_code == 422, "Missing keyword must return 422, not crash"


# ═══════════════════════════════════════════════════════════════════════════════
# ACC-03: 评论分析场景
# User intent: "I want to know what customers love/hate about a competitor product"
# ═══════════════════════════════════════════════════════════════════════════════

@patch("app.adapters.amazon.adapter.AmazonAdapter.get_reviews")
@patch("app.modules.review_analyzer.analyzer.get_llm_provider")
def test_acc03_review_analysis_provides_actionable_insights(mock_llm, mock_scraper, client):
    """
    User enters a competitor's ASIN.
    Should get a structured sentiment report with pain points and actionable suggestions.
    """
    from app.adapters.base import ReviewItem
    mock_scraper.return_value = [
        ReviewItem(review_id="R001", asin="B0MOCK001", rating=5, title="Great bottle",
                   body="Excellent insulation, keeps drinks cold all day.", author="TestUser1",
                   date="2026-01-01", verified_purchase=True, helpful_votes=10),
        ReviewItem(review_id="R002", asin="B0MOCK001", rating=2, title="Lid leaks",
                   body="The lid leaks after a few weeks of use. Very disappointing.", author="TestUser2",
                   date="2026-01-02", verified_purchase=True, helpful_votes=5),
        ReviewItem(review_id="R003", asin="B0MOCK001", rating=5, title="Love it",
                   body="Durable and keeps my coffee hot for hours.", author="TestUser3",
                   date="2026-01-03", verified_purchase=True, helpful_votes=8),
    ]
    mock_provider = MagicMock()
    mock_provider.complete = AsyncMock(return_value=MOCK_REVIEW_ANALYSIS)
    mock_llm.return_value = mock_provider

    resp = client.post("/api/v1/reviews/analyze", json={
        "asin": "B0MOCK001",
        "max_reviews": 100,
    })

    assert resp.status_code == 200, f"Review analysis failed: {resp.text}"
    data = resp.json()

    # Sentiment breakdown must sum to ~100% (chart needs consistent data)
    assert "sentiment_breakdown" in data
    breakdown = data["sentiment_breakdown"]
    for key in ("positive", "negative", "neutral"):
        assert key in breakdown, f"Sentiment breakdown missing '{key}' key"
    total = sum(breakdown.values())
    assert abs(total - 100) <= 2, (
        f"Sentiment percentages sum to {total} — should be ~100%"
    )

    # User needs at least one concrete pain point to act on
    assert len(data.get("top_pain_points", [])) >= 1, (
        "Must surface at least one pain point"
    )

    # Improvement suggestions must be actionable (not just vague)
    suggestions = data.get("improvement_suggestions", [])
    assert len(suggestions) >= 1, "Must provide at least one improvement suggestion"
    for s in suggestions:
        assert len(s) >= 10, f"Suggestion '{s}' is too vague to be actionable"

    # Summary must be readable (user shouldn't have to decode raw numbers)
    assert len(data.get("summary", "")) >= 30, (
        "Summary is too short — user needs a human-readable overview"
    )

    # Listing recommendations tie review findings to user's own product actions
    assert len(data.get("listing_recommendations", [])) >= 1, (
        "Must connect review findings to listing improvement actions"
    )


def test_acc03_review_missing_asin_returns_validation_error(client):
    """User submits empty ASIN — should get 422, not 500."""
    resp = client.post("/api/v1/reviews/analyze", json={})
    assert resp.status_code == 422


# ═══════════════════════════════════════════════════════════════════════════════
# ACC-04: 竞品监控场景
# User intent: "I want to track competitor B0MOCK001 and get alerted on price drops > 10%"
# ═══════════════════════════════════════════════════════════════════════════════

def test_acc04_monitor_add_confirms_tracking(client):
    """
    User adds a competitor ASIN with custom alert rules.
    Should get a confirmation that the ASIN is being tracked.
    """
    resp = client.post("/api/v1/monitor/add", json={
        "asin": "B0MONITOR001",
        "label": "Main competitor — premium water bottle",
        "alert_rules": {
            "price_drop_pct": 10,
            "bsr_change_pct": 20,
        },
    })

    assert resp.status_code == 200, f"Monitor add failed: {resp.text}"
    data = resp.json()
    assert data.get("status") == "added", (
        f"Response should confirm addition with status='added', got: {data}"
    )


def test_acc04_monitor_remove_cleans_up(client):
    """User removes a monitored ASIN — should succeed without errors."""
    asin = "B0MONITOR_REMOVE"
    client.post("/api/v1/monitor/add", json={
        "asin": asin,
        "label": "temp",
        "alert_rules": {},
    })

    resp = client.delete(f"/api/v1/monitor/remove/{asin}")
    assert resp.status_code == 200, f"Monitor remove failed: {resp.text}"


# ═══════════════════════════════════════════════════════════════════════════════
# ACC-05: 广告优化场景
# User intent: "I want to know which keywords to raise bids on and which to pause"
# ═══════════════════════════════════════════════════════════════════════════════

@patch("app.adapters.amazon.adapter.AmazonAdapter.get_ad_campaigns")
@patch("app.modules.ad_optimizer.optimizer.get_llm_provider")
def test_acc05_ad_optimization_gives_keyword_actions_with_reasons(mock_llm, mock_adapter, client):
    """
    User submits their ad profile for optimization.
    Should get keyword-level recommendations with a clear action and explanation.
    """
    from app.adapters.base import AdCampaign
    mock_adapter.return_value = [
        AdCampaign(campaign_id="camp-001", name="Sponsored - Water Bottle", state="enabled",
                   budget=50.0, spend=350.0, sales=1400.0, acos=25.0, roas=4.0,
                   clicks=400, impressions=12000),
    ]
    mock_provider = MagicMock()
    mock_provider.complete = AsyncMock(return_value=MOCK_AD_REPORT)
    mock_llm.return_value = mock_provider

    resp = client.post("/api/v1/ads/optimize")

    assert resp.status_code == 200, f"Ad optimization failed: {resp.text}"
    data = resp.json()

    # User reads the executive summary first — must be meaningful
    assert len(data.get("executive_summary", "")) >= 20, (
        "Executive summary is too short — user needs a plain-language overview"
    )

    # Each keyword recommendation must have a clear action
    recs = data.get("keyword_recommendations", [])
    assert len(recs) >= 1, "Must provide at least one keyword recommendation"

    valid_actions = {"raise", "lower", "pause", "keep"}
    for rec in recs:
        assert "keyword" in rec, "Each recommendation must identify the keyword"
        assert rec.get("action") in valid_actions, (
            f"action '{rec.get('action')}' is not one of {valid_actions}"
        )
        assert len(rec.get("reason", "")) >= 10, (
            f"Reason for '{rec['keyword']}' is too short — user needs an explanation"
        )

    # User needs to know the expected ROI of accepting the recommendations
    assert "estimated_monthly_savings" in data, "Must show potential savings"
    assert "estimated_monthly_sales_increase" in data, "Must show potential sales upside"


@patch("app.adapters.amazon.adapter.AmazonAdapter.get_ad_campaigns")
@patch("app.modules.ad_optimizer.optimizer.get_llm_provider")
def test_acc05_pause_keywords_have_zero_or_negative_roi(mock_llm, mock_adapter, client):
    """
    Keywords marked 'pause' should have evidence of poor performance.
    """
    from app.adapters.base import AdCampaign
    mock_adapter.return_value = [
        AdCampaign(campaign_id="camp-001", name="Test Campaign", state="enabled",
                   budget=50.0, spend=100.0, sales=0.0, acos=999.0, roas=0.0,
                   clicks=200, impressions=5000),
    ]
    mock_provider = MagicMock()
    mock_provider.complete = AsyncMock(return_value=MOCK_AD_REPORT)
    mock_llm.return_value = mock_provider

    resp = client.post("/api/v1/ads/optimize")
    assert resp.status_code == 200

    for rec in resp.json().get("keyword_recommendations", []):
        if rec["action"] == "pause":
            assert rec.get("conversions", -1) == 0 or rec.get("acos", 0) > 100, (
                f"Keyword '{rec['keyword']}' is marked pause but has "
                f"{rec.get('conversions')} conversions and {rec.get('acos')}% ACoS"
            )
