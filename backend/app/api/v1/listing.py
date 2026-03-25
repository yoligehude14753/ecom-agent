from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
import dataclasses

from app.modules.listing_generator import generate_listing, optimize_listing_from_asin

router = APIRouter(prefix="/listing", tags=["Listing Generator"])


class GenerateRequest(BaseModel):
    keyword: str
    product_details: Optional[dict] = None
    marketplace: str = "amazon.com"
    language: str = "en"


class OptimizeRequest(BaseModel):
    asin: str
    platform: str = "amazon"
    language: str = "en"


@router.post("/generate")
async def generate(req: GenerateRequest):
    listing = await generate_listing(
        keyword=req.keyword,
        product_details=req.product_details,
        marketplace=req.marketplace,
        language=req.language,
    )
    return dataclasses.asdict(listing)


@router.post("/optimize")
async def optimize(req: OptimizeRequest):
    try:
        listing = await optimize_listing_from_asin(
            asin=req.asin,
            platform=req.platform,
            language=req.language,
        )
        return dataclasses.asdict(listing)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/languages")
async def supported_languages():
    from app.modules.listing_generator.generator import SUPPORTED_LANGUAGES
    return {"languages": SUPPORTED_LANGUAGES}
