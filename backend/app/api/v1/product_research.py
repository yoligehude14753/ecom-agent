from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
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
    scores = await research_category(
        req.category,
        limit=req.limit,
        min_overall_score=req.min_score,
        platform=req.platform,
    )
    return {"category": req.category, "results": [dataclasses.asdict(s) for s in scores]}


@router.get("/score/{asin}")
async def score_single(asin: str, platform: str = Query("amazon")):
    adapter = get_adapter(platform)
    try:
        product = await adapter.get_product(asin)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Product not found: {e}")
    score = await score_product(product)
    return dataclasses.asdict(score)


@router.get("/categories")
async def list_categories():
    from app.adapters.amazon.adapter import BEST_SELLERS_CATEGORIES
    return {"categories": list(BEST_SELLERS_CATEGORIES.keys())}
