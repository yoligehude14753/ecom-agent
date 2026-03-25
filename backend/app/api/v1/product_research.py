from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
import dataclasses

from app.modules.product_research import research_category, score_product
from app.adapters import get_adapter

router = APIRouter(prefix="/product-research", tags=["Product Research"])


class ResearchRequest(BaseModel):
    category: str
    limit: int = 50
    min_score: float = 6.0
    platform: str = "amazon"


@router.post("/research")
async def run_research(req: ResearchRequest):
    try:
        scores = await research_category(
            req.category,
            limit=req.limit,
            min_overall_score=req.min_score,
            platform=req.platform,
        )
        return {"category": req.category, "results": [dataclasses.asdict(s) for s in scores]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/score/{asin}")
async def score_single(asin: str, platform: str = Query("amazon")):
    try:
        adapter = get_adapter(platform)
        product = await adapter.get_product(asin)
        score = await score_product(product)
        return dataclasses.asdict(score)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/categories")
async def list_categories():
    from app.adapters.amazon.adapter import BEST_SELLERS_CATEGORIES
    return {"categories": list(BEST_SELLERS_CATEGORIES.keys())}
