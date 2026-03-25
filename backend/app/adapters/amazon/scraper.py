import asyncio
import random
from typing import Optional
from playwright.async_api import async_playwright, Page, Browser
from app.core.config import get_settings
from app.adapters.base import ProductListing, ReviewItem
from app.core.logging import logger

settings = get_settings()

MARKETPLACE_DOMAINS = {
    "ATVPDKIKX0DER": "amazon.com",
    "A1F83G8C2ARO7P": "amazon.co.uk",
    "A1PA6795UKMFR9": "amazon.de",
    "A13V1IB3VIYZZH": "amazon.fr",
    "A1RKKUPIHCS9HS": "amazon.es",
    "APJ6JRA9NG5V4": "amazon.it",
    "A1VC38T7YXB528": "amazon.co.jp",
}

USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
]


def _get_domain(marketplace_id: str) -> str:
    return MARKETPLACE_DOMAINS.get(marketplace_id, "amazon.com")


async def _make_browser(playwright) -> Browser:
    launch_args = {
        "headless": settings.SCRAPER_HEADLESS,
        "args": [
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-blink-features=AutomationControlled",
        ],
    }
    if settings.SCRAPER_PROXY_URL:
        launch_args["proxy"] = {"server": settings.SCRAPER_PROXY_URL}
    return await playwright.chromium.launch(**launch_args)


async def _new_page(browser: Browser) -> Page:
    context = await browser.new_context(
        user_agent=random.choice(USER_AGENTS),
        viewport={"width": 1366, "height": 768},
        locale="en-US",
    )
    page = await context.new_page()
    await page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
        window.chrome = { runtime: {} };
    """)
    return page


async def scrape_product(asin: str, marketplace_id: Optional[str] = None) -> ProductListing:
    domain = _get_domain(marketplace_id or settings.AMAZON_MARKETPLACE_ID)
    url = f"https://www.{domain}/dp/{asin}"

    async with async_playwright() as p:
        browser = await _make_browser(p)
        page = await _new_page(browser)
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(random.uniform(1.5, 3.0))

            title = await page.text_content("#productTitle") or ""
            title = title.strip()

            price_el = await page.query_selector(".a-price .a-offscreen")
            price_str = await price_el.text_content() if price_el else "0"
            price = float(price_str.replace("$", "").replace(",", "").strip() or 0)

            brand_el = await page.query_selector("#bylineInfo")
            brand = await brand_el.text_content() if brand_el else ""
            brand = brand.replace("Brand: ", "").replace("Visit the ", "").replace(" Store", "").strip()

            # BSR
            bsr_rank = None
            bsr_category = None
            bsr_el = await page.query_selector("#SalesRank, #detailBulletsWrapper_feature_div")
            if bsr_el:
                bsr_text = await bsr_el.text_content() or ""
                import re
                m = re.search(r"#([\d,]+)\s+in\s+([^\(]+)", bsr_text)
                if m:
                    bsr_rank = int(m.group(1).replace(",", ""))
                    bsr_category = m.group(2).strip()

            # Reviews
            review_count = 0
            rating = 0.0
            rc_el = await page.query_selector("#acrCustomerReviewText")
            if rc_el:
                rc_text = await rc_el.text_content() or ""
                import re
                m = re.search(r"([\d,]+)", rc_text)
                if m:
                    review_count = int(m.group(1).replace(",", ""))
            ra_el = await page.query_selector(".a-icon-alt")
            if ra_el:
                ra_text = await ra_el.text_content() or ""
                import re
                m = re.search(r"([\d.]+)", ra_text)
                if m:
                    rating = float(m.group(1))

            # Bullet points
            bullets = []
            bullet_els = await page.query_selector_all("#feature-bullets .a-list-item")
            for el in bullet_els:
                text = await el.text_content()
                if text:
                    bullets.append(text.strip())

            # Images
            images = []
            img_els = await page.query_selector_all("#altImages img")
            for el in img_els[:6]:
                src = await el.get_attribute("src")
                if src and "sprite" not in src:
                    images.append(src.replace("._SS40_", "._SL500_"))

            return ProductListing(
                asin=asin,
                title=title,
                brand=brand,
                price=price,
                currency="USD",
                bsr_rank=bsr_rank,
                bsr_category=bsr_category,
                review_count=review_count,
                rating=rating,
                images=images,
                bullet_points=bullets,
                marketplace=marketplace_id or settings.AMAZON_MARKETPLACE_ID,
            )
        finally:
            await browser.close()


async def scrape_reviews(asin: str, max_pages: int = 5) -> list[ReviewItem]:
    domain = _get_domain(settings.AMAZON_MARKETPLACE_ID)
    reviews: list[ReviewItem] = []

    async with async_playwright() as p:
        browser = await _make_browser(p)
        page = await _new_page(browser)
        try:
            for page_num in range(1, max_pages + 1):
                url = f"https://www.{domain}/product-reviews/{asin}?pageNumber={page_num}&sortBy=recent"
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                await asyncio.sleep(random.uniform(1.5, 2.5))

                review_els = await page.query_selector_all('[data-hook="review"]')
                if not review_els:
                    break

                for el in review_els:
                    rid = await el.get_attribute("id") or ""
                    rating_el = await el.query_selector('[data-hook="review-star-rating"] .a-icon-alt')
                    rating_text = await rating_el.text_content() if rating_el else "0"
                    import re
                    rm = re.search(r"([\d.]+)", rating_text or "")
                    rating = int(float(rm.group(1))) if rm else 0

                    title_el = await el.query_selector('[data-hook="review-title"]')
                    title = await title_el.text_content() if title_el else ""

                    body_el = await el.query_selector('[data-hook="review-body"]')
                    body = await body_el.text_content() if body_el else ""

                    author_el = await el.query_selector(".a-profile-name")
                    author = await author_el.text_content() if author_el else ""

                    date_el = await el.query_selector('[data-hook="review-date"]')
                    date = await date_el.text_content() if date_el else ""

                    vp_el = await el.query_selector('[data-hook="avp-badge"]')
                    verified = vp_el is not None

                    helpful_el = await el.query_selector('[data-hook="helpful-vote-statement"]')
                    helpful_text = await helpful_el.text_content() if helpful_el else ""
                    hm = re.search(r"(\d+)", helpful_text)
                    helpful = int(hm.group(1)) if hm else 0

                    reviews.append(ReviewItem(
                        review_id=rid,
                        asin=asin,
                        rating=rating,
                        title=title.strip(),
                        body=body.strip(),
                        author=author.strip(),
                        date=date.strip(),
                        verified_purchase=verified,
                        helpful_votes=helpful,
                    ))

                logger.info("scraped_reviews_page", asin=asin, page=page_num, count=len(review_els))
        finally:
            await browser.close()

    return reviews


async def scrape_best_sellers(category_url: str, limit: int = 100) -> list[dict]:
    """Scrape Amazon Best Sellers page for a category URL."""
    async with async_playwright() as p:
        browser = await _make_browser(p)
        page = await _new_page(browser)
        items = []
        try:
            await page.goto(category_url, wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(random.uniform(2, 3))

            product_els = await page.query_selector_all(".zg-grid-general-faceout, .zg-item-immersion")
            import re
            for el in product_els[:limit]:
                link_el = await el.query_selector("a")
                href = await link_el.get_attribute("href") if link_el else ""
                asin_m = re.search(r"/dp/([A-Z0-9]{10})", href or "")
                asin = asin_m.group(1) if asin_m else ""

                rank_el = await el.query_selector(".zg-bdg-text")
                rank_text = await rank_el.text_content() if rank_el else "0"
                rank = int(re.sub(r"[^\d]", "", rank_text) or 0)

                title_el = await el.query_selector("._cDEzb_p13n-sc-css-line-clamp-3_g3dy1, .p13n-sc-truncate-desktop-type2")
                title = await title_el.text_content() if title_el else ""

                price_el = await el.query_selector(".p13n-sc-price, ._cDEzb_p13n-sc-price_3mJ9Z")
                price_text = await price_el.text_content() if price_el else "0"
                price_m = re.search(r"[\d,.]+", price_text)
                price = float(price_m.group().replace(",", "")) if price_m else 0.0

                rating_el = await el.query_selector(".a-icon-alt")
                rating_text = await rating_el.text_content() if rating_el else "0"
                rating_m = re.search(r"([\d.]+)", rating_text)
                rating = float(rating_m.group(1)) if rating_m else 0.0

                if asin:
                    items.append({"asin": asin, "rank": rank, "title": title.strip(), "price": price, "rating": rating})

        finally:
            await browser.close()

    return items
