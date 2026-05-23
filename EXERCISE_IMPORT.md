# Import exerciții IronVexel

Fișierul principal `iv_exercise_catalog_ro_en.jsonl` este în format JSONL: fiecare linie este un exercițiu JSON separat.

## 1. Creează CSV-ul de import

Copiază `new_exercises.template.csv` în `new_exercises.csv` și adaugă exercițiile noi acolo.

```bash
copy new_exercises.template.csv new_exercises.csv
```

Pe Git Bash / Linux / macOS:

```bash
cp new_exercises.template.csv new_exercises.csv
```

## 2. Reguli CSV

Separatorul este `;`.

Pentru câmpurile listă folosește `|`, nu virgulă:

```txt
FatLoss|Definition|MuscleGain|Fitness
bodyweight|push|home
machine-chest-press|db-bench-press
```

Coloane obligatorii:

```txt
id;name;muscleGroup;equipment;movementPattern;level;goals;defaultSets;repsMin;repsMax;restSeconds;tags;alternatives
```

Valori permise pentru `level`:

```txt
Beginner
Intermediate
Advanced
```

Valori permise pentru `goals`:

```txt
FatLoss
Definition
MuscleGain
Fitness
```

## 3. Generează catalogul combinat

```bash
python scripts/import_exercises_csv.py --csv new_exercises.csv
```

Asta creează:

```txt
iv_exercise_catalog_ro_en.merged.jsonl
```

## 4. Validează catalogul generat

```bash
python scripts/validate_exercise_catalog.py iv_exercise_catalog_ro_en.merged.jsonl
```

Dacă totul e OK, vei vedea ceva de genul:

```txt
OK: catalog valid. Total exerciții: 5008
```

## 5. Înlocuiește catalogul principal

Variantă automată, cu backup `.bak`:

```bash
python scripts/import_exercises_csv.py --csv new_exercises.csv --replace
```

Apoi validează din nou:

```bash
python scripts/validate_exercise_catalog.py
```

## 6. Commit

```bash
git add iv_exercise_catalog_ro_en.jsonl scripts/import_exercises_csv.py scripts/validate_exercise_catalog.py new_exercises.template.csv EXERCISE_IMPORT.md
git commit -m "Import exercise catalog tools"
git push
```

## Recomandare

Nu băga 5000 de exerciții duplicate doar ca să fie multe. Mai bine 500-1000 curate, cu alternative bune, decât 5000 de variante aproape identice care strică recomandările de antrenament.
