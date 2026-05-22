#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import gzip
import io
import json
import re
import sys
import urllib.request
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, Optional

DEFAULT_URL = "https://static.openfoodfacts.org/data/en.openfoodfacts.org.products.csv.gz"
DEFAULT_OUTPUT = Path("iv_food_catalog_ro.jsonl")
DEFAULT_LIMIT = 25000

NAME_KEYS = ("product_name_ro", "product_name", "generic_name_ro", "generic_name", "abbreviated_product_name")
CALORIE_KEYS = ("energy-kcal_100g", "energy_kcal_100g", "kcal_100g", "calories")
PROTEIN_KEYS = ("proteins_100g", "protein_100g", "protein")
CARB_KEYS = ("carbohydrates_100g", "carbs_100g", "carbs")
FAT_KEYS = ("fat_100g", "fat")
CODE_KEYS = ("code", "id", "barcode")
COUNTRY_KEYS = ("countries_tags", "countries_en", "countries")


def raise_csv_field_limit() -> None:
    limit = sys.maxsize
    while True:
        try:
            csv.field_size_limit(limit)
            return
        except OverflowError:
            limit = int(limit / 10)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    parser.add_argument("--prefer-country", default="romania")
    parser.add_argument("--timeout", type=int, default=90)
    return parser.parse_args()


def rows_from_openfoodfacts(url: str, timeout: int) -> Iterator[Dict[str, Any]]:
    raise_csv_field_limit()
    req = urllib.request.Request(url, headers={"User-Agent": "IronVexelCatalogGenerator/0.1"})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        with gzip.GzipFile(fileobj=response) as gz:
            stream = io.TextIOWrapper(gz, encoding="utf-8", errors="replace", newline="")
            reader = csv.DictReader(stream, delimiter="\t")
            for row in reader:
                yield dict(row)


def first_text(row: Dict[str, Any], keys: Iterable[str]) -> str:
    for key in keys:
        value = row.get(key)
        if value is not None and str(value).strip():
            return str(value).strip()
    return ""


def parse_number(value: Any) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().replace(",", ".")
    match = re.search(r"-?\d+(?:\.\d+)?", text)
    if not match:
        return None
    return float(match.group(0))


def first_number(row: Dict[str, Any], keys: Iterable[str]) -> Optional[float]:
    for key in keys:
        value = parse_number(row.get(key))
        if value is not None and value >= 0:
            return value
    return None


def normalize(value: str) -> str:
    table = str.maketrans("ăâîșşțţĂÂÎȘŞȚŢ", "aaissttAAISSTT")
    return value.translate(table).lower()


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", normalize(value)).strip("-") or "food"


def clean_name(name: str) -> str:
    name = re.sub(r"\s+", " ", name).strip()
    return (name[:1].upper() + name[1:])[:90] if name else ""


def is_bad_name(name: str) -> bool:
    clean = normalize(name)
    return not clean or any(part in clean for part in ("unknown", "undefined", "nutrition facts", "ingredients"))


def country_match(row: Dict[str, Any], country: str) -> bool:
    haystack = normalize(" ".join(first_text(row, (key,)) for key in COUNTRY_KEYS))
    preferred = normalize(country)
    return preferred in haystack or "romania" in haystack


def convert_row(row: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    name = clean_name(first_text(row, NAME_KEYS))
    if is_bad_name(name):
        return None
    calories = first_number(row, CALORIE_KEYS)
    protein = first_number(row, PROTEIN_KEYS)
    carbs = first_number(row, CARB_KEYS)
    fat = first_number(row, FAT_KEYS)
    if calories is None or protein is None or carbs is None or fat is None:
        return None
    if calories < 0 or protein < 0 or carbs < 0 or fat < 0:
        return None
    code = first_text(row, CODE_KEYS)
    food_id = f"off-{code}" if code.isdigit() and len(code) >= 6 else f"local-{slugify(name)}"

    def macro(value: float) -> float | int:
        rounded = round(value, 1)
        return int(rounded) if rounded.is_integer() else rounded

    return {"id": food_id, "name": name, "calories": int(round(calories)), "protein": macro(protein), "carbs": macro(carbs), "fat": macro(fat)}


def add_unique(food: Dict[str, Any], result: list[Dict[str, Any]], seen_ids: set[str], seen_names: set[str], limit: int) -> bool:
    item_id = str(food["id"])
    name_key = slugify(str(food["name"]))
    if item_id in seen_ids or name_key in seen_names:
        return False
    seen_ids.add(item_id)
    seen_names.add(name_key)
    result.append(food)
    return len(result) >= limit


def write_jsonl(path: Path, foods: list[Dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for food in foods:
            handle.write(json.dumps(food, ensure_ascii=False, separators=(",", ":")) + "\n")


def main() -> int:
    opts = parse_args()
    preferred: list[Dict[str, Any]] = []
    global_items: list[Dict[str, Any]] = []
    scanned = 0
    valid = 0
    for row in rows_from_openfoodfacts(opts.url, opts.timeout):
        scanned += 1
        food = convert_row(row)
        if food is None:
            continue
        valid += 1
        if country_match(row, opts.prefer_country):
            preferred.append(food)
        else:
            global_items.append(food)
        if len(preferred) >= opts.limit * 2:
            break
        if scanned % 250000 == 0:
            print(f"scanned={scanned} valid={valid} preferred={len(preferred)}", file=sys.stderr)

    result: list[Dict[str, Any]] = []
    seen_ids: set[str] = set()
    seen_names: set[str] = set()
    for food in preferred + global_items:
        if add_unique(food, result, seen_ids, seen_names, opts.limit):
            break
    write_jsonl(opts.output, result)
    print(f"Rows scanned: {scanned}")
    print(f"Valid rows: {valid}")
    print(f"Exported foods: {len(result)}")
    print(f"Output: {opts.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
