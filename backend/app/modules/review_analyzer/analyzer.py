from __future__ import annotations

import json
from collections import Counter
from app.adapters.base import ReviewItem
from app.ai import get_llm_provider
from app.modules.review_analyzer.models import ReviewAnalysis

SYSTEM_PROMPT = """You are an expert e-commerce product analyst specializing in customer review analysis.
Extract actionable insights from Amazon reviews to help sellers improve products and listings.
Always respond with valid JSON only, no markdown fences."""

ANALYSIS_TEMPLATE = """Analyze these Amazon product reviews for ASIN {asin}.

Reviews summary (showing {sample_count} of {total} total reviews):
Average rating: {avg_rating:.1f}/5
Rating distribution: {rating_dist}

Review samples:
{review_samples}

Return a JSON object with these exact keys:
{{
  "sentiment_breakdown": {{"positive": <0-100>, "negative": <0-100>, "neutral": <0-100>}},
  "top_pain_points": [<5 specific pain points from negative reviews>],
  "top_praise_points": [<5 specific things customers love>],
  "improvement_suggestions": [<5 concrete product improvement ideas based on reviews>],
  "common_keywords": [
    {{"word": <string>, "count": <int>, "sentiment": "positive|negative|neutral"}},
    ...  // top 15 keywords
  ],
  "summary": <3-4 sentence executive summary>,
  "listing_recommendations": [<3-5 things to add/emphasize/fix in the listing based on reviews>]
}}"""


def _build_review_samples(reviews: list[ReviewItem], max_samples: int = 50) -> str:
    samples = []
    # Prioritize: include 1-2 star and 4-5 star reviews equally
    neg = [r for r in reviews if r.rating <= 2][:max_samples // 3]
    pos = [r for r in reviews if r.rating >= 4][:max_samples // 3]
    mid = [r for r in reviews if r.rating == 3][:max_samples // 6]
    selected = pos + neg + mid

    for r in selected[:max_samples]:
        samples.append(f"[{r.rating}★] {r.title}: {r.body[:300]}")
    return "\n\n".join(samples)


async def analyze_reviews(
    asin: str,
    reviews: list[ReviewItem] | None = None,
    platform: str = "amazon",
    max_pages: int = 5,
) -> ReviewAnalysis:
    if reviews is None:
        from app.adapters import get_adapter
        adapter = get_adapter(platform)
        reviews = await adapter.get_reviews(asin, max_pages=max_pages)

    if not reviews:
        return ReviewAnalysis(
            asin=asin,
            total_reviews=0,
            avg_rating=0.0,
            sentiment_breakdown={"positive": 0, "negative": 0, "neutral": 0},
            top_pain_points=[],
            top_praise_points=[],
            improvement_suggestions=[],
            common_keywords=[],
            rating_distribution={},
            verified_purchase_ratio=0.0,
            summary="No reviews found.",
            listing_recommendations=[],
        )

    # Build basic stats
    rating_dist = Counter(r.rating for r in reviews)
    avg_rating = sum(r.rating for r in reviews) / len(reviews)
    verified_count = sum(1 for r in reviews if r.verified_purchase)
    verified_ratio = verified_count / len(reviews)

    review_samples = _build_review_samples(reviews)

    llm = get_llm_provider()
    prompt = ANALYSIS_TEMPLATE.format(
        asin=asin,
        sample_count=min(50, len(reviews)),
        total=len(reviews),
        avg_rating=avg_rating,
        rating_dist=dict(sorted(rating_dist.items())),
        review_samples=review_samples,
    )

    raw = await llm.complete(prompt, system=SYSTEM_PROMPT, temperature=0.3, max_tokens=2500)

    try:
        result = json.loads(raw.strip())
    except json.JSONDecodeError:
        import re
        m = re.search(r"\{.*\}", raw, re.DOTALL)
        result = json.loads(m.group()) if m else {}

    return ReviewAnalysis(
        asin=asin,
        total_reviews=len(reviews),
        avg_rating=round(avg_rating, 2),
        sentiment_breakdown=result.get("sentiment_breakdown", {"positive": 0, "negative": 0, "neutral": 0}),
        top_pain_points=result.get("top_pain_points", []),
        top_praise_points=result.get("top_praise_points", []),
        improvement_suggestions=result.get("improvement_suggestions", []),
        common_keywords=result.get("common_keywords", []),
        rating_distribution={str(k): v for k, v in rating_dist.items()},
        verified_purchase_ratio=round(verified_ratio, 3),
        summary=result.get("summary", ""),
        listing_recommendations=result.get("listing_recommendations", []),
    )
