from fastapi import APIRouter
from app.api.v1 import product_research, listing, reviews, monitor, ads

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(product_research.router)
api_router.include_router(listing.router)
api_router.include_router(reviews.router)
api_router.include_router(monitor.router)
api_router.include_router(ads.router)
