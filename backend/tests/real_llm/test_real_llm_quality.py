"""
Real LLM quality tests for EcomAgent — uses actual API call via yunwu.

These tests verify that the real model produces outputs meeting our quality standards.
They are NOT run in CI (excluded via pytest.ini: -m "not real_llm").

Local setup (copy .env.dev.example → .env.dev and fill in your key):
    cp .env.dev.example .env.dev
    # edit .env.dev: set OPENAI_API_KEY to your YUNWU_GPT_KEY or YUNWU_CLAUDE_KEY

Run:
    source .env.dev && pytest tests/real_llm/ -v -m real_llm -s

The `real_llm_provider` fixture auto-skips if no valid key is set.
"""
from __future__ import annotations

import json
import re
import pytest


# ─── Node 1: Listing Generator ────────────────────────────────────────────────

@pytest.mark.real_llm
@pytest.mark.asyncio
async def test_listing_generator_real_output(real_llm_provider):
    """
    Call the real model to generate a listing and verify quality criteria.
    Checks: Amazon compliance (title ≤ 200 chars, 5 bullets), SEO score range,
    bullet format (CAPS: description), keyword presence in title.
    """
    from app.modules.listing_generator.generator import LISTING_TEMPLATE, SYSTEM_PROMPT

    product_info = {
        "primary_keyword": "silicone kitchen spatula set",
        "material": "food-grade silicone",
        "quantity": "5-piece set",
        "heat_resistance": "up to 600°F",
        "color_options": "multiple colors",
    }
    prompt = LISTING_TEMPLATE.format(
        product_json=json.dumps(product_info, indent=2),
        marketplace="amazon.com",
        language_name="English (US)",
    )
    raw = await real_llm_provider.complete(prompt, system=SYSTEM_PROMPT, temperature=0.6, max_tokens=2000)
    result = json.loads(raw.strip())

    title = result.get("title", "")
    bullets = result.get("bullet_points", [])
    seo_score = float(result.get("seo_score", 0))

    # Amazon compliance
    assert len(title) <= 200, f"Title too long: {len(title)} chars"
    assert len(bullets) == 5, f"Expected 5 bullets, got {len(bullets)}"

    # Keyword in title
    assert "spatula" in title.lower() or "kitchen" in title.lower(), (
        f"Primary keyword not found in title: '{title}'"
    )

    # Bullet format: CAPS keyword before colon (robust to °, /, & and other special chars)
    def is_caps_format(bullet: str) -> bool:
        if ":" not in bullet:
            return False
        kw, desc = bullet.split(":", 1)
        alpha = [c for c in kw if c.isalpha()]
        if not alpha:
            return False
        return kw.strip()[0].isupper() and sum(c.isupper() for c in alpha) / len(alpha) >= 0.9 and len(desc.strip()) >= 10

    for i, bullet in enumerate(bullets):
        assert is_caps_format(bullet), (
            f"Bullet {i+1} doesn't follow 'CAPS: description' format: '{bullet[:80]}'"
        )

    # SEO score sanity
    assert 0 <= seo_score <= 10, f"SEO score {seo_score} out of range"
    print(f"\n✓ Title ({len(title)} chars): {title}")
    print(f"✓ SEO score: {seo_score}")
    print(f"✓ Bullets: {len(bullets)}")


# ─── Node 2: Product Scoring ──────────────────────────────────────────────────

@pytest.mark.real_llm
@pytest.mark.asyncio
async def test_product_scoring_real_output(real_llm_provider):
    """
    Call the real model to score a product and verify reasoning consistency.
    The product is a low-review-count, mid-price item — should score as good opportunity.
    """
    from app.modules.product_research.engine import ANALYSIS_TEMPLATE, SYSTEM_PROMPT

    product_data = {
        "asin": "B0EVAL001",
        "title": "Silicone Kitchen Spatula Set 5-Piece BPA Free",
        "price_usd": 22.99,
        "bsr_rank": 5800,
        "bsr_category": "Kitchen & Dining",
        "review_count": 68,
        "rating": 4.4,
        "num_bullet_points": 5,
    }
    prompt = ANALYSIS_TEMPLATE.format(product_json=json.dumps(product_data, indent=2))
    raw = await real_llm_provider.complete(prompt, system=SYSTEM_PROMPT, temperature=0.3)
    result = json.loads(raw.strip())

    competition_score = float(result.get("competition_score", 0))
    profit_potential = float(result.get("profit_potential_score", 0))
    overall_score = float(result.get("overall_score", 0))
    recommended = bool(result.get("recommended", False))
    analysis = result.get("analysis", "")
    tags = result.get("tags", [])

    # Low review count → should NOT have very low competition_score
    assert competition_score >= 5.0, (
        f"Only 68 reviews but competition_score={competition_score} — expected ≥ 5.0"
    )

    # Price in sweet spot → profit should be reasonable
    assert profit_potential >= 4.0, (
        f"$22.99 is in FBA sweet spot but profit_potential_score={profit_potential}"
    )

    # Recommendation consistency
    if recommended:
        assert overall_score >= 6.0, f"Recommended but score={overall_score}"

    # Analysis must be substantive
    assert len(analysis) >= 50, f"Analysis too short: '{analysis}'"
    assert len(tags) >= 1, "No tags returned"

    print(f"\n✓ Competition: {competition_score}, Profit: {profit_potential}, Overall: {overall_score}")
    print(f"✓ Recommended: {recommended}")
    print(f"✓ Analysis: {analysis[:120]}...")


# ─── Node 3: Review Analysis ──────────────────────────────────────────────────

@pytest.mark.real_llm
@pytest.mark.asyncio
async def test_review_analysis_real_output(real_llm_provider):
    """
    Call the real model with sample reviews and verify sentiment consistency.
    Input: mostly positive reviews about a kitchen spatula (avg 4.5 stars).
    """
    from app.modules.review_analyzer.analyzer import ANALYSIS_TEMPLATE, SYSTEM_PROMPT

    review_samples = """
[5★] Great spatulas!: These are the best spatulas I've ever owned. They don't scratch my non-stick pans and the silicone feels very high quality. Clean up is super easy too.

[5★] Love the set: Perfect size range for all my cooking needs. The heat resistance is impressive - used them right next to my burner with no issues.

[4★] Good but handles could be longer: Really nice quality and the colors are fun. Only downside is I wish the handles were slightly longer for deep pots.

[5★] Excellent quality: Been using these for 6 months now, still look brand new. The non-stick coating on my pan is intact too. Highly recommend.

[2★] Melted on high heat: Used on high heat and the head started to deform after a few minutes. Very disappointing for a product claiming 600°F resistance.

[1★] Misleading claims: These are not heat resistant at all. Damaged on first use at medium-high heat.
""".strip()

    prompt = ANALYSIS_TEMPLATE.format(
        asin="B0EVAL001",
        sample_count=6,
        total=6,
        avg_rating=4.5,
        rating_dist={1: 1, 2: 1, 4: 1, 5: 3},
        review_samples=review_samples,
    )
    raw = await real_llm_provider.complete(prompt, system=SYSTEM_PROMPT, temperature=0.3, max_tokens=2500)
    result = json.loads(raw.strip())

    breakdown = result.get("sentiment_breakdown", {})
    total_pct = sum(breakdown.values())
    pain_points = result.get("top_pain_points", [])
    suggestions = result.get("improvement_suggestions", [])
    summary = result.get("summary", "")

    # Sentiment consistency with avg 4.5 stars
    assert breakdown.get("positive", 0) >= 50, (
        f"4.5 avg but positive sentiment={breakdown.get('positive')}%"
    )

    # Sentiment sums to ~100
    assert abs(total_pct - 100) <= 5, f"Sentiment sum={total_pct}"

    # Heat issue should surface in pain points
    heat_mentioned = any("heat" in p.lower() or "melt" in p.lower() for p in pain_points)
    assert heat_mentioned, (
        f"Heat issue appears in negative reviews but not in pain points: {pain_points}"
    )

    # Suggestions must be actionable
    assert len(suggestions) >= 2, "Too few improvement suggestions"

    print(f"\n✓ Sentiment: {breakdown}")
    print(f"✓ Pain points: {pain_points}")
    print(f"✓ Summary: {summary[:120]}...")


# ─── Node 4: Ad Optimization ─────────────────────────────────────────────────

@pytest.mark.real_llm
@pytest.mark.asyncio
async def test_ad_optimization_real_output(real_llm_provider):
    """
    Call the real model with ad performance data and verify recommendation logic.
    Includes one high-performing keyword (raise) and one zero-conversion keyword (pause).
    """
    from app.modules.ad_optimizer.optimizer import OPTIMIZATION_TEMPLATE, SYSTEM_PROMPT

    campaigns_data = [
        {
            "campaign_id": "camp-001",
            "name": "Spatula Set - Exact Match",
            "keywords": [
                {
                    "keyword": "silicone spatula set",
                    "match_type": "exact",
                    "current_bid": 0.55,
                    "impressions": 15000,
                    "clicks": 420,
                    "ctr": 2.8,
                    "conversions": 28,
                    "spend": 231.0,
                    "sales": 644.0,
                    "acos": 35.9,
                },
                {
                    "keyword": "free kitchen tools",
                    "match_type": "broad",
                    "current_bid": 0.35,
                    "impressions": 8000,
                    "clicks": 320,
                    "ctr": 4.0,
                    "conversions": 0,
                    "spend": 112.0,
                    "sales": 0.0,
                    "acos": 999.0,
                },
            ],
        }
    ]
    prompt = OPTIMIZATION_TEMPLATE.format(
        campaigns_json=json.dumps(campaigns_data, indent=2),
        target_acos=35.0,
    )

    raw = await real_llm_provider.complete(prompt, system=SYSTEM_PROMPT, temperature=0.3, max_tokens=3000)
    result = json.loads(raw.strip())

    keyword_recs = result.get("keyword_recommendations", [])
    executive_summary = result.get("executive_summary", "")

    assert len(keyword_recs) >= 2, f"Expected recommendations for both keywords, got {len(keyword_recs)}"
    assert len(executive_summary) >= 20, "Executive summary too short"

    valid_actions = {"raise", "lower", "pause", "keep"}
    for rec in keyword_recs:
        assert rec.get("action") in valid_actions, f"Invalid action: {rec.get('action')}"

    # "free kitchen tools" had 0 conversions — should be paused
    free_tool_recs = [r for r in keyword_recs if "free" in r.get("keyword", "").lower()]
    if free_tool_recs:
        assert free_tool_recs[0]["action"] == "pause", (
            f"'free kitchen tools' with 0 conversions should be paused, "
            f"got: {free_tool_recs[0]['action']}"
        )

    # "silicone spatula set" has good performance — should not be paused
    spatula_recs = [r for r in keyword_recs if "spatula" in r.get("keyword", "").lower()]
    if spatula_recs:
        assert spatula_recs[0]["action"] != "pause", (
            "High-performing keyword 'silicone spatula set' should not be paused"
        )

    print(f"\n✓ {len(keyword_recs)} keyword recommendations")
    print(f"✓ Summary: {executive_summary[:120]}...")
    for rec in keyword_recs:
        print(f"  {rec['keyword']}: {rec['action']} (reason: {rec.get('reason', '')[:60]})")
