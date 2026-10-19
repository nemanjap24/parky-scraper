# parky-scraper

Scrapes grocery prices from JS-rendered e-shops and classifies products with Qwen over Ollama API.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Environment setup

1. Copy example env file:

```bash
cp .env.example .env
```

2. Fill values in `.env`:
- `OLLAMA_BASE_URL` (e.g. `https://nucaa.fei.stuba.sk:8082/ollama`)
- `OLLAMA_API_KEY` (token, nikdy ho necommituj)
- `OLLAMA_MODEL` (`qwen3:30b`)
- `CLASSIFICATION_CONFIDENCE_THRESHOLD` (default `0.75`)

## Run CLI

```bash
python -m qwen_classifier.cli \
  --products "K-Classic Dušená šunka výberová 100 g" "Coca-Cola 1,5 l" \
  --output qwen_classifier/output/classification.json \
  --mark-needs-review
```

## Expected JSON output

```json
[
  {
    "name": "K-Classic Dušená šunka výberová 100 g",
    "category": "masove_vyrobky",
    "subcategory": "sunka",
    "confidence": 0.98,
    "needs_review": false
  }
]
```

## Manual integration test

```bash
python -m qwen_classifier.cli \
  --products \
  "K-Classic Dušená šunka výberová 100 g" \
  "Pilos Extra jemný tvaroh 250 g" \
  "Coca-Cola 1,5 l" \
  "Horká čokoláda Milka 100 g" \
  "Mrazená zeleninová zmes Bonduelle 450 g" \
  "Čerstvé banány 1 kg" \
  "Pekárenský bagel sezamový 80 g" \
  "Klasické párky Tesco 400 g" \
  --output qwen_classifier/output/classification.json \
  --mark-needs-review
```

## Integration with scraper

When scraper output is a list of product objects, collect `raw_title` values and pass them to `QwenClassifier.classify`.

Example flow:
1. Read scraper results (list of dicts/objects).
2. Build input list: `products = [item["raw_title"] for item in scraper_results]`.
3. Call classifier: `classifier.classify(products, mark_needs_review=True)`.
4. Persist returned list to JSON for downstream processing.

## Troubleshooting

- **Missing env variables**: ensure `.env` exists and contains all required keys.
- **HTTP 401/403**: skontroluj hodnotu `OLLAMA_API_KEY` a prístup na endpoint
- **Timeout**: verify network connectivity and Ollama server responsiveness.
- **Validation errors**: inspect model JSON in `response` field, it must be strict JSON array.
