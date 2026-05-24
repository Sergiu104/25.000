#!/usr/bin/env python3
"""Generate exactly 500 IronVexel recipe JSONL entries.

Output format matches Iv2.0 RecipeCatalogRepository:
{"id":"...","title":"...","subtitle":"...","goalTags":[...],"mealType":"Main","difficulty":"Easy","prepMinutes":25,"ingredients":[{"aliases":[...],"grams":150,"required":true}],"steps":[...]}

Safe rule: this script writes only recipe_catalog_ro.jsonl by default and refuses to write over iv_food_catalog_ro.jsonl.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

TARGET_COUNT = 500


def ingredient(aliases: List[str], grams: float, required: bool = True) -> Dict[str, Any]:
    return {"aliases": aliases, "grams": grams, "required": required}


PROTEINS = [
    {"key":"pui","name":"Pui","title":"piept de pui","aliases":["chicken-breast","local-piept-pui","piept pui","piept de pui","pui"],"grams":150,"tags":["FatLoss","Definition","MuscleGain","Fitness"],"prep":25},
    {"key":"pulpa-pui","name":"Pulpă de pui","title":"pulpă de pui","aliases":["chicken-thigh","pulpa pui","pulpă pui","pui"],"grams":160,"tags":["Definition","MuscleGain","Fitness"],"prep":30},
    {"key":"curcan","name":"Curcan","title":"piept de curcan","aliases":["turkey","turkey-breast","curcan","piept curcan","piept de curcan"],"grams":150,"tags":["FatLoss","Definition","MuscleGain","Fitness"],"prep":25},
    {"key":"ton","name":"Ton","title":"ton","aliases":["tuna","local-ton-suc-propriu","ton","ton in suc propriu","ton în suc propriu"],"grams":120,"tags":["FatLoss","Definition","Fitness"],"prep":10},
    {"key":"somon","name":"Somon","title":"somon","aliases":["salmon","somon"],"grams":140,"tags":["Definition","MuscleGain","Fitness"],"prep":25},
    {"key":"cod","name":"Cod","title":"cod","aliases":["cod","cod file","file cod","white fish","peste alb","pește alb"],"grams":160,"tags":["FatLoss","Definition","Fitness"],"prep":20},
    {"key":"sardine","name":"Sardine","title":"sardine","aliases":["sardines","sardine","sardina"],"grams":120,"tags":["FatLoss","Definition","Fitness"],"prep":8},
    {"key":"macrou","name":"Macrou","title":"macrou","aliases":["mackerel","macrou"],"grams":140,"tags":["Definition","Fitness"],"prep":20},
    {"key":"oua","name":"Ouă","title":"ouă","aliases":["eggs","local-oua","oua","ouă","egg"],"grams":120,"tags":["FatLoss","Definition","MuscleGain","Fitness"],"prep":12},
    {"key":"albus","name":"Albușuri","title":"albușuri","aliases":["egg whites","local-albus-ou","albus","albuș","albus ou"],"grams":180,"tags":["FatLoss","Definition","Fitness"],"prep":10},
    {"key":"cottage","name":"Cottage","title":"brânză cottage","aliases":["cottage-cheese","local-branza-cottage","branza cottage","brânză cottage","cottage"],"grams":180,"tags":["FatLoss","Definition","MuscleGain","Fitness"],"prep":6},
    {"key":"iaurt","name":"Iaurt grecesc","title":"iaurt grecesc","aliases":["greek-yogurt","local-iaurt-grecesc-2","iaurt grecesc","iaurt"],"grams":180,"tags":["FatLoss","Definition","MuscleGain","Fitness"],"prep":5},
    {"key":"tofu","name":"Tofu","title":"tofu","aliases":["tofu"],"grams":160,"tags":["FatLoss","Definition","Fitness"],"prep":18},
    {"key":"naut","name":"Năut","title":"năut","aliases":["chickpeas","naut","năut","local-naut"],"grams":180,"tags":["FatLoss","Definition","Fitness"],"prep":12},
    {"key":"fasole","name":"Fasole","title":"fasole","aliases":["beans","fasole","local-fasole"],"grams":180,"tags":["FatLoss","Definition","Fitness"],"prep":15},
    {"key":"linte","name":"Linte","title":"linte","aliases":["lentils","linte","local-linte"],"grams":180,"tags":["FatLoss","Definition","Fitness"],"prep":15},
    {"key":"vita-slaba","name":"Vită slabă","title":"vită slabă","aliases":["lean beef","beef","vita","vită","carne vita","carne vită"],"grams":140,"tags":["Definition","MuscleGain","Fitness"],"prep":30},
]

CARBS = [
    {"key":"orez","title":"orez","aliases":["rice-cooked","local-orez-fiert","orez","orez fiert"],"grams":180,"prep":15},
    {"key":"cartofi","title":"cartofi","aliases":["potatoes","local-cartofi-fierti","cartofi","cartofi fierti","cartofi fierți"],"grams":220,"prep":20},
    {"key":"cartofi-dulci","title":"cartofi dulci","aliases":["sweet potatoes","local-cartofi-dulci","cartofi dulci"],"grams":200,"prep":25},
    {"key":"paste","title":"paste","aliases":["pasta","paste","spaghetti","penne"],"grams":180,"prep":15},
    {"key":"lipie","title":"lipie","aliases":["wrap","lipie","tortilla"],"grams":70,"prep":5},
    {"key":"paine","title":"pâine","aliases":["bread","paine","pâine","toast"],"grams":80,"prep":5},
    {"key":"ovaz","title":"ovăz","aliases":["oats","local-fulgi-ovaz","ovaz","ovăz","fulgi ovaz","fulgi ovăz"],"grams":60,"prep":5},
    {"key":"cuscus","title":"cușcuș","aliases":["couscous","cuscus","cușcuș"],"grams":160,"prep":10},
    {"key":"quinoa","title":"quinoa","aliases":["quinoa"],"grams":160,"prep":15},
    {"key":"mamaliga","title":"mămăligă","aliases":["mamaliga","mămăligă","polenta"],"grams":220,"prep":15},
]

VEG = [
    {"title":"salată","aliases":["salata","salată","lettuce"],"grams":100},
    {"title":"roșii","aliases":["tomatoes","rosii","roșii","tomate"],"grams":100},
    {"title":"castraveți","aliases":["cucumber","castravete","castraveți","castraveti"],"grams":100},
    {"title":"broccoli","aliases":["broccoli"],"grams":120},
    {"title":"ardei","aliases":["pepper","ardei","ardei gras"],"grams":100},
    {"title":"spanac","aliases":["spinach","spanac"],"grams":80},
    {"title":"ciuperci","aliases":["mushrooms","ciuperci"],"grams":120},
    {"title":"legume mix","aliases":["legume","local-legume-mix","legume mix","mixed vegetables"],"grams":120},
    {"title":"porumb","aliases":["corn","porumb"],"grams":80},
    {"title":"mazăre","aliases":["peas","mazare","mazăre"],"grams":100},
]

SAUCES = [
    {"title":"sos de iaurt","aliases":["greek-yogurt","local-iaurt-grecesc-2","iaurt grecesc","iaurt"],"grams":60},
    {"title":"cottage","aliases":["cottage-cheese","local-branza-cottage","branza cottage","brânză cottage"],"grams":80},
    {"title":"hummus","aliases":["hummus","humus"],"grams":50},
    {"title":"ulei de măsline","aliases":["olive oil","ulei masline","ulei de masline","ulei de măsline"],"grams":10},
    {"title":"avocado","aliases":["avocado"],"grams":60},
]

FRUITS = [
    {"key":"banana","title":"banană","aliases":["banana","local-banana","banană"],"grams":120},
    {"key":"mar","title":"măr","aliases":["apple","local-mar","mar","măr"],"grams":150},
    {"key":"fructe-padure","title":"fructe de pădure","aliases":["berries","fructe padure","fructe de padure","fructe de pădure"],"grams":100},
    {"key":"capsuni","title":"căpșuni","aliases":["strawberries","capsuni","căpșuni"],"grams":120},
    {"key":"portocala","title":"portocală","aliases":["orange","portocala","portocală"],"grams":150},
]


def add_recipe(recipes: List[Dict[str, Any]], recipe: Dict[str, Any]) -> None:
    if len(recipes) >= TARGET_COUNT:
        return
    ids = {item["id"] for item in recipes}
    if recipe["id"] not in ids:
        recipes.append(recipe)


def make_recipe(recipe_id: str, title: str, subtitle: str, goals: List[str], meal_type: str, prep: int, ingredients: List[Dict[str, Any]], steps: List[str]) -> Dict[str, Any]:
    return {
        "id": recipe_id,
        "title": title,
        "subtitle": subtitle,
        "goalTags": goals,
        "mealType": meal_type,
        "difficulty": "Easy",
        "prepMinutes": int(prep),
        "ingredients": ingredients,
        "steps": steps,
    }


def generate() -> List[Dict[str, Any]]:
    recipes: List[Dict[str, Any]] = []

    main_styles = [
        ("bowl", "Bowl de {p} cu {c}", ["Pune baza într-un bol.", "Adaugă proteina gătită.", "Completează cu legume sau sos."]),
        ("salata", "Salată de {p} cu {c}", ["Pregătește ingredientele.", "Amestecă proteina cu baza.", "Adaugă legume și condimente."]),
        ("wrap", "Wrap cu {p} și {c}", ["Încălzește lipia dacă o folosești.", "Adaugă proteina și restul ingredientelor.", "Rulează și servește."]),
        ("farfurie", "{p} cu {c} și legume", ["Gătește proteina simplu.", "Adaugă baza cântărită.", "Servește cu legume."]),
        ("rapid", "{p} rapid cu {c}", ["Pregătește baza.", "Adaugă proteina.", "Condimentează simplu."]),
        ("mealprep", "Meal prep cu {p} și {c}", ["Porționează baza.", "Adaugă proteina.", "Păstrează la rece sau servește."]),
    ]

    for protein in PROTEINS:
        for carb in CARBS:
            if protein["key"] == "iaurt" and carb["key"] not in {"ovaz", "paine", "lipie"}:
                continue
            if protein["key"] == "cottage" and carb["key"] in {"paste", "mamaliga"}:
                continue
            style = main_styles[len(recipes) % len(main_styles)]
            veg = VEG[(len(recipes) * 3) % len(VEG)]
            sauce = SAUCES[(len(recipes) * 5) % len(SAUCES)]
            ingredients = [
                ingredient(protein["aliases"], protein["grams"], True),
                ingredient(carb["aliases"], carb["grams"], True),
                ingredient(veg["aliases"], veg["grams"], False),
            ]
            if protein["key"] != "iaurt" and len(recipes) % 2 == 0:
                ingredients.append(ingredient(sauce["aliases"], sauce["grams"], False))
            add_recipe(
                recipes,
                make_recipe(
                    f"{style[0]}-{protein['key']}-{carb['key']}",
                    style[1].format(p=protein["name"], c=carb["title"]),
                    "Rețetă simplă generată pentru frigiderul virtual.",
                    protein["tags"],
                    "Main",
                    max(protein["prep"], carb["prep"]) + 5,
                    ingredients,
                    style[2],
                ),
            )
            if len(recipes) >= 300:
                break
        if len(recipes) >= 300:
            break

    fish_keys = {"ton", "somon", "cod", "sardine", "macrou"}
    fish_carbs = [item for item in CARBS if item["key"] in {"orez", "cartofi", "lipie", "paine", "cuscus", "quinoa", "paste"}]
    fish_styles = [
        ("mediteranean", "{p} mediteranean cu {c}", ["Pregătește baza.", "Adaugă peștele.", "Pune legume proaspete și servește."]),
        ("rece", "{p} rece cu {c}", ["Scurge sau gătește peștele.", "Amestecă cu baza.", "Servește rece sau cald."]),
        ("light", "{p} light cu {c}", ["Gătește simplu.", "Ține grăsimile controlate.", "Completează cu salată."]),
    ]
    for protein in [item for item in PROTEINS if item["key"] in fish_keys]:
        for carb in fish_carbs:
            for style_key, style_title, steps in fish_styles:
                veg = VEG[(len(recipes) + 2) % len(VEG)]
                add_recipe(
                    recipes,
                    make_recipe(
                        f"{style_key}-{protein['key']}-{carb['key']}",
                        style_title.format(p=protein["name"], c=carb["title"]),
                        "Variantă bună pentru cine preferă pește în loc de carne grea.",
                        protein["tags"],
                        "Main",
                        max(protein["prep"], carb["prep"]),
                        [ingredient(protein["aliases"], protein["grams"], True), ingredient(carb["aliases"], carb["grams"], True), ingredient(veg["aliases"], veg["grams"], False)],
                        steps,
                    ),
                )
                if len(recipes) >= 390:
                    break
            if len(recipes) >= 390:
                break
        if len(recipes) >= 390:
            break

    breakfast_proteins = [item for item in PROTEINS if item["key"] in {"oua", "albus", "iaurt", "cottage"}]
    breakfast_carbs = [item for item in CARBS if item["key"] in {"ovaz", "paine", "lipie", "cartofi"}]
    breakfast_styles = [
        ("mic-dejun", "Mic dejun cu {p} și {c}", "Breakfast", ["Pregătește proteina.", "Adaugă carbohidratul.", "Servește rapid."]),
        ("snack", "Snack cu {p} și {c}", "Snack", ["Pune ingredientele într-un bol.", "Amestecă și ajustează cantitatea.", "Servește rece."]),
        ("preworkout", "Pre-workout cu {p} și {c}", "Snack", ["Pregătește porția.", "Mănâncă cu 60-90 minute înainte de sală.", "Păstrează gramajul controlat."]),
    ]
    for protein in breakfast_proteins:
        for carb in breakfast_carbs:
            for style_key, style_title, meal_type, steps in breakfast_styles:
                fruit = FRUITS[(len(recipes) + 1) % len(FRUITS)]
                extras = [ingredient(fruit["aliases"], fruit["grams"], False)] if carb["key"] == "ovaz" or protein["key"] in {"iaurt", "cottage"} else []
                add_recipe(
                    recipes,
                    make_recipe(
                        f"{style_key}-{protein['key']}-{carb['key']}-{fruit['key'] if extras else 'simplu'}",
                        style_title.format(p=protein["name"], c=carb["title"]),
                        "Opțiune simplă pentru dimineață sau gustare.",
                        protein["tags"],
                        meal_type,
                        max(protein["prep"], carb["prep"]),
                        [ingredient(protein["aliases"], protein["grams"], True), ingredient(carb["aliases"], carb["grams"], True)] + extras,
                        steps,
                    ),
                )
                if len(recipes) >= 460:
                    break
            if len(recipes) >= 460:
                break
        if len(recipes) >= 460:
            break

    veggie_proteins = [item for item in PROTEINS if item["key"] in {"tofu", "naut", "fasole", "linte", "oua", "albus", "cottage", "iaurt"}]
    veggie_carbs = [item for item in CARBS if item["key"] in {"orez", "cartofi", "paste", "lipie", "paine", "cuscus", "quinoa", "mamaliga", "ovaz"}]
    veggie_styles = [
        ("veggie-bowl", "Bowl vegetarian cu {p} și {c}"),
        ("veggie-wrap", "Wrap vegetarian cu {p} și {c}"),
        ("veggie-salata", "Salată vegetariană cu {p} și {c}"),
        ("veggie-rapid", "{p} cu {c} fără carne"),
    ]
    for protein in veggie_proteins:
        for carb in veggie_carbs:
            for style_key, style_title in veggie_styles:
                if protein["key"] == "iaurt" and carb["key"] not in {"ovaz", "paine"}:
                    continue
                if style_key == "veggie-wrap" and carb["key"] != "lipie":
                    continue
                veg = VEG[(len(recipes) + 4) % len(VEG)]
                sauce = SAUCES[(len(recipes) + 3) % len(SAUCES)]
                add_recipe(
                    recipes,
                    make_recipe(
                        f"{style_key}-{protein['key']}-{carb['key']}",
                        style_title.format(p=protein["name"], c=carb["title"]),
                        "Fără carne, potrivită când vrei o masă mai ușoară.",
                        protein["tags"],
                        "Main",
                        max(protein["prep"], carb["prep"]) + 3,
                        [ingredient(protein["aliases"], protein["grams"], True), ingredient(carb["aliases"], carb["grams"], True), ingredient(veg["aliases"], veg["grams"], False), ingredient(sauce["aliases"], sauce["grams"], False)],
                        ["Pregătește baza.", "Adaugă proteina vegetală sau lactatele.", "Completează cu legume și sos."],
                    ),
                )
                if len(recipes) >= TARGET_COUNT:
                    return recipes
    return recipes[:TARGET_COUNT]


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate IronVexel 500 recipe catalog.")
    parser.add_argument("--output", default="recipe_catalog_ro.jsonl", type=Path)
    args = parser.parse_args()

    if args.output.name == "iv_food_catalog_ro.jsonl":
        raise SystemExit("[ERROR] Refusing to write recipes over iv_food_catalog_ro.jsonl")

    recipes = generate()
    if len(recipes) != TARGET_COUNT:
        raise SystemExit(f"[ERROR] Expected {TARGET_COUNT} recipes, generated {len(recipes)}")

    args.output.write_text("".join(json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n" for item in recipes), encoding="utf-8")
    print(f"[OK] Wrote {len(recipes)} recipes to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
