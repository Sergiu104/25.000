import argparse
import csv
import json
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

API_BASE_URL = "https://wger.de/api/v2/exerciseinfo/"
DEFAULT_LANGUAGE = 2  # English in wger
DEFAULT_LIMIT = 100

VALID_GOALS = "FatLoss|Definition|MuscleGain|Fitness"

CATEGORY_TO_MUSCLE_GROUP = {
    "abs": "Core",
    "arms": "Arms",
    "back": "Back",
    "calves": "Legs",
    "chest": "Chest",
    "legs": "Legs",
    "shoulders": "Shoulders",
}

CATEGORY_TO_PATTERN = {
    "abs": "Core",
    "arms": "Isolation",
    "back": "Pull",
    "calves": "CalfRaise",
    "chest": "HorizontalPush",
    "legs": "Squat",
    "shoulders": "VerticalPush",
}

EQUIPMENT_NAME_MAP = {
    "barbell": "Barbell",
    "bench": "Bench",
    "dumbbell": "Dumbbell",
    "gym mat": "Bodyweight",
    "incline bench": "Bench",
    "kettlebell": "Kettlebell",
    "pull-up bar": "Bodyweight",
    "sz-bar": "Barbell",
    "swiss ball": "Bodyweight",
    "none": "Bodyweight",
    "bodyweight": "Bodyweight",
    "cable": "Cable",
    "machine": "Machine",
}


def slugify(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    value = value.encode("ascii", "ignore").decode("ascii")
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-+", "-", value)
    return value.strip("-")


def clean_text(value: str) -> str:
    value = re.sub(r"<[^>]+>", " ", value or "")
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def fetch_json(url: str, retries: int = 3, sleep_seconds: float = 1.0) -> dict[str, Any]:
    last_error: Exception | None = None

    for attempt in range(1, retries + 1):
        try:
            request = urllib.request.Request(
                url,
                headers={
                    "User-Agent": "IronVexelExerciseImporter/1.0 (+https://github.com/Sergiu104/25.000)",
                    "Accept": "application/json",
                },
            )
            with urllib.request.urlopen(request, timeout=30) as response:
                return json.loads(response.read().decode("utf-8"))
        except Exception as exc:  # noqa: BLE001 - intentionally broad for network retries
            last_error = exc
            if attempt < retries:
                time.sleep(sleep_seconds * attempt)

    raise RuntimeError(f"Nu am putut descărca datele wger: {last_error}")


def get_name(value: Any) -> str:
    if isinstance(value, dict):
        return str(value.get("name") or value.get("name_en") or "").strip()
    return str(value or "").strip()


def pick_equipment(item: dict[str, Any]) -> str:
    equipment = item.get("equipment") or []
    if isinstance(equipment, list) and equipment:
        first_name = get_name(equipment[0]).lower()
        return EQUIPMENT_NAME_MAP.get(first_name, get_name(equipment[0]) or "Other")
    return "Bodyweight"


def pick_category_name(item: dict[str, Any]) -> str:
    category = item.get("category") or {}
    return get_name(category).lower()


def pick_muscle_group(item: dict[str, Any]) -> str:
    category_name = pick_category_name(item)
    if category_name in CATEGORY_TO_MUSCLE_GROUP:
        return CATEGORY_TO_MUSCLE_GROUP[category_name]

    muscles = item.get("muscles") or []
    if isinstance(muscles, list) and muscles:
        first_muscle = get_name(muscles[0]).lower()
        if any(word in first_muscle for word in ["chest", "pectoralis"]):
            return "Chest"
        if any(word in first_muscle for word in ["back", "latissimus", "trapezius"]):
            return "Back"
        if any(word in first_muscle for word in ["shoulder", "deltoid"]):
            return "Shoulders"
        if any(word in first_muscle for word in ["quadriceps", "hamstring", "glute", "calf", "soleus"]):
            return "Legs"
        if any(word in first_muscle for word in ["biceps", "triceps", "forearm"]):
            return "Arms"
        if any(word in first_muscle for word in ["abs", "abdominal", "oblique"]):
            return "Core"

    return "Other"


def pick_movement_pattern(item: dict[str, Any], muscle_group: str, equipment: str) -> str:
    category_name = pick_category_name(item)
    if category_name in CATEGORY_TO_PATTERN:
        return CATEGORY_TO_PATTERN[category_name]

    name = str(item.get("name") or "").lower()

    if any(word in name for word in ["squat", "lunge", "leg press"]):
        return "Squat"
    if any(word in name for word in ["deadlift", "hip thrust", "good morning"]):
        return "Hinge"
    if any(word in name for word in ["row", "pull", "pulldown", "chin-up"]):
        return "Pull"
    if any(word in name for word in ["press", "push-up", "pushup"]):
        if muscle_group == "Shoulders":
            return "VerticalPush"
        return "HorizontalPush"
    if any(word in name for word in ["curl", "extension", "raise", "fly"]):
        return "Isolation"
    if muscle_group == "Core":
        return "Core"
    if equipment == "Bodyweight":
        return "Bodyweight"
    return "Other"


def pick_level(item: dict[str, Any]) -> str:
    name = str(item.get("name") or "").lower()
    if any(word in name for word in ["advanced", "one arm", "one-arm", "pistol", "muscle-up"]):
        return "Advanced"
    if any(word in name for word in ["beginner", "assisted", "machine"]):
        return "Beginner"
    return "Intermediate"


def pick_reps_and_rest(muscle_group: str, pattern: str, level: str) -> tuple[int, int, int, int]:
    if pattern == "Core":
        return 3, 12, 20, 60
    if pattern in {"Isolation", "CalfRaise"}:
        return 3, 12, 15, 75
    if level == "Advanced":
        return 4, 6, 10, 120
    if muscle_group == "Legs":
        return 3, 8, 12, 120
    return 3, 8, 12, 90


def build_tags(item: dict[str, Any], muscle_group: str, equipment: str, pattern: str) -> str:
    tags = ["wger", muscle_group.lower(), equipment.lower(), pattern.lower()]

    muscles = item.get("muscles") or []
    if isinstance(muscles, list):
        for muscle in muscles[:3]:
            name = slugify(get_name(muscle))
            if name:
                tags.append(name)

    seen: set[str] = set()
    unique_tags = []
    for tag in tags:
        tag = slugify(tag)
        if tag and tag not in seen:
            seen.add(tag)
            unique_tags.append(tag)

    return "|".join(unique_tags)


def normalize_item(item: dict[str, Any]) -> dict[str, str] | None:
    name = clean_text(str(item.get("name") or ""))
    if not name:
        return None

    source_id = str(item.get("id") or item.get("uuid") or slugify(name))
    exercise_id = f"wger-{source_id}-{slugify(name)}"

    muscle_group = pick_muscle_group(item)
    equipment = pick_equipment(item)
    movement_pattern = pick_movement_pattern(item, muscle_group, equipment)
    level = pick_level(item)
    default_sets, reps_min, reps_max, rest_seconds = pick_reps_and_rest(muscle_group, movement_pattern, level)

    return {
        "id": exercise_id,
        "name": name,
        "muscleGroup": muscle_group,
        "equipment": equipment,
        "movementPattern": movement_pattern,
        "level": level,
        "goals": VALID_GOALS,
        "defaultSets": str(default_sets),
        "repsMin": str(reps_min),
        "repsMax": str(reps_max),
        "restSeconds": str(rest_seconds),
        "tags": build_tags(item, muscle_group, equipment, movement_pattern),
        "alternatives": "",
    }


def fetch_all_exercises(language: int, limit: int, max_pages: int | None) -> list[dict[str, Any]]:
    params = urllib.parse.urlencode({"language": language, "limit": limit})
    url: str | None = f"{API_BASE_URL}?{params}"
    results: list[dict[str, Any]] = []
    page = 0

    while url:
        page += 1
        if max_pages is not None and page > max_pages:
            break

        data = fetch_json(url)
        page_results = data.get("results") or []
        if not isinstance(page_results, list):
            raise RuntimeError("Răspuns wger invalid: results nu este listă")

        results.extend(page_results)
        print(f"Pagina {page}: +{len(page_results)} exerciții, total {len(results)}")
        url = data.get("next")

    return results


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    fieldnames = [
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

    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()
        writer.writerows(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Descarcă exerciții din wger și le convertește în CSV IronVexel.")
    parser.add_argument("--output", default="new_exercises_wger.csv", help="CSV-ul generat")
    parser.add_argument("--language", type=int, default=DEFAULT_LANGUAGE, help="ID limbă wger. Default: 2 = English")
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT, help="Număr exerciții per pagină API")
    parser.add_argument("--max-pages", type=int, default=None, help="Limită opțională pentru testare")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_path = Path(args.output)

    try:
        raw_exercises = fetch_all_exercises(language=args.language, limit=args.limit, max_pages=args.max_pages)

        rows: list[dict[str, str]] = []
        seen_ids: set[str] = set()
        skipped = 0

        for item in raw_exercises:
            row = normalize_item(item)
            if row is None:
                skipped += 1
                continue
            if row["id"] in seen_ids:
                skipped += 1
                continue
            seen_ids.add(row["id"])
            rows.append(row)

        write_csv(output_path, rows)
        print(f"CSV generat: {output_path}")
        print(f"Exerciții brute wger: {len(raw_exercises)}")
        print(f"Exerciții exportate: {len(rows)}")
        print(f"Exerciții sărite: {skipped}")
        return 0
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
