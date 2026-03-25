import json
from typing import Optional
from app.ai import get_llm_provider
from app.modules.listing_generator.models import GeneratedListing

SUPPORTED_LANGUAGES = {
    "en": "English (US)",
    "de": "German",
    "fr": "French",
    "es": "Spanish",
    "it": "Italian",
    "jp": "Japanese",
}

SYSTEM_PROMPT = """You are an expert Amazon listing copywriter and SEO specialist.
You create high-converting, keyword-rich Amazon listings that comply with Amazon's style guidelines.
Always respond with valid JSON only, no markdown fences."""

LISTING_TEMPLATE = """Create a complete Amazon product listing optimized for search and conversion.

Product info:
{product_json}

Target market: {marketplace}
Language: {language_name}

Amazon listing rules:
- Title: max 200 characters, include primary keyword naturally, brand + key features
- Bullet points: exactly 5, each max 500 characters, start with CAPS benefit label
- Description: max 2000 characters, storytelling format, include social proof language
- Search terms: backend keywords NOT in title, max 250 characters total (space separated)
- Subject matter: 5 A+ content module topics

Return JSON with these exact keys:
{{
  "title": <string>,
  "bullet_points": [<string>, <string>, <string>, <string>, <string>],
  "description": <string>,
  "search_terms": [<string>],
  "subject_matter": [<string>, <string>, <string>, <string>, <string>],
  "a_plus_draft": <string 300-500 chars narrative for A+ brand story>,
  "seo_score": <float 0-10>
}}"""

OPTIMIZE_TEMPLATE = """Analyze this existing Amazon listing and provide an improved version.

Original listing:
{original_json}

Competitor insights (top 3 competitors):
{competitors_json}

Return the same JSON structure as above with the optimized listing."""


async def generate_listing(
    keyword: str,
    product_details: Optional[dict] = None,
    marketplace: str = "amazon.com",
    language: str = "en",
) -> GeneratedListing:
    llm = get_llm_provider()
    language_name = SUPPORTED_LANGUAGES.get(language, "English (US)")

    product_info = product_details or {}
    if keyword and "primary_keyword" not in product_info:
        product_info["primary_keyword"] = keyword

    prompt = LISTING_TEMPLATE.format(
        product_json=json.dumps(product_info, indent=2),
        marketplace=marketplace,
        language_name=language_name,
    )

    raw = await llm.complete(prompt, system=SYSTEM_PROMPT, temperature=0.6, max_tokens=2000)

    try:
        result = json.loads(raw.strip())
    except json.JSONDecodeError:
        import re
        m = re.search(r"\{.*\}", raw, re.DOTALL)
        result = json.loads(m.group()) if m else {}

    title = result.get("title", "")
    description = result.get("description", "")
    search_terms = result.get("search_terms", [])
    search_terms_str = " ".join(search_terms)[:250]

    return GeneratedListing(
        asin_reference=product_details.get("asin", "") if product_details else "",
        marketplace=marketplace,
        language=language,
        title=title,
        bullet_points=result.get("bullet_points", [])[:5],
        description=description,
        search_terms=search_terms,
        subject_matter=result.get("subject_matter", []),
        a_plus_draft=result.get("a_plus_draft", ""),
        seo_score=float(result.get("seo_score", 0)),
        character_counts={
            "title": len(title),
            "description": len(description),
            "search_terms": len(search_terms_str),
        },
    )


async def optimize_listing_from_asin(
    asin: str,
    platform: str = "amazon",
    language: str = "en",
) -> GeneratedListing:
    from app.adapters import get_adapter
    adapter = get_adapter(platform)
    product = await adapter.get_product(asin)

    original = {
        "asin": asin,
        "title": product.title,
        "bullet_points": product.bullet_points,
        "description": product.description,
        "price": product.price,
        "rating": product.rating,
        "review_count": product.review_count,
    }

    llm = get_llm_provider()
    language_name = SUPPORTED_LANGUAGES.get(language, "English (US)")

    prompt = OPTIMIZE_TEMPLATE.format(
        original_json=json.dumps(original, indent=2),
        competitors_json="{}",
    )
    raw = await llm.complete(prompt, system=SYSTEM_PROMPT, temperature=0.6, max_tokens=2000)

    try:
        result = json.loads(raw.strip())
    except json.JSONDecodeError:
        import re
        m = re.search(r"\{.*\}", raw, re.DOTALL)
        result = json.loads(m.group()) if m else {}

    title = result.get("title", "")
    description = result.get("description", "")
    search_terms = result.get("search_terms", [])
    search_terms_str = " ".join(search_terms)[:250]

    return GeneratedListing(
        asin_reference=asin,
        marketplace="amazon.com",
        language=language,
        title=title,
        bullet_points=result.get("bullet_points", [])[:5],
        description=description,
        search_terms=search_terms,
        subject_matter=result.get("subject_matter", []),
        a_plus_draft=result.get("a_plus_draft", ""),
        seo_score=float(result.get("seo_score", 0)),
        character_counts={
            "title": len(title),
            "description": len(description),
            "search_terms": len(search_terms_str),
        },
    )
