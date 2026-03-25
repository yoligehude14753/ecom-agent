import json
from app.adapters.base import AdCampaign
from app.ai import get_llm_provider
from app.modules.ad_optimizer.models import AdOptimizationReport, KeywordRecommendation

SYSTEM_PROMPT = """You are an Amazon PPC advertising expert with deep knowledge of Sponsored Products optimization.
Analyze campaign performance data and provide data-driven optimization recommendations.
Always respond with valid JSON only, no markdown fences."""

OPTIMIZATION_TEMPLATE = """Analyze these Amazon Sponsored Products campaign metrics and provide optimization recommendations.

Campaign performance data:
{campaigns_json}

Target ACoS benchmark: {target_acos}%

Return a JSON object with these exact keys:
{{
  "keyword_recommendations": [
    {{
      "keyword": <string>,
      "current_bid": <float>,
      "recommended_bid": <float>,
      "impressions": <int>,
      "clicks": <int>,
      "ctr": <float>,
      "conversions": <int>,
      "spend": <float>,
      "sales": <float>,
      "acos": <float>,
      "action": "raise|lower|pause|add|negate",
      "reason": <string>
    }}
  ],
  "budget_recommendations": [
    {{"campaign_id": <string>, "campaign_name": <string>, "current_budget": <float>, "recommended_budget": <float>, "reason": <string>}}
  ],
  "negative_keyword_suggestions": [<list of keywords to negate>],
  "executive_summary": <2-3 sentence summary of current performance and top opportunities>,
  "estimated_monthly_savings": <float>,
  "estimated_monthly_sales_increase": <float>
}}"""


async def optimize_ads(
    platform: str = "amazon",
    target_acos: float = 25.0,
) -> AdOptimizationReport:
    from app.adapters import get_adapter
    adapter = get_adapter(platform)
    campaigns: list[AdCampaign] = await adapter.get_ad_campaigns()

    if not campaigns:
        return AdOptimizationReport(
            profile_id="",
            campaign_count=0,
            total_spend=0,
            total_sales=0,
            overall_acos=0,
            overall_roas=0,
            keyword_recommendations=[],
            budget_recommendations=[],
            negative_keyword_suggestions=[],
            executive_summary="No campaigns found.",
            estimated_monthly_savings=0,
            estimated_monthly_sales_increase=0,
        )

    total_spend = sum(c.spend for c in campaigns)
    total_sales = sum(c.sales for c in campaigns)
    overall_acos = (total_spend / total_sales * 100) if total_sales > 0 else 0
    overall_roas = (total_sales / total_spend) if total_spend > 0 else 0

    campaigns_data = [
        {
            "campaign_id": c.campaign_id,
            "name": c.name,
            "state": c.state,
            "budget": c.budget,
            "spend": c.spend,
            "sales": c.sales,
            "acos": c.acos,
            "roas": c.roas,
            "clicks": c.clicks,
            "impressions": c.impressions,
            "ctr": (c.clicks / c.impressions * 100) if c.impressions > 0 else 0,
        }
        for c in campaigns
    ]

    llm = get_llm_provider()
    prompt = OPTIMIZATION_TEMPLATE.format(
        campaigns_json=json.dumps(campaigns_data, indent=2),
        target_acos=target_acos,
    )
    raw = await llm.complete(prompt, system=SYSTEM_PROMPT, temperature=0.3, max_tokens=3000)

    try:
        result = json.loads(raw.strip())
    except json.JSONDecodeError:
        import re
        m = re.search(r"\{.*\}", raw, re.DOTALL)
        result = json.loads(m.group()) if m else {}

    kw_recs = [
        KeywordRecommendation(**kw) for kw in result.get("keyword_recommendations", [])
    ]

    return AdOptimizationReport(
        profile_id="",
        campaign_count=len(campaigns),
        total_spend=round(total_spend, 2),
        total_sales=round(total_sales, 2),
        overall_acos=round(overall_acos, 2),
        overall_roas=round(overall_roas, 2),
        keyword_recommendations=kw_recs,
        budget_recommendations=result.get("budget_recommendations", []),
        negative_keyword_suggestions=result.get("negative_keyword_suggestions", []),
        executive_summary=result.get("executive_summary", ""),
        estimated_monthly_savings=float(result.get("estimated_monthly_savings", 0)),
        estimated_monthly_sales_increase=float(result.get("estimated_monthly_sales_increase", 0)),
    )
