from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ProductListing:
    asin: str
    title: str
    brand: str
    price: float
    currency: str
    bsr_rank: Optional[int]
    bsr_category: Optional[str]
    review_count: int
    rating: float
    images: list[str] = field(default_factory=list)
    bullet_points: list[str] = field(default_factory=list)
    description: str = ""
    marketplace: str = ""


@dataclass
class ReviewItem:
    review_id: str
    asin: str
    rating: int
    title: str
    body: str
    author: str
    date: str
    verified_purchase: bool
    helpful_votes: int


@dataclass
class BSRSnapshot:
    asin: str
    rank: int
    category: str
    timestamp: str


@dataclass
class AdCampaign:
    campaign_id: str
    name: str
    state: str
    budget: float
    spend: float
    sales: float
    acos: float
    roas: float
    clicks: int
    impressions: int


class BasePlatformAdapter(ABC):
    """Pluggable adapter interface. Implement one class per e-commerce platform."""

    @property
    @abstractmethod
    def platform_name(self) -> str:
        ...

    @abstractmethod
    async def get_product(self, product_id: str) -> ProductListing:
        """Fetch a single product by its platform ID (ASIN for Amazon)."""
        ...

    @abstractmethod
    async def search_products(self, keyword: str, category: str = "", limit: int = 50) -> list[ProductListing]:
        """Keyword product search."""
        ...

    @abstractmethod
    async def get_best_sellers(self, category: str, limit: int = 100) -> list[ProductListing]:
        """Fetch best sellers list for a given category."""
        ...

    @abstractmethod
    async def get_reviews(self, product_id: str, max_pages: int = 5) -> list[ReviewItem]:
        """Fetch product reviews."""
        ...

    @abstractmethod
    async def create_listing(self, listing: dict) -> dict:
        """Create or update a product listing (requires seller API credentials)."""
        ...

    @abstractmethod
    async def get_ad_campaigns(self) -> list[AdCampaign]:
        """Fetch advertising campaigns (requires ads API credentials)."""
        ...
