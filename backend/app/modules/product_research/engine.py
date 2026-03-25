import json
from app.adapters.base import ProductListing
from app.ai import get_llm_provider
from app.modules.product_research.models import ProductScore


SYSTEM_PROMPT = """You are an expert Amazon FBA product researcher with 10+ years of experience.
Analyze products from a seller's perspective and provide actionable insights.
Always respond with valid JSON only, no markdown fences."""

ANALYSIS_TEMPLATE = """Analyze this Amazon product and score it for a new FBA seller:

Product data:
{product_json}

Return a JSON object with these exact keys:
{{
  "competition_score": <float 0-10, lower = less competition>,
  "profit_potential_score": <float 0-10, higher = better>,
  "trend_score": <float 0-10, higher = more trending>,
  "overall_score": <float 0-10 weighted composite>,
  "recommended": <boolean>,
  "tags": <list of 3-5 short descriptor tags e.g. ["low competition", "high margin"]>,
  "analysis": <2-3 sentence narrative for seller>
}}

Scoring guidelines:
- competition_score: BSR rank < 1000 in category = high competition (score 2-4). Review count < 200 = low competition (score 7-9).
- profit_potential_score: Price $15-$60 sweet spot = high (7-9). Consider typical FBA fees ~35% of price.
- trend_score: Use BSR rank + review velocity clues from review count vs rating age.
- recommended: true if overall_score >= 6.5 AND price is $15-$80"""


async def score_product(product: ProductListing) -> ProductScore:
    llm = get_llm_provider()
    product_data = {
        "asin": product.asin,
        "title": product.title,
        "price_usd": product.price,
        "bsr_rank": product.bsr_rank,
        "bsr_category": product.bsr_category,
        "review_count": product.review_count,
        "rating": product.rating,
        "num_bullet_points": len(product.bullet_points),
    }
    prompt = ANALYSIS_TEMPLATE.format(product_json=json.dumps(product_data, indent=2))
    raw = await llm.complete(prompt, system=SYSTEM_PROMPT, temperature=0.3)

    try:
        result = json.loads(raw.strip())
    except json.JSONDecodeError:
        import re
        m = re.search(r"\{.*\}", raw, re.DOTALL)
        result = json.loads(m.group()) if m else {}

    return ProductScore(
        asin=product.asin,
        title=product.title,
        price=product.price,
        bsr_rank=product.bsr_rank,
        bsr_category=product.bsr_category or "",
        review_count=product.review_count,
        rating=product.rating,
        competition_score=float(result.get("competition_score", 5)),
        profit_potential_score=float(result.get("profit_potential_score", 5)),
        trend_score=float(result.get("trend_score", 5)),
        overall_score=float(result.get("overall_score", 5)),
        ai_analysis=result.get("analysis", ""),
        recommended=bool(result.get("recommended", False)),
        tags=result.get("tags", []),
    )


async def research_category(
    category: str,
    limit: int = 50,
    min_overall_score: float = 6.0,
    platform: str = "amazon",
) -> list[ProductScore]:
    from app.adapters import get_adapter
    adapter = get_adapter(platform)
    products = await adapter.get_best_sellers(category, limit=limit)

    scores = []
    for product in products:
        try:
            score = await score_product(product)
            if score.overall_score >= min_overall_score:
                scores.append(score)
        except Exception:
            continue

    scores.sort(key=lambda s: s.overall_score, reverse=True)
    return scores
