# IronVexel Food Catalog

Repo separat pentru catalogul mare de alimente IronVexel.

## Fișierul principal

Aplicația IronVexel așteaptă un fișier JSONL compact:

```text
iv_food_catalog_ro.jsonl
```

Format pe fiecare linie:

```json
{"id":"local-piept-pui","name":"Piept de pui","calories":165,"protein":31,"carbs":0,"fat":3.6}
```

Reguli:

- un aliment pe linie;
- valori nutriționale per 100g;
- `calories` poate fi `0` pentru apă;
- fără array JSON mare;
- fără CSV în aplicație;
- recomandat: maximum 25.000 alimente pentru MVP.

## Link pentru IronVexel

Dacă repo-ul este public, link-ul raw va fi:

```text
https://raw.githubusercontent.com/Sergiu104/25.000/main/iv_food_catalog_ro.jsonl
```

În aplicația IronVexel, setează în `local.properties`:

```properties
FOOD_CATALOG_URL=https://raw.githubusercontent.com/Sergiu104/25.000/main/iv_food_catalog_ro.jsonl
```

## Atenție

Repo-ul trebuie să fie public pentru ca aplicația să poată descărca JSONL-ul fără login/token.

Dacă repo-ul rămâne private, aplicația Android nu va putea folosi URL-ul raw simplu.

## Cum generezi catalogul

Din repo-ul principal IronVexel:

```powershell
python tools/import_food_catalog.py data/raw_foods.csv --output iv_food_catalog_ro.jsonl --limit 25000
```

Sau, dacă vrei să păstrezi starter foods:

```powershell
python tools/import_food_catalog.py data/raw_foods.csv --append app/src/main/assets/food/iv_food_catalog_ro.jsonl --output iv_food_catalog_ro.jsonl --limit 25000
```

Apoi pui `iv_food_catalog_ro.jsonl` aici.
