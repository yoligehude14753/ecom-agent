from __future__ import annotations

import httpx
import time
from app.core.config import get_settings

settings = get_settings()

_TOKEN_CACHE: dict = {}


async def get_lwa_access_token() -> str:
    """Exchange refresh token for LWA access token with caching."""
    now = time.time()
    if _TOKEN_CACHE.get("expires_at", 0) > now + 60:
        return _TOKEN_CACHE["access_token"]

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://api.amazon.com/auth/o2/token",
            data={
                "grant_type": "refresh_token",
                "refresh_token": settings.AMAZON_REFRESH_TOKEN,
                "client_id": settings.AMAZON_CLIENT_ID,
                "client_secret": settings.AMAZON_CLIENT_SECRET,
            },
        )
        resp.raise_for_status()
        data = resp.json()
        _TOKEN_CACHE["access_token"] = data["access_token"]
        _TOKEN_CACHE["expires_at"] = now + data["expires_in"]
        return data["access_token"]


async def sp_api_request(
    method: str,
    path: str,
    params: dict | None = None,
    json: dict | None = None,
) -> dict:
    """Generic Amazon SP-API authenticated request."""
    token = await get_lwa_access_token()
    url = f"{settings.AMAZON_SP_API_ENDPOINT}{path}"
    headers = {
        "x-amz-access-token": token,
        "x-amz-date": time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()),
        "content-type": "application/json",
        "user-agent": "EcomAgent/1.0",
    }
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.request(method, url, headers=headers, params=params, json=json)
        resp.raise_for_status()
        return resp.json()
