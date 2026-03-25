from dataclasses import dataclass, field


@dataclass
class ProductScore:
    asin: str
    title: str
    price: float
    bsr_rank: int | None
    bsr_category: str
    review_count: int
    rating: float
    competition_score: float      # 0-10, lower = less competition
    profit_potential_score: float # 0-10, higher = better
    trend_score: float            # 0-10, higher = trending up
    overall_score: float          # weighted composite
    ai_analysis: str              # LLM narrative
    recommended: bool
    tags: list[str] = field(default_factory=list)
