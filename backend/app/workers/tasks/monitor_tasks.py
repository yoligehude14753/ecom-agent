import asyncio
from app.workers.celery_app import celery_app
from app.core.logging import logger


@celery_app.task(bind=True, name="app.workers.tasks.monitor_tasks.run_scheduled_monitors", max_retries=3)
def run_scheduled_monitors(self):
    """Periodic task: take snapshots for all monitored ASINs stored in Redis."""
    asyncio.run(_run_monitors())


async def _run_monitors():
    import redis.asyncio as aioredis
    import json
    from app.core.config import get_settings
    from app.modules.competitor_monitor import take_snapshot, MonitoredASIN

    settings = get_settings()
    r = await aioredis.from_url(settings.REDIS_URL)
    keys = await r.keys("monitor:asin:*")

    for key in keys:
        raw = await r.get(key)
        if not raw:
            continue
        data = json.loads(raw)
        monitored = MonitoredASIN(
            asin=data["asin"],
            platform=data.get("platform", "amazon"),
            label=data.get("label", ""),
            check_interval_minutes=data.get("check_interval_minutes", 60),
            alert_rules=data.get("alert_rules", {}),
            snapshots=[],
        )
        try:
            snapshot = await take_snapshot(monitored)
            # Persist snapshot to Redis list
            snap_key = f"snapshots:{monitored.asin}"
            import dataclasses
            await r.lpush(snap_key, json.dumps(dataclasses.asdict(snapshot)))
            await r.ltrim(snap_key, 0, 999)  # keep last 1000 snapshots per ASIN
            logger.info("snapshot_taken", asin=monitored.asin, price=snapshot.price)
        except Exception as exc:
            logger.error("snapshot_failed", asin=monitored.asin, error=str(exc))

    await r.aclose()


@celery_app.task(name="app.workers.tasks.monitor_tasks.scrape_product_research")
def scrape_product_research(category: str, limit: int = 50):
    """On-demand task: run product research for a category."""
    return asyncio.run(_research(category, limit))


async def _research(category: str, limit: int):
    import dataclasses
    from app.modules.product_research import research_category
    scores = await research_category(category, limit=limit)
    return [dataclasses.asdict(s) for s in scores]
