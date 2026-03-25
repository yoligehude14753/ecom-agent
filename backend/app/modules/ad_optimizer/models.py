from dataclasses import dataclass, field


@dataclass
class KeywordRecommendation:
    keyword: str
    current_bid: float
    recommended_bid: float
    impressions: int
    clicks: int
    ctr: float
    conversions: int
    spend: float
    sales: float
    acos: float
    action: str           # raise | lower | pause | add | negate
    reason: str


@dataclass
class AdOptimizationReport:
    profile_id: str
    campaign_count: int
    total_spend: float
    total_sales: float
    overall_acos: float
    overall_roas: float
    keyword_recommendations: list[KeywordRecommendation]
    budget_recommendations: list[dict]   # [{campaign_id, current, recommended, reason}]
    negative_keyword_suggestions: list[str]
    executive_summary: str
    estimated_monthly_savings: float
    estimated_monthly_sales_increase: float
