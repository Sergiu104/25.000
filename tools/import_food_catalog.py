#!/usr/bin/env python3
"""
IronVexel food catalog importer.

Converts CSV / JSON / JSONL food data into the compact JSONL format expected by IronVexel:
{"id":"local-piept-pui","name":"Piept de pui","calories":165,"protein":31,"carbs":0,"fat":3.6}

Usage examples:
  python tools/import_food_catalog.py data/raw_foods.csv --output iv_food_catalog_ro.jsonl --limit 25000
  python tools/import_food_catalog.py data/raw_foods.jsonl --append iv_food_catalog_ro.jsonl --output iv_food_catalog_ro.jsonl --limit 25000
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

REQUIRED_OUTPUT_KEYS = ["id", "name", "calories", "protein", "carbs", "fat"]

NAME_KEYS = [
    "name",
    "product_name",
    "product_name_ro",
    "generic_name",
    "generic_name_ro",
    "food_name",
    "aliment",
    "nume",
]

BARCODE_KEYS = ["barcode", "code", "ean", "ean13", "gtin"]
BRAND_KEYS = ["brand", "brands", "marca"]
CATEGORY_KEYS = ["category", "categories", "categorie", "main_category"]

CALORIE_KEYS = [
    "calories",
    "kcal",
    "energy_kcal_100g",
    "energy-kcal_100g",
    "energy-kcal",
    "energy_kcal",
]
PROTEIN_KEYS = ["protein", "protein_g", "proteins_100g", "proteins", "proteine"]
CARB_KEYS = ["carbs", "carbs_g", "carbohydrates_100g", "carbohydrates", "glucide"]
FAT_KEYS = ["fat", "fat_g", "fat_100g", "grasimi", "fats"]


def normalize_key(key: str) -> str:
    return key.strip().lower().replace(" ", "_").replace("-", "_")


def normalize_row_keys(row: Dict[str, Any]) -> Dict[str, Any]:
    return {normalize_key(str(k)): v for k, v in row.items()}


def first_text(row: Dict[str, Any], keys: List[str]) -> str:
    for key in keys:
        value = row.get(normalize_key(key))
        if value is None:
            continue
        text = str(value).strip()
        if text and text.lower() not in {"nan", "none", "null"}:
            return text
    return ""


def parse_number(value: Any) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        number = float(value)
        return number if number >= 0 else None

    text = str(value).strip()
    if not text or text.lower() in {"nan", "none", "null", "-"}:
        return None

    # Handles Romanian comma decimals and values like "165 kcal".
    text = text.replace(",", ".")
    match = re.search(r"-?\d+(?:\.\d+)?", text)
    if not match:
        return None
    number = float(match.group(0))
    return number if number >= 0 else None


def first_number(row: Dict[str, Any], keys: List[str]) -> Optional[float]:
    for key in keys:
        value = row.get(normalize_key(key))
        number = parse_number(value)
        if number is not None:
            return number
    return None


def slugify(value: str) -> str:
    value = value.lower()
    replacements = {
        "ă": "a",
        "â": "a",
        "î": "i",
        "ș": "s",
        "ş": "s",
        "ț": "t",
        "ţ": "t",
    }
    for old, new in replacements.items():
        value = value.replace(old, new)
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    return value or "food"


def clean_name(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def build_food_item(raw_row: Dict[str, Any], source: str) -> Optional[Dict[str, Any]]:
    row = normalize_row_keys(raw_row)

    name = clean_name(first_text(row, NAME_KEYS))
    if not name:
        return None

    calories = first_number(row, CALORIE_KEYS)
    protein = first_number(row, PROTEIN_KEYS)
    carbs = first_number(row, CARB_KEYS)
    fat = first_number(row, FAT_KEYS)

    if calories is None or protein is None or carbs is None or fat is None:
        return None

    barcode = first_text(row, BARCODE_KEYS)
    raw_id = first_text(row, ["id", "food_id"])
    stable_id = raw_id or (f"off-{barcode}" if barcode else f"local-{slugify(name)}")

    item: Dict[str, Any] = {
        "id": stable_id,
        "name": name,
        "calories": int(round(calories)),
        "protein": round(float(protein), 2),
        "carbs": round(float(carbs), 2),
        "fat": round(float(fat), 2),
    }

    brand = first_text(row, BRAND_KEYS)
    category = first_text(row, CATEGORY_KEYS)
    if barcode:
        item["barcode"] = barcode
    if brand:
        item["brand"] = brand
    if category:
        item["category"] = category
    if source:
        item["source"] = source

    return item


def read_csv(path: Path) -> Iterable[Dict[str, Any]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        sample = handle.read(4096)
        handle.seek(0)
        dialect = csv.Sniffer().sniff(sample, delimiters=",;\t") if sample.strip() else csv.excel
        reader = csv.DictReader(handle, dialect=dialect)
        for row in reader:
            yield row


def read_jsonl(path: Path) -> Iterable[Dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            text = line.strip()
            if not text or text.startswith("#"):
                continue
            try:
                value = json.loads(text)
            except json.JSONDecodeError as exc:
                print(f"[WARN] Invalid JSONL line {line_number}: {exc}", file=sys.stderr)
                continue
            if isinstance(value, dict):
                yield value


def read_json(path: Path) -> Iterable[Dict[str, Any]]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(value, list):
        for item in value:
            if isinstance(item, dict):
                yield item
    elif isinstance(value, dict):
        products = value.get("products") or value.get("foods") or value.get("items")
        if isinstance(products, list):
            for item in products:
                if isinstance(item, dict):
                    yield item
        else:
            yield value


def read_input(path: Path) -> Iterable[Dict[str, Any]]:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return read_csv(path)
    if suffix in {".jsonl", ".ndjson"}:
        return read_jsonl(path)
    if suffix == ".json":
        return read_json(path)
    raise ValueError(f"Unsupported input file type: {suffix}. Use .csv, .json or .jsonl")


def write_jsonl(items: List[Dict[str, Any]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="\n") as handle:
        for item in items:
            handle.write(json.dumps(item, ensure_ascii=False, separators=(",", ":")))
            handle.write("\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Import food catalog data for IronVexel.")
    parser.add_argument("input", type=Path, help="Raw source file: CSV, JSON or JSONL")
    parser.add_argument("--output", type=Path, default=Path("iv_food_catalog_ro.jsonl"))
    parser.add_argument("--append", type=Path, help="Existing JSONL catalog to prepend/keep before imported items")
    parser.add_argument("--limit", type=int, default=25_000)
    parser.add_argument("--source", default="manual-import")
    args = parser.parse_args()

    if not args.input.exists():
        print(f"[ERROR] Input file not found: {args.input}", file=sys.stderr)
        return 2

    items: List[Dict[str, Any]] = []
    seen_ids = set()
    seen_barcodes = set()
    seen_names = set()

    def add_item(item: Dict[str, Any]) -> None:
        item_id = str(item.get("id", "")).strip()
        barcode = str(item.get("barcode", "")).strip()
        normalized_name = slugify(str(item.get("name", "")))

        if not item_id or item_id in seen_ids:
            return
        if barcode and barcode in seen_barcodes:
            return
        if normalized_name and normalized_name in seen_names:
            return

        seen_ids.add(item_id)
        if barcode:
            seen_barcodes.add(barcode)
        if normalized_name:
            seen_names.add(normalized_name)
        items.append(item)

    if args.append and args.append.exists():
        for raw in read_jsonl(args.append):
            item = build_food_item(raw, source=str(raw.get("source", "local-existing")))
            if item:
                add_item(item)
                if len(items) >= args.limit:
                    break

    imported = 0
    skipped = 0
    for row in read_input(args.input):
        item = build_food_item(row, source=args.source)
        if item:
            add_item(item)
            imported += 1
        else:
            skipped += 1
        if len(items) >= args.limit:
            break

    write_jsonl(items[: args.limit], args.output)

    print(f"[OK] Wrote {min(len(items), args.limit)} foods to {args.output}")
    print(f"[INFO] Imported valid rows: {imported}")
    print(f"[INFO] Skipped invalid rows: {skipped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
