from app.adapters.base import BasePlatformAdapter
from app.adapters.amazon.adapter import AmazonAdapter
from functools import lru_cache


@lru_cache
def get_adapter(platform: str = "amazon") -> BasePlatformAdapter:
    if platform == "amazon":
        return AmazonAdapter()
    raise ValueError(f"Unknown platform: {platform}")
