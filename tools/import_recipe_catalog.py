#!/usr/bin/env python3
"""
IronVexel recipe catalog importer.

Converts CSV / JSON / JSONL recipe data into the JSONL format currently expected by Iv2.0 RecipeCatalogRepository:
{"id":"pui-orez-legume","title":"Piept de pui cu orez si legume","subtitle":"...","goalTags":["FatLoss"],"mealType":"Main","difficulty":"Easy","prepMinutes":25,"ingredients":[{"aliases":["local-piept-pui","pui"],"grams":150,"required":true}],"steps":["..."]}

Safe rule: write recipes only to recipe_catalog_ro.jsonl, never to iv_food_catalog_ro.jsonl.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

DEFAULT_GOAL_TAGS = ["FatLoss", "Definition", "MuscleGain", "Fitness"]


def normalize_key(key: str) -> str:
    return key.strip().lower().replace(" ", "_").replace("-", "_")


def normalize_row_keys(row: Dict[str, Any]) -> Dict[str, Any]:
    return {normalize_key(str(k)): v for k, v in row.items()}


def clean_text(value: Any) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    if text.lower() in {"nan", "none", "null"}:
        return ""
    return re.sub(r"\s+", " ", text)


def first_text(row: Dict[str, Any], keys: List[str]) -> str:
    for key in keys:
        text = clean_text(row.get(normalize_key(key)))
        if text:
            return text
    return ""


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
    return value or "recipe"


def parse_int(value: Any, default: int) -> int:
    text = clean_text(value).replace(",", ".")
    match = re.search(r"\d+", text)
    if not match:
        return default
    return max(0, int(match.group(0)))


def split_list(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [clean_text(item) for item in value if clean_text(item)]
    text = clean_text(value)
    if not text:
        return []
    parts = re.split(r"[|;]\s*", text)
    return [clean_text(part) for part in parts if clean_text(part)]


def parse_ingredients(value: Any) -> List[Dict[str, Any]]:
    """Accepts either JSON array or compact text.

    Text format examples:
      local-piept-pui|pui:150:true; local-orez-fiert|orez:200:true
      ton:120:true; cartofi:220:true; salata:100:false
    """
    if value is None:
        return []

    if isinstance(value, list):
        ingredients = []
        for item in value:
            if not isinstance(item, dict):
                continue
            aliases = split_list(item.get("aliases"))
            if not aliases:
                alias = clean_text(item.get("name") or item.get("foodId") or item.get("id"))
                aliases = [alias] if alias else []
            grams = parse_int(item.get("grams"), 100)
            required_raw = str(item.get("required", "true")).strip().lower()
            required = required_raw not in {"false", "0", "no", "nu"}
            if aliases and grams > 0:
                ingredients.append({"aliases": aliases, "grams": grams, "required": required})
        return ingredients

    text = clean_text(value)
    if not text:
        return []

    # Try full JSON first.
    if text.startswith("["):
        try:
            return parse_ingredients(json.loads(text))
        except json.JSONDecodeError:
            pass

    ingredients: List[Dict[str, Any]] = []
    for chunk in re.split(r";\s*", text):
        chunk = clean_text(chunk)
        if not chunk:
            continue
        bits = chunk.split(":")
        aliases = split_list(bits[0])
        grams = parse_int(bits[1], 100) if len(bits) > 1 else 100
        required = True
        if len(bits) > 2:
            required = bits[2].strip().lower() not in {"false", "0", "no", "nu"}
        if aliases and grams > 0:
            ingredients.append({"aliases": aliases, "grams": grams, "required": required})
    return ingredients


def build_recipe(raw_row: Dict[str, Any], source: str) -> Optional[Dict[str, Any]]:
    row = normalize_row_keys(raw_row)

    title = first_text(row, ["title", "name", "recipe_name", "reteta", "rețetă", "nume"])
    if not title:
        return None

    ingredients = parse_ingredients(row.get("ingredients") or row.get("ingrediente"))
    steps = split_list(row.get("steps") or row.get("instructions") or row.get("instructiuni") or row.get("instrucțiuni"))

    if not ingredients or not steps:
        return None

    raw_id = first_text(row, ["id", "recipe_id"])
    recipe_id = raw_id or slugify(title)

    goal_tags = split_list(row.get("goalTags") or row.get("goal_tags") or row.get("goals") or row.get("scopuri"))
    if not goal_tags:
        goal_tags = DEFAULT_GOAL_TAGS

    recipe: Dict[str, Any] = {
        "id": recipe_id,
        "title": title,
        "subtitle": first_text(row, ["subtitle", "description", "descriere"]) or "Rețetă simplă pentru IronVexel.",
        "goalTags": goal_tags,
        "mealType": first_text(row, ["mealType", "meal_type", "tip_masa", "masa"]) or "Main",
        "difficulty": first_text(row, ["difficulty", "dificultate"]) or "Easy",
        "prepMinutes": parse_int(row.get("prepMinutes") or row.get("prep_minutes") or row.get("minute") or row.get("timp"), 10),
        "ingredients": ingredients,
        "steps": steps,
    }

    if source:
        recipe["source"] = source

    return recipe


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
        recipes = value.get("recipes") or value.get("items") or value.get("data")
        if isinstance(recipes, list):
            for item in recipes:
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
    parser = argparse.ArgumentParser(description="Import recipe catalog data for IronVexel.")
    parser.add_argument("input", type=Path, help="Raw source file: CSV, JSON or JSONL")
    parser.add_argument("--output", type=Path, default=Path("recipe_catalog_ro.jsonl"))
    parser.add_argument("--append", type=Path, help="Existing recipe JSONL catalog to keep before imported items")
    parser.add_argument("--limit", type=int, default=5_000)
    parser.add_argument("--source", default="manual-recipe-import")
    args = parser.parse_args()

    if args.output.name == "iv_food_catalog_ro.jsonl":
        print("[ERROR] Refusing to write recipes over iv_food_catalog_ro.jsonl", file=sys.stderr)
        return 3

    if not args.input.exists():
        print(f"[ERROR] Input file not found: {args.input}", file=sys.stderr)
        return 2

    recipes: List[Dict[str, Any]] = []
    seen_ids = set()

    def add_recipe(recipe: Dict[str, Any]) -> None:
        recipe_id = str(recipe.get("id", "")).strip()
        if not recipe_id or recipe_id in seen_ids:
            return
        seen_ids.add(recipe_id)
        recipes.append(recipe)

    if args.append and args.append.exists():
        for raw in read_jsonl(args.append):
            recipe = build_recipe(raw, source=str(raw.get("source", "local-existing")))
            if recipe:
                add_recipe(recipe)
                if len(recipes) >= args.limit:
                    break

    imported = 0
    skipped = 0
    for row in read_input(args.input):
        recipe = build_recipe(row, source=args.source)
        if recipe:
            add_recipe(recipe)
            imported += 1
        else:
            skipped += 1
        if len(recipes) >= args.limit:
            break

    write_jsonl(recipes[: args.limit], args.output)

    print(f"[OK] Wrote {min(len(recipes), args.limit)} recipes to {args.output}")
    print(f"[INFO] Imported valid rows: {imported}")
    print(f"[INFO] Skipped invalid rows: {skipped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
