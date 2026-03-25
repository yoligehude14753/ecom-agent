from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import dataclasses

from app.modules.review_analyzer import analyze_reviews

router = APIRouter(prefix="/reviews", tags=["Review Analyzer"])


class AnalyzeRequest(BaseModel):
    asin: str
    platform: str = "amazon"
    max_pages: int = 5


@router.post("/analyze")
async def analyze(req: AnalyzeRequest):
    try:
        analysis = await analyze_reviews(
            asin=req.asin,
            platform=req.platform,
            max_pages=req.max_pages,
        )
        return dataclasses.asdict(analysis)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analyze/{asin}")
async def analyze_get(asin: str, platform: str = "amazon", max_pages: int = 3):
    try:
        analysis = await analyze_reviews(asin=asin, platform=platform, max_pages=max_pages)
        return dataclasses.asdict(analysis)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
