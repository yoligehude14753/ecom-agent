from __future__ import annotations

from datetime import datetime, timezone
from app.adapters.base import ProductListing
from app.modules.competitor_monitor.models import CompetitorSnapshot, MonitoredASIN
from app.core.logging import logger


def _check_alerts(snapshot: CompetitorSnapshot, previous: CompetitorSnapshot | None, rules: dict) -> tuple[bool, str]:
    if not previous:
        return False, ""

    if "price_drop_pct" in rules and previous.price > 0:
        drop = (previous.price - snapshot.price) / previous.price * 100
        if drop >= rules["price_drop_pct"]:
            return True, f"Price dropped {drop:.1f}% (${previous.price:.2f} → ${snapshot.price:.2f})"

    if "price_rise_pct" in rules and previous.price > 0:
        rise = (snapshot.price - previous.price) / previous.price * 100
        if rise >= rules["price_rise_pct"]:
            return True, f"Price rose {rise:.1f}% (${previous.price:.2f} → ${snapshot.price:.2f})"

    if "bsr_change_pct" in rules and previous.bsr_rank and snapshot.bsr_rank:
        change = abs(snapshot.bsr_rank - previous.bsr_rank) / previous.bsr_rank * 100
        if change >= rules["bsr_change_pct"]:
            direction = "improved" if snapshot.bsr_rank < previous.bsr_rank else "dropped"
            return True, f"BSR {direction} by {change:.1f}% (#{previous.bsr_rank} → #{snapshot.bsr_rank})"

    if "review_spike" in rules:
        new_reviews = snapshot.review_count - previous.review_count
        if new_reviews >= rules["review_spike"]:
            return True, f"Review spike: +{new_reviews} new reviews"

    return False, ""


async def take_snapshot(monitored: MonitoredASIN) -> CompetitorSnapshot:
    from app.adapters import get_adapter
    adapter = get_adapter(monitored.platform)
    product: ProductListing = await adapter.get_product(monitored.asin)

    previous = monitored.snapshots[-1] if monitored.snapshots else None
    triggered, reason = _check_alerts(
        CompetitorSnapshot(
            asin=product.asin,
            title=product.title,
            price=product.price,
            bsr_rank=product.bsr_rank,
            bsr_category=product.bsr_category or "",
            review_count=product.review_count,
            rating=product.rating,
            timestamp=datetime.now(timezone.utc).isoformat(),
        ),
        previous,
        monitored.alert_rules,
    )

    snapshot = CompetitorSnapshot(
        asin=product.asin,
        title=product.title,
        price=product.price,
        bsr_rank=product.bsr_rank,
        bsr_category=product.bsr_category or "",
        review_count=product.review_count,
        rating=product.rating,
        timestamp=datetime.now(timezone.utc).isoformat(),
        alert_triggered=triggered,
        alert_reason=reason,
    )

    if triggered:
        logger.warning("competitor_alert", asin=monitored.asin, reason=reason)

    return snapshot
