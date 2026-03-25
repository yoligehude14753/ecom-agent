from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import json, dataclasses

from app.modules.competitor_monitor import take_snapshot, MonitoredASIN, CompetitorSnapshot

router = APIRouter(prefix="/monitor", tags=["Competitor Monitor"])


class AddMonitorRequest(BaseModel):
    asin: str
    platform: str = "amazon"
    label: str = ""
    check_interval_minutes: int = 60
    alert_rules: dict = {}


@router.post("/add")
async def add_monitor(req: AddMonitorRequest):
    import redis.asyncio as aioredis
    from app.core.config import get_settings
    settings = get_settings()
    r = await aioredis.from_url(settings.REDIS_URL)
    key = f"monitor:asin:{req.asin}"
    await r.set(key, json.dumps(req.dict()))
    await r.aclose()
    return {"status": "added", "asin": req.asin}


@router.delete("/remove/{asin}")
async def remove_monitor(asin: str):
    import redis.asyncio as aioredis
    from app.core.config import get_settings
    settings = get_settings()
    r = await aioredis.from_url(settings.REDIS_URL)
    deleted = await r.delete(f"monitor:asin:{asin}")
    await r.aclose()
    return {"status": "removed" if deleted else "not_found", "asin": asin}


@router.get("/list")
async def list_monitors():
    import redis.asyncio as aioredis
    from app.core.config import get_settings
    settings = get_settings()
    r = await aioredis.from_url(settings.REDIS_URL)
    keys = await r.keys("monitor:asin:*")
    monitors = []
    for key in keys:
        raw = await r.get(key)
        if raw:
            monitors.append(json.loads(raw))
    await r.aclose()
    return {"monitors": monitors}


@router.get("/snapshots/{asin}")
async def get_snapshots(asin: str, limit: int = 100):
    import redis.asyncio as aioredis
    from app.core.config import get_settings
    settings = get_settings()
    r = await aioredis.from_url(settings.REDIS_URL)
    raw_list = await r.lrange(f"snapshots:{asin}", 0, limit - 1)
    await r.aclose()
    snapshots = [json.loads(s) for s in raw_list]
    return {"asin": asin, "snapshots": snapshots}


@router.post("/snapshot/{asin}")
async def manual_snapshot(asin: str, platform: str = "amazon"):
    """Trigger an immediate snapshot for an ASIN."""
    monitored = MonitoredASIN(asin=asin, platform=platform, label="manual")
    try:
        snapshot = await take_snapshot(monitored)

        import redis.asyncio as aioredis
        from app.core.config import get_settings
        settings = get_settings()
        r = await aioredis.from_url(settings.REDIS_URL)
        await r.lpush(f"snapshots:{asin}", json.dumps(dataclasses.asdict(snapshot)))
        await r.ltrim(f"snapshots:{asin}", 0, 999)
        await r.aclose()

        return dataclasses.asdict(snapshot)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
