from fastapi import APIRouter
import dataclasses
from app.modules.ad_optimizer import optimize_ads

router = APIRouter(prefix="/ads", tags=["Ad Optimizer"])


@router.post("/optimize")
async def run_optimization(platform: str = "amazon", target_acos: float = 25.0):
    report = await optimize_ads(platform=platform, target_acos=target_acos)
    return dataclasses.asdict(report)
