import json
import sys
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


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def validate_exercise(exercise: dict[str, Any], line_number: int) -> None:
    missing = [field for field in REQUIRED_FIELDS if field not in exercise]
    if missing:
        fail(f"Linia {line_number}: lipsesc câmpurile {missing}")

    if not isinstance(exercise["id"], str) or not exercise["id"].strip():
        fail(f"Linia {line_number}: id invalid")

    if not isinstance(exercise["name"], str) or not exercise["name"].strip():
        fail(f"Linia {line_number}: name invalid")

    if exercise["level"] not in VALID_LEVELS:
        fail(f"Linia {line_number}: level invalid {exercise['level']!r}")

    if not isinstance(exercise["goals"], list) or not exercise["goals"]:
        fail(f"Linia {line_number}: goals trebuie să fie listă negoală")

    invalid_goals = [goal for goal in exercise["goals"] if goal not in VALID_GOALS]
    if invalid_goals:
        fail(f"Linia {line_number}: goals invalide {invalid_goals}")

    for field in ["defaultSets", "repsMin", "repsMax", "restSeconds"]:
        if not isinstance(exercise[field], int):
            fail(f"Linia {line_number}: {field} trebuie să fie int")

    if exercise["defaultSets"] <= 0:
        fail(f"Linia {line_number}: defaultSets trebuie să fie > 0")

    if exercise["repsMin"] <= 0 or exercise["repsMax"] <= 0:
        fail(f"Linia {line_number}: repsMin/repsMax trebuie să fie > 0")

    if exercise["repsMin"] > exercise["repsMax"]:
        fail(f"Linia {line_number}: repsMin este mai mare decât repsMax")

    if exercise["restSeconds"] < 0:
        fail(f"Linia {line_number}: restSeconds nu poate fi negativ")

    for field in ["tags", "alternatives"]:
        if not isinstance(exercise[field], list):
            fail(f"Linia {line_number}: {field} trebuie să fie listă")


def main() -> int:
    catalog_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("iv_exercise_catalog_ro_en.jsonl")

    if not catalog_path.exists():
        fail(f"Nu există fișierul {catalog_path}")

    ids: set[str] = set()
    total = 0

    with catalog_path.open("r", encoding="utf-8") as file:
        for line_number, raw_line in enumerate(file, start=1):
            line = raw_line.strip()
            if not line:
                continue

            try:
                exercise = json.loads(line)
            except json.JSONDecodeError as exc:
                fail(f"Linia {line_number}: JSON invalid: {exc}")

            validate_exercise(exercise, line_number)

            exercise_id = exercise["id"]
            if exercise_id in ids:
                fail(f"Linia {line_number}: id duplicat {exercise_id!r}")

            ids.add(exercise_id)
            total += 1

    print(f"OK: catalog valid. Total exerciții: {total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
