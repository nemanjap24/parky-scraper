"""Environment-backed scraper configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


def _float_setting(name: str, default: float, *, minimum: float = 0) -> float:
    raw = os.getenv(name, str(default)).strip()
    try:
        value = float(raw)
    except ValueError as exc:
        raise ValueError(f"{name} must be a number") from exc
    if value < minimum:
        raise ValueError(f"{name} must be at least {minimum}")
    return value


@dataclass(frozen=True)
class ScraperSettings:
    user_agent: str = "Mozilla/5.0"
    request_delay_seconds: float = 2.0
    page_timeout_seconds: float = 60.0
    classification_enabled: bool = False
    classification_confidence_threshold: float = 0.75


def get_scraper_settings() -> ScraperSettings:
    enabled = os.getenv("CLASSIFICATION_ENABLED", "false").strip().lower()
    if enabled not in {"true", "false"}:
        raise ValueError("CLASSIFICATION_ENABLED must be true or false")
    threshold = _float_setting("CLASSIFICATION_CONFIDENCE_THRESHOLD", 0.75)
    if threshold > 1:
        raise ValueError("CLASSIFICATION_CONFIDENCE_THRESHOLD must be at most 1")
    return ScraperSettings(
        user_agent=os.getenv("SCRAPER_USER_AGENT", "Mozilla/5.0").strip() or "Mozilla/5.0",
        request_delay_seconds=_float_setting("SCRAPER_REQUEST_DELAY_SECONDS", 2.0),
        page_timeout_seconds=_float_setting("SCRAPER_PAGE_TIMEOUT_SECONDS", 60.0),
        classification_enabled=enabled == "true",
        classification_confidence_threshold=threshold,
    )
