import argparse
import csv
import json
import re
import shutil
import sys
import unicodedata
from pathlib import Path
from typing import Any

REQUIRED_FIELDS = [
    "id",
    "name",
    "muscleGroup",
    "equipment",
    "movementPattern",
    "level",
    "goals",
    "defaultSets",
    "repsMin",
    "repsMax",
    "restSeconds",
    "tags",
    "alternatives",
]

VALID_LEVELS = {"Beginner", "Intermediate", "Advanced"}
VALID_GOALS = {"FatLoss", "Definition", "MuscleGain", "Fitness"}

DEFAULT_GOALS = ["FatLoss", "Definition", "MuscleGain", "Fitness"]


def slugify(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    value = value.encode("ascii", "ignore").decode("ascii")
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-+", "-", value)
    return value.strip("-")


def split_list(value: str | None, default: list[str] | None = None) -> list[str]:
    if value is None or not str(value).strip():
        return list(default or [])
    return [item.strip() for item in str(value).split("|") if item.strip()]


def parse_int(value: str | None, fallback: int, field: str, row_number: int) -> int:
    if value is None or not str(value).strip():
        return fallback
    try:
        return int(str(value).strip())
    except ValueError as exc:
        raise ValueError(f"Linia {row_number}: {field} trebuie să fie număr întreg, primit: {value!r}") from exc


def load_jsonl(path: Path) -> tuple[list[dict[str, Any]], set[str]]:
    exercises: list[dict[str, Any]] = []
    ids: set[str] = set()

    if not path.exists():
        return exercises, ids

    with path.open("r", encoding="utf-8") as file:
        for line_number, raw_line in enumerate(file, start=1):
            line = raw_line.strip()
            if not line:
                continue

            try:
                exercise = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Catalog JSONL invalid la linia {line_number}: {exc}") from exc

            exercise_id = str(exercise.get("id", "")).strip()
            if not exercise_id:
                raise ValueError(f"Catalog invalid la linia {line_number}: lipsește id")
            if exercise_id in ids:
                raise ValueError(f"Catalog invalid: id duplicat {exercise_id!r}")

            ids.add(exercise_id)
            exercises.append(exercise)

    return exercises, ids


def normalize_csv_row(row: dict[str, str], existing_ids: set[str], row_number: int) -> dict[str, Any]:
    name = str(row.get("name", "")).strip()
    exercise_id = str(row.get("id", "")).strip() or slugify(name)

    if not exercise_id:
        raise ValueError(f"Linia {row_number}: lipsește id sau name")
    if not name:
        raise ValueError(f"Linia {row_number}: lipsește name")
    if exercise_id in existing_ids:
        raise ValueError(f"Linia {row_number}: id duplicat deja existent: {exercise_id!r}")

    level = str(row.get("level", "Beginner")).strip() or "Beginner"
    if level not in VALID_LEVELS:
        raise ValueError(f"Linia {row_number}: level invalid {level!r}. Valori permise: {sorted(VALID_LEVELS)}")

    goals = split_list(row.get("goals"), DEFAULT_GOALS)
    invalid_goals = [goal for goal in goals if goal not in VALID_GOALS]
    if invalid_goals:
        raise ValueError(f"Linia {row_number}: goals invalide {invalid_goals}. Valori permise: {sorted(VALID_GOALS)}")

    reps_min = parse_int(row.get("repsMin"), 8, "repsMin", row_number)
    reps_max = parse_int(row.get("repsMax"), 12, "repsMax", row_number)
    if reps_min > reps_max:
        raise ValueError(f"Linia {row_number}: repsMin ({reps_min}) este mai mare decât repsMax ({reps_max})")

    exercise = {
        "id": exercise_id,
        "name": name,
        "muscleGroup": str(row.get("muscleGroup", "Other")).strip() or "Other",
        "equipment": str(row.get("equipment", "Other")).strip() or "Other",
        "movementPattern": str(row.get("movementPattern", "Other")).strip() or "Other",
        "level": level,
        "goals": goals,
        "defaultSets": parse_int(row.get("defaultSets"), 3, "defaultSets", row_number),
        "repsMin": reps_min,
        "repsMax": reps_max,
        "restSeconds": parse_int(row.get("restSeconds"), 90, "restSeconds", row_number),
        "tags": split_list(row.get("tags")),
        "alternatives": split_list(row.get("alternatives")),
    }

    missing_fields = [field for field in REQUIRED_FIELDS if field not in exercise]
    if missing_fields:
        raise ValueError(f"Linia {row_number}: lipsesc câmpurile {missing_fields}")

    return exercise


def read_csv_exercises(csv_path: Path, existing_ids: set[str], delimiter: str) -> list[dict[str, Any]]:
    imported: list[dict[str, Any]] = []

    with csv_path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file, delimiter=delimiter)
        if not reader.fieldnames:
            raise ValueError("CSV-ul nu are header")

        missing_columns = [field for field in REQUIRED_FIELDS if field not in reader.fieldnames]
        if missing_columns:
            raise ValueError(f"CSV-ul nu are coloanele obligatorii: {missing_columns}")

        for row_number, row in enumerate(reader, start=2):
            if not any(str(value).strip() for value in row.values() if value is not None):
                continue

            exercise = normalize_csv_row(row, existing_ids, row_number)
            existing_ids.add(exercise["id"])
            imported.append(exercise)

    return imported


def write_jsonl(path: Path, exercises: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as file:
        for exercise in exercises:
            file.write(json.dumps(exercise, ensure_ascii=False, separators=(",", ":")) + "\n")


def backup_file(path: Path) -> Path:
    backup_path = path.with_suffix(path.suffix + ".bak")
    shutil.copy2(path, backup_path)
    return backup_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Importă exerciții din CSV în catalogul JSONL IronVexel.")
    parser.add_argument("--catalog", default="iv_exercise_catalog_ro_en.jsonl", help="Catalogul JSONL existent")
    parser.add_argument("--csv", default="new_exercises.csv", help="CSV-ul cu exerciții noi")
    parser.add_argument("--output", default="iv_exercise_catalog_ro_en.merged.jsonl", help="Fișierul JSONL generat")
    parser.add_argument("--delimiter", default=";", help="Delimiter CSV. Default: ;")
    parser.add_argument("--replace", action="store_true", help="Înlocuiește catalogul original după generare și face .bak")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    catalog_path = Path(args.catalog)
    csv_path = Path(args.csv)
    output_path = Path(args.output)

    if not catalog_path.exists():
        print(f"ERROR: nu există catalogul {catalog_path}", file=sys.stderr)
        return 1
    if not csv_path.exists():
        print(f"ERROR: nu există CSV-ul {csv_path}", file=sys.stderr)
        return 1

    try:
        existing_exercises, existing_ids = load_jsonl(catalog_path)
        imported_exercises = read_csv_exercises(csv_path, existing_ids, args.delimiter)
        merged_exercises = existing_exercises + imported_exercises
        write_jsonl(output_path, merged_exercises)

        if args.replace:
            backup_path = backup_file(catalog_path)
            shutil.move(str(output_path), str(catalog_path))
            print(f"Backup creat: {backup_path}")
            print(f"Catalog înlocuit: {catalog_path}")
        else:
            print(f"Fișier generat: {output_path}")

        print(f"Exerciții existente: {len(existing_exercises)}")
        print(f"Exerciții importate: {len(imported_exercises)}")
        print(f"Total final: {len(merged_exercises)}")
        return 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
