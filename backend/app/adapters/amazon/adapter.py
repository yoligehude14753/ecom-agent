from app.adapters.base import BasePlatformAdapter, ProductListing, ReviewItem, AdCampaign
from app.adapters.amazon.auth import sp_api_request
from app.adapters.amazon.scraper import scrape_product, scrape_reviews, scrape_best_sellers
from app.core.config import get_settings

settings = get_settings()

BEST_SELLERS_CATEGORIES = {
    "electronics": "https://www.amazon.com/Best-Sellers-Electronics/zgbs/electronics/",
    "home": "https://www.amazon.com/Best-Sellers-Home-Kitchen/zgbs/kitchen/",
    "sports": "https://www.amazon.com/Best-Sellers-Sports-Outdoors/zgbs/sporting-goods/",
    "toys": "https://www.amazon.com/Best-Sellers-Toys-Games/zgbs/toys-and-games/",
    "beauty": "https://www.amazon.com/Best-Sellers-Beauty/zgbs/beauty/",
    "health": "https://www.amazon.com/Best-Sellers-Health-Personal-Care/zgbs/hpc/",
    "clothing": "https://www.amazon.com/Best-Sellers-Clothing/zgbs/apparel/",
    "pet": "https://www.amazon.com/Best-Sellers-Pet-Supplies/zgbs/pet-supplies/",
    "tools": "https://www.amazon.com/Best-Sellers-Tools-Home-Improvement/zgbs/hi/",
    "office": "https://www.amazon.com/Best-Sellers-Office-Products/zgbs/office-products/",
}


class AmazonAdapter(BasePlatformAdapter):

    @property
    def platform_name(self) -> str:
        return "amazon"

    async def get_product(self, product_id: str) -> ProductListing:
        return await scrape_product(product_id)

    async def search_products(self, keyword: str, category: str = "", limit: int = 50) -> list[ProductListing]:
        # SP-API catalog items search
        params = {
            "keywords": keyword,
            "marketplaceIds": settings.AMAZON_MARKETPLACE_ID,
        }
        if category:
            params["includedData"] = "summaries,salesRanks"
        try:
            data = await sp_api_request("GET", "/catalog/2022-04-01/items", params=params)
            items = data.get("items", [])[:limit]
            results = []
            for item in items:
                summary = item.get("summaries", [{}])[0]
                asin = item.get("asin", "")
                results.append(ProductListing(
                    asin=asin,
                    title=summary.get("itemName", ""),
                    brand=summary.get("brand", ""),
                    price=0.0,
                    currency="USD",
                    bsr_rank=None,
                    bsr_category=None,
                    review_count=0,
                    rating=0.0,
                    marketplace=settings.AMAZON_MARKETPLACE_ID,
                ))
            return results
        except Exception:
            return []

    async def get_best_sellers(self, category: str, limit: int = 100) -> list[ProductListing]:
        url = BEST_SELLERS_CATEGORIES.get(category.lower())
        if not url:
            url = f"https://www.amazon.com/Best-Sellers/zgbs/{category}/"
        raw = await scrape_best_sellers(url, limit)
        return [
            ProductListing(
                asin=item["asin"],
                title=item["title"],
                brand="",
                price=item["price"],
                currency="USD",
                bsr_rank=item["rank"],
                bsr_category=category,
                review_count=0,
                rating=item["rating"],
                marketplace=settings.AMAZON_MARKETPLACE_ID,
            )
            for item in raw
        ]

    async def get_reviews(self, product_id: str, max_pages: int = 5) -> list[ReviewItem]:
        return await scrape_reviews(product_id, max_pages)

    async def create_listing(self, listing: dict) -> dict:
        # SP-API listings items PUT
        seller_id = listing.get("seller_id", "")
        sku = listing.get("sku", "")
        body = listing.get("body", {})
        return await sp_api_request(
            "PUT",
            f"/listings/2021-08-01/items/{seller_id}/{sku}",
            params={"marketplaceIds": settings.AMAZON_MARKETPLACE_ID},
            json=body,
        )

    async def get_ad_campaigns(self) -> list[AdCampaign]:
        # Amazon Advertising API — Sponsored Products campaigns
        import httpx
        from app.adapters.amazon.auth import get_lwa_access_token

        token = await get_lwa_access_token()
        headers = {
            "Amazon-Advertising-API-ClientId": settings.AMAZON_ADS_CLIENT_ID,
            "Amazon-Advertising-API-Scope": settings.AMAZON_ADS_PROFILE_ID,
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(
                "https://advertising-api.amazon.com/v2/sp/campaigns",
                headers=headers,
            )
            resp.raise_for_status()
            raw = resp.json()

        campaigns = []
        for c in raw:
            campaigns.append(AdCampaign(
                campaign_id=str(c.get("campaignId", "")),
                name=c.get("name", ""),
                state=c.get("state", ""),
                budget=float(c.get("dailyBudget", 0)),
                spend=0.0,
                sales=0.0,
                acos=0.0,
                roas=0.0,
                clicks=0,
                impressions=0,
            ))
        return campaigns
