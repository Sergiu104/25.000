# IronVexel Food & Recipe Catalog

Repo separat pentru catalogul mare de alimente si retete IronVexel.

Scopul repo-ului:

- tine backup public pentru baza mare de alimente;
- ofera fisiere raw usor de descarcat de aplicatia Android;
- separa datele grele de repo-ul principal IronVexel;
- permite update la catalog fara rebuild complet al aplicatiei.

## Fisiere principale

Aplicatia IronVexel poate citi urmatoarele fisiere:

```text
iv_import_settings.json
iv_food_catalog_ro.jsonl
iv_recipe_catalog_ro.jsonl
```

### 1. Import settings

```text
iv_import_settings.json
```

Acesta este manifestul central. Contine URL-urile raw, versiunile de schema, limitele si regulile de import pentru alimente si retete.

Raw URL:

```text
https://raw.githubusercontent.com/Sergiu104/25.000/main/iv_import_settings.json
```

In aplicatia IronVexel, recomandat in `local.properties`:

```properties
FOOD_IMPORT_SETTINGS_URL=https://raw.githubusercontent.com/Sergiu104/25.000/main/iv_import_settings.json
FOOD_CATALOG_URL=https://raw.githubusercontent.com/Sergiu104/25.000/main/iv_food_catalog_ro.jsonl
RECIPE_CATALOG_URL=https://raw.githubusercontent.com/Sergiu104/25.000/main/iv_recipe_catalog_ro.jsonl
```

## Catalog alimente

Fisier:

```text
iv_food_catalog_ro.jsonl
```

Format pe fiecare linie:

```json
{"id":"local-piept-pui","name":"Piept de pui","calories":165,"protein":31,"carbs":0,"fat":3.6}
```

Reguli:

- un aliment pe linie;
- valori nutritionale per 100g;
- `calories` poate fi `0` doar pentru apa / produse similare fara energie;
- fara array JSON mare;
- fara CSV direct in aplicatie;
- recomandat: maximum 25.000 alimente pentru MVP;
- campuri minime: `id`, `name`, `calories`, `protein`, `carbs`, `fat`;
- campuri optionale recomandate: `brand`, `barcode`, `category`, `servingGrams`, `aliases`, `source`.

Raw URL:

```text
https://raw.githubusercontent.com/Sergiu104/25.000/main/iv_food_catalog_ro.jsonl
```

## Catalog retete

Fisier:

```text
iv_recipe_catalog_ro.jsonl
```

Format pe fiecare linie:

```json
{"id":"recipe-pui-orez-legume","name":"Pui cu orez si legume","servings":1,"ingredients":[{"foodId":"local-piept-pui","name":"Piept de pui","grams":150}],"instructions":["Gateste ingredientele."],"nutrition":{"calories":520,"protein":43,"carbs":58,"fat":10}}
```

Reguli:

- o reteta pe linie;
- `ingredients` este array de ingrediente;
- fiecare ingredient ar trebui sa aiba `foodId` cand exista alimentul in catalog;
- `name` ramane fallback pentru cautare daca nu exista `foodId`;
- `grams` reprezinta cantitatea folosita in reteta;
- `nutrition` este per portie de reteta, nu per 100g;
- campuri minime: `id`, `name`, `servings`, `ingredients`, `instructions`, `nutrition`;
- campuri optionale recomandate: `tags`, `difficulty`, `prepMinutes`, `cookMinutes`, `source`.

Raw URL:

```text
https://raw.githubusercontent.com/Sergiu104/25.000/main/iv_recipe_catalog_ro.jsonl
```

## Regula pentru Frigider Virtual

Retetele trebuie gandite ca sa functioneze cu Frigiderul Virtual:

1. aplicatia cauta ingredientele dupa `foodId`;
2. daca nu gaseste `foodId`, cauta dupa `barcode` sau nume normalizat;
3. daca utilizatorul consuma reteta, aplicatia scade ingredientele din frigider;
4. reteta consumata se adauga in Food Log;
5. Home Balance se actualizeaza din Food Log.

## Cum generezi catalogul mare

Din repo-ul principal IronVexel:

```powershell
python tools/import_food_catalog.py data/raw_foods.csv --output iv_food_catalog_ro.jsonl --limit 25000
```

Sau, daca vrei sa pastrezi starter foods:

```powershell
python tools/import_food_catalog.py data/raw_foods.csv --append app/src/main/assets/food/iv_food_catalog_ro.jsonl --output iv_food_catalog_ro.jsonl --limit 25000
```

Apoi pui `iv_food_catalog_ro.jsonl` aici.

## Atentie

Repo-ul trebuie sa fie public pentru ca aplicatia sa poata descarca fisierele raw fara login/token.

Daca repo-ul devine private, aplicatia Android nu va putea folosi URL-urile raw simple.

## Recomandare tehnica

In aplicatie, importul trebuie sa fie defensiv:

- daca fisierul remote este gol, pastreaza datele locale existente;
- daca o linie JSONL este invalida, sari peste linie;
- daca prea multe linii sunt invalide, opreste importul;
- daca exista duplicate, pastreaza varianta locala sau cea mai completa;
- cache local obligatoriu pentru folosire offline.
