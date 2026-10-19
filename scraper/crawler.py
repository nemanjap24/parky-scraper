"""Crawl4AI browser integration for public Kosik product pages."""

from __future__ import annotations

import asyncio

from .config import ScraperSettings, get_scraper_settings


class CrawlError(RuntimeError):
    """Raised when a product page cannot be rendered."""


class KosikCrawler:
    def __init__(self, settings: ScraperSettings | None = None) -> None:
        self.settings = settings or get_scraper_settings()
        self._last_request_at: float | None = None

    async def crawl(self, url: str) -> str:
        if not url.startswith(("https://www.kosik.sk/", "https://kosik.sk/")):
            raise CrawlError("Only public kosik.sk product URLs are supported")
        try:
            from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
        except ImportError as exc:
            raise CrawlError("Crawl4AI is required for live scraping; install requirements.txt") from exc
        await self._delay()
        browser = BrowserConfig(headless=True, user_agent=self.settings.user_agent)
        run_config = CrawlerRunConfig(
            page_timeout=int(self.settings.page_timeout_seconds * 1000),
            wait_for="css:body",
        )
        try:
            async with AsyncWebCrawler(config=browser) as crawler:
                result = await crawler.arun(url=url, config=run_config)
        except asyncio.TimeoutError as exc:
            raise CrawlError(f"Timed out while loading {url}") from exc
        except Exception as exc:
            raise CrawlError(f"Failed to load {url}: {exc}") from exc
        content = getattr(result, "html", None) or getattr(result, "cleaned_html", None)
        if not isinstance(content, str) or not content.strip():
            raise CrawlError(f"Rendered page was empty: {url}")
        self._last_request_at = asyncio.get_running_loop().time()
        return content

    async def _delay(self) -> None:
        if self._last_request_at is None:
            return
        elapsed = asyncio.get_running_loop().time() - self._last_request_at
        remaining = self.settings.request_delay_seconds - elapsed
        if remaining > 0:
            await asyncio.sleep(remaining)
