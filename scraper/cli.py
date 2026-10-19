"""Command-line interface for scraping Kosik products."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

from qwen_classifier.client import QwenClassifier

from .config import get_scraper_settings
from .pipeline import ScrapingPipeline


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scrape public Kosik product pages")
    parser.add_argument("--url", action="append", required=True, help="Kosik product URL; may be repeated")
    parser.add_argument("--output", required=True, help="Final JSON output path")
    parser.add_argument("--classify", action="store_true", help="Classify product names with Qwen")
    return parser.parse_args()


async def _run(args: argparse.Namespace) -> int:
    settings = get_scraper_settings()
    classifier = QwenClassifier() if args.classify else None
    try:
        pipeline = ScrapingPipeline(classifier=classifier, settings=settings)
        raw_products = await pipeline.scrape_many(args.url, classify=False)
        products = [pipeline.classify_product(product) for product in raw_products] if args.classify else raw_products
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        raw_payload = [product.model_dump(mode="json") for product in raw_products]
        payload = [product.model_dump(mode="json") for product in products]
        output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        raw_path = output.with_name(f"{output.stem}.raw{output.suffix}")
        raw_path.write_text(json.dumps(raw_payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Scraped {len(products)} product(s); saved {output}")
        return 0
    finally:
        if classifier is not None:
            classifier.close()


def main() -> int:
    args = parse_args()
    try:
        return asyncio.run(_run(args))
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
