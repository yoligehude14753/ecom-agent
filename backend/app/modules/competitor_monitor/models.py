from dataclasses import dataclass, field
from typing import Optional


@dataclass
class CompetitorSnapshot:
    asin: str
    title: str
    price: float
    bsr_rank: Optional[int]
    bsr_category: str
    review_count: int
    rating: float
    timestamp: str
    is_in_stock: bool = True
    alert_triggered: bool = False
    alert_reason: str = ""


@dataclass
class MonitoredASIN:
    asin: str
    platform: str
    label: str
    check_interval_minutes: int = 60
    snapshots: list[CompetitorSnapshot] = field(default_factory=list)
    alert_rules: dict = field(default_factory=dict)
    # alert_rules example: {"price_drop_pct": 10, "bsr_change_pct": 20}
