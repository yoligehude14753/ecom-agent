from dataclasses import dataclass, field


@dataclass
class ReviewAnalysis:
    asin: str
    total_reviews: int
    avg_rating: float
    sentiment_breakdown: dict              # {positive: %, negative: %, neutral: %}
    top_pain_points: list[str]             # top 5 user pain points
    top_praise_points: list[str]           # top 5 things users love
    improvement_suggestions: list[str]     # top 5 product improvement ideas
    common_keywords: list[dict]            # [{word, count, sentiment}]
    rating_distribution: dict             # {1: n, 2: n, 3: n, 4: n, 5: n}
    verified_purchase_ratio: float
    summary: str                           # executive summary narrative
    listing_recommendations: list[str]    # what to add/fix in the listing
