#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

DEFAULT_OUTPUT = Path("recipe_catalog_ro.jsonl")


def ing(aliases: list[str], grams: int, required: bool = True) -> dict[str, Any]:
    return {"aliases": aliases, "grams": grams, "required": required}


def rec(id: str, title: str, subtitle: str, tags: list[str], meal_type: str, minutes: int, ingredients: list[dict[str, Any]], steps: list[str]) -> dict[str, Any]:
    return {"id": id, "title": title, "subtitle": subtitle, "goalTags": tags, "mealType": meal_type, "difficulty": "Easy", "prepMinutes": minutes, "ingredients": ingredients, "steps": steps}


def catalog() -> list[dict[str, Any]]:
    all_goals = ["FatLoss", "Definition", "MuscleGain", "Fitness"]
    cut = ["FatLoss", "Definition", "Fitness"]
    bulk = ["MuscleGain", "Definition", "Fitness"]
    return [
        rec("pui-orez-legume", "Piept de pui cu orez și legume", "Proteină slabă, carbo controlat și legume.", all_goals, "Main", 25, [ing(["chicken-breast", "local-piept-pui", "piept pui", "pui"], 150), ing(["rice-cooked", "local-orez-fiert", "orez"], 200), ing(["legume", "salata", "salată", "rosii", "roșii", "castravete"], 100, False)], ["Încălzește puiul.", "Adaugă orezul cântărit.", "Completează cu legume sau salată."]),
        rec("pui-cartofi-iaurt", "Piept de pui cu cartofi și sos de iaurt", "Masă sățioasă, curată și ușor de logat.", cut, "Main", 25, [ing(["chicken-breast", "local-piept-pui", "pui"], 150), ing(["potatoes", "local-cartofi-fierti", "cartofi"], 220), ing(["greek-yogurt", "local-iaurt-grecesc-2", "iaurt"], 70, False)], ["Încălzește cartofii și puiul.", "Amestecă iaurtul cu sare/condimente.", "Servește totul într-un bowl."]),
        rec("salata-ton-cartofi", "Salată de ton cu cartofi", "Rețetă rece, rapidă, proteică și sățioasă.", cut, "Main", 10, [ing(["tuna", "local-ton-suc-propriu", "ton"], 120), ing(["potatoes", "local-cartofi-fierti", "cartofi"], 220), ing(["salata", "salată", "rosii", "roșii", "castravete", "legume"], 100, False)], ["Taie cartofii fierți.", "Adaugă tonul scurs.", "Completează cu salată/legume."]),
        rec("ton-orez-legume", "Ton cu orez și legume", "Masă rapidă, proteică, cu carbo simplu.", cut, "Main", 8, [ing(["tuna", "local-ton-suc-propriu", "ton"], 120), ing(["rice-cooked", "local-orez-fiert", "orez"], 180), ing(["porumb", "corn", "salata", "legume"], 80, False)], ["Încălzește orezul.", "Adaugă tonul scurs.", "Amestecă cu legume sau porumb."]),
        rec("omleta-cottage", "Omletă proteică cu brânză cottage", "Mic dejun proteic, rapid și sățios.", all_goals, "Breakfast", 12, [ing(["eggs", "local-oua", "oua", "ouă", "egg"], 120), ing(["cottage-cheese", "local-branza-cottage", "branza cottage", "brânză cottage"], 100, False), ing(["local-albus-ou", "albus", "albuș", "egg whites"], 100, False)], ["Bate ouăle.", "Gătește omleta la foc mediu.", "Adaugă cottage lângă sau peste omletă."]),
        rec("oua-cartofi-salata", "Ouă cu cartofi și salată", "Rețetă simplă, ieftină și sățioasă.", all_goals, "Main", 18, [ing(["eggs", "local-oua", "oua", "ouă"], 120), ing(["potatoes", "local-cartofi-fierti", "cartofi"], 200), ing(["salata", "salată", "rosii", "roșii", "legume"], 100, False)], ["Încălzește cartofii.", "Gătește ouăle după preferință.", "Servește cu salată."]),
        rec("iaurt-ovaz-banana", "Iaurt grecesc cu ovăz și banană", "Snack dulce cu proteine și energie.", all_goals, "Snack", 5, [ing(["greek-yogurt", "local-iaurt-grecesc-2", "iaurt grecesc", "iaurt"], 180), ing(["oats", "local-fulgi-ovaz", "ovaz", "ovăz"], 60), ing(["banana", "local-banana"], 120, False)], ["Pune iaurtul în bol.", "Adaugă ovăzul.", "Taie banana deasupra."]),
        rec("cottage-mar-ovaz", "Cottage cu măr și ovăz", "Snack rece, proteic și logic culinar.", cut, "Snack", 5, [ing(["cottage-cheese", "local-branza-cottage", "branza cottage", "brânză cottage"], 180), ing(["apple", "local-mar", "mar", "măr"], 150), ing(["oats", "local-fulgi-ovaz", "ovaz", "ovăz"], 40, False)], ["Pune cottage într-un bol.", "Taie mărul bucăți.", "Adaugă ovăz dacă vrei mai multă sațietate."]),
        rec("bowl-pui-orez-iaurt", "Bowl de pui cu orez și sos de iaurt", "Rețetă completă cu sos light.", all_goals, "Main", 25, [ing(["chicken-breast", "local-piept-pui", "pui"], 150), ing(["rice-cooked", "local-orez-fiert", "orez"], 180), ing(["greek-yogurt", "local-iaurt-grecesc-2", "iaurt"], 70), ing(["salata", "legume", "rosii", "roșii"], 80, False)], ["Pune orezul la bază.", "Adaugă puiul tăiat.", "Pune sosul de iaurt și legume."]),
        rec("banana-ovaz-iaurt", "Banană cu ovăz și iaurt", "Pre-workout simplu și rapid.", bulk, "Snack", 5, [ing(["banana", "local-banana"], 120), ing(["oats", "local-fulgi-ovaz", "ovaz", "ovăz"], 50), ing(["greek-yogurt", "local-iaurt-grecesc-2", "iaurt"], 120, False)], ["Taie banana.", "Adaugă ovăzul.", "Amestecă cu iaurt dacă îl ai."]),
        rec("orez-oua", "Orez cu ouă", "Masă rapidă pentru zile active.", bulk, "Main", 12, [ing(["rice-cooked", "local-orez-fiert", "orez"], 220), ing(["eggs", "local-oua", "oua", "ouă"], 120)], ["Încălzește orezul.", "Gătește ouăle separat.", "Amestecă sau servește separat."]),
        rec("ton-cottage-salata", "Salată proteică cu ton și cottage", "Proteină multă, calorii controlate.", cut, "Main", 7, [ing(["tuna", "local-ton-suc-propriu", "ton"], 120), ing(["cottage-cheese", "local-branza-cottage", "branza cottage"], 150), ing(["salata", "salată", "castravete", "rosii", "roșii"], 100, False)], ["Scurge tonul.", "Pune cottage lângă ton.", "Completează cu salată/legume."]),
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    recipes = catalog()
    with args.output.open("w", encoding="utf-8", newline="\n") as handle:
        for item in recipes:
            handle.write(json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n")
    print(f"Generated {len(recipes)} recipes -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
