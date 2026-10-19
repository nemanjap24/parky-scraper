from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .client import QwenClassifier


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Classify grocery products with Qwen over Ollama API")
    parser.add_argument("--products", nargs="+", required=True, help="One or more product names")
    parser.add_argument("--output", required=True, help="Path to output JSON file")
    parser.add_argument(
        "--mark-needs-review",
        action="store_true",
        help="Mark products below CLASSIFICATION_CONFIDENCE_THRESHOLD with needs_review=true",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_path = Path(args.output)

    try:
        with QwenClassifier() as classifier:
            result = classifier.classify(args.products, mark_needs_review=args.mark_needs_review)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        payload = [item.model_dump(exclude_none=True) for item in result]
        output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
