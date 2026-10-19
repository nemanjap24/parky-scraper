"""Crawl4AI browser integration for public Kosik product pages."""

from __future__ import annotations

import asyncio
import hashlib
from pathlib import Path
from urllib.parse import urlparse

from .config import ScraperSettings, get_scraper_settings


class CrawlError(RuntimeError):
    """Raised when a product page cannot be rendered."""


class KosikCrawler:
    def __init__(
        self,
        settings: ScraperSettings | None = None,
        debug_output_dir: Path | None = Path("scraper/output/rendered"),
    ) -> None:
        self.settings = settings or get_scraper_settings()
        self.debug_output_dir = debug_output_dir
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
            wait_for="js:() => document.querySelector('#kosik-app2')?.innerText.trim().length > 50",
            delay_before_return_html=2,
        )
        try:
            async with AsyncWebCrawler(config=browser) as crawler:
                result = await crawler.arun(url=url, config=run_config)
        except asyncio.TimeoutError as exc:
            raise CrawlError(f"Timed out while loading {url}") from exc
        except Exception as exc:
            raise CrawlError(f"Failed to load {url}: {exc}") from exc
        if getattr(result, "success", True) is False:
            raise CrawlError(f"Page navigation failed for {url}")
        content = getattr(result, "html", None) or getattr(result, "cleaned_html", None)
        if not isinstance(content, str) or not content.strip():
            raise CrawlError(f"Rendered page was empty: {url}")
        self._save_debug_html(content, url)
        self._last_request_at = asyncio.get_running_loop().time()
        return content

    def _save_debug_html(self, content: str, url: str) -> None:
        if self.debug_output_dir is None:
            return
        path = urlparse(url).path.strip("/").replace("/", "_") or "page"
        digest = hashlib.sha256(url.encode("utf-8")).hexdigest()[:10]
        output_path = self.debug_output_dir / f"{path[:80]}-{digest}.html"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding="utf-8")

    async def _delay(self) -> None:
        if self._last_request_at is None:
            return
        elapsed = asyncio.get_running_loop().time() - self._last_request_at
        remaining = self.settings.request_delay_seconds - elapsed
        if remaining > 0:
            await asyncio.sleep(remaining)
