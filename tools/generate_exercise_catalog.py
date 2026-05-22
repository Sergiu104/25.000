#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

DEFAULT_OUTPUT = Path("exercise_catalog_ro.jsonl")

Exercise = Dict[str, Any]


def exercise(
    id: str,
    name: str,
    group: str,
    equipment: str,
    pattern: str,
    level: str,
    goals: List[str],
    sets: int,
    reps_min: int,
    reps_max: int,
    rest: int,
    tags: List[str] | None = None,
    alternatives: List[str] | None = None,
) -> Exercise:
    return {
        "id": id,
        "name": name,
        "muscleGroup": group,
        "equipment": equipment,
        "movementPattern": pattern,
        "level": level,
        "goals": goals,
        "defaultSets": sets,
        "repsMin": reps_min,
        "repsMax": reps_max,
        "restSeconds": rest,
        "tags": tags or [],
        "alternatives": alternatives or [],
    }


def catalog() -> List[Exercise]:
    fat_loss = ["FatLoss", "Definition", "Fitness"]
    muscle = ["MuscleGain", "Definition"]
    all_goals = ["FatLoss", "Definition", "MuscleGain", "Fitness"]

    return [
        # Chest
        exercise("machine-chest-press", "Chest press la aparat", "Chest", "Machine", "HorizontalPush", "Beginner", all_goals, 3, 10, 15, 90, ["safe", "gym", "press"], ["db-bench-press", "bench-press"]),
        exercise("db-bench-press", "Împins la piept cu gantere", "Chest", "Dumbbell", "HorizontalPush", "Beginner", all_goals, 3, 8, 12, 90, ["gym", "press"], ["machine-chest-press", "bench-press"]),
        exercise("bench-press", "Împins la piept cu bara", "Chest", "Barbell", "HorizontalPush", "Intermediate", muscle, 4, 6, 10, 120, ["compound", "strength"], ["db-bench-press", "machine-chest-press"]),
        exercise("incline-db-press", "Împins înclinat cu gantere", "Chest", "Dumbbell", "InclinePush", "Intermediate", all_goals, 3, 8, 12, 100, ["upper-chest"], ["incline-machine-press"]),
        exercise("incline-machine-press", "Împins înclinat la aparat", "Chest", "Machine", "InclinePush", "Beginner", all_goals, 3, 10, 14, 90, ["safe", "upper-chest"], ["incline-db-press"]),
        exercise("pec-deck", "Pec deck", "Chest", "Machine", "Fly", "Beginner", all_goals, 3, 12, 15, 75, ["isolation"], ["cable-fly"]),
        exercise("cable-fly", "Fluturări la cablu", "Chest", "Cable", "Fly", "Intermediate", all_goals, 3, 12, 16, 75, ["isolation", "control"], ["pec-deck"]),

        # Back
        exercise("lat-pulldown", "Tracțiuni la helcometru", "Back", "Cable", "VerticalPull", "Beginner", all_goals, 3, 10, 15, 90, ["safe", "lat"], ["assisted-pullup"]),
        exercise("assisted-pullup", "Tracțiuni asistate", "Back", "Machine", "VerticalPull", "Beginner", all_goals, 3, 8, 12, 100, ["bodyweight", "lat"], ["lat-pulldown"]),
        exercise("pullup", "Tracțiuni", "Back", "Bodyweight", "VerticalPull", "Advanced", ["MuscleGain", "Definition", "Fitness"], 4, 6, 12, 120, ["bodyweight", "compound"], ["assisted-pullup", "lat-pulldown"]),
        exercise("seated-cable-row", "Ramat la cablu din șezut", "Back", "Cable", "HorizontalPull", "Beginner", all_goals, 3, 10, 14, 90, ["safe", "row"], ["machine-row", "db-row"]),
        exercise("machine-row", "Ramat la aparat", "Back", "Machine", "HorizontalPull", "Beginner", all_goals, 3, 10, 14, 90, ["safe", "row"], ["seated-cable-row"]),
        exercise("db-row", "Ramat cu gantera", "Back", "Dumbbell", "HorizontalPull", "Intermediate", all_goals, 3, 8, 12, 100, ["row", "unilateral"], ["seated-cable-row"]),
        exercise("barbell-row", "Ramat cu bara", "Back", "Barbell", "HorizontalPull", "Advanced", muscle, 4, 6, 10, 120, ["compound", "strength"], ["machine-row", "seated-cable-row"]),
        exercise("straight-arm-pulldown", "Pulldown cu brațele drepte", "Back", "Cable", "IsolationPull", "Intermediate", all_goals, 3, 12, 16, 75, ["lat", "isolation"], ["lat-pulldown"]),

        # Legs
        exercise("leg-press", "Presă picioare", "Legs", "Machine", "Squat", "Beginner", all_goals, 3, 10, 15, 100, ["safe", "quad"], ["goblet-squat", "hack-squat"]),
        exercise("goblet-squat", "Genuflexiuni goblet", "Legs", "Dumbbell", "Squat", "Beginner", all_goals, 3, 10, 14, 90, ["foundation"], ["leg-press"]),
        exercise("hack-squat", "Hack squat", "Legs", "Machine", "Squat", "Intermediate", all_goals, 4, 8, 12, 120, ["quad", "machine"], ["leg-press"]),
        exercise("barbell-squat", "Genuflexiuni cu bara", "Legs", "Barbell", "Squat", "Advanced", muscle, 4, 5, 10, 150, ["compound", "strength"], ["leg-press", "hack-squat"]),
        exercise("leg-extension", "Extensii cvadriceps", "Legs", "Machine", "KneeExtension", "Beginner", all_goals, 3, 12, 16, 75, ["quad", "isolation"], ["leg-press"]),
        exercise("lying-leg-curl", "Flexii femurali culcat", "Legs", "Machine", "KneeFlexion", "Beginner", all_goals, 3, 10, 15, 80, ["hamstrings", "isolation"], ["seated-leg-curl"]),
        exercise("seated-leg-curl", "Flexii femurali șezut", "Legs", "Machine", "KneeFlexion", "Beginner", all_goals, 3, 10, 15, 80, ["hamstrings", "isolation"], ["lying-leg-curl"]),
        exercise("romanian-deadlift", "Îndreptări românești", "Legs", "Barbell", "HipHinge", "Intermediate", all_goals, 3, 8, 12, 120, ["hamstrings", "glutes", "hinge"], ["db-romanian-deadlift"]),
        exercise("db-romanian-deadlift", "Îndreptări românești cu gantere", "Legs", "Dumbbell", "HipHinge", "Beginner", all_goals, 3, 10, 14, 100, ["hamstrings", "hinge"], ["romanian-deadlift"]),
        exercise("calf-raise-machine", "Ridicări gambe la aparat", "Legs", "Machine", "CalfRaise", "Beginner", all_goals, 4, 12, 20, 70, ["calves"], ["standing-calf-raise"]),

        # Shoulders
        exercise("machine-shoulder-press", "Presă umeri la aparat", "Shoulders", "Machine", "VerticalPush", "Beginner", all_goals, 3, 10, 14, 90, ["safe", "press"], ["db-shoulder-press"]),
        exercise("db-shoulder-press", "Presă umeri cu gantere", "Shoulders", "Dumbbell", "VerticalPush", "Intermediate", all_goals, 3, 8, 12, 100, ["press"], ["machine-shoulder-press"]),
        exercise("barbell-overhead-press", "Presă militară cu bara", "Shoulders", "Barbell", "VerticalPush", "Advanced", muscle, 4, 5, 10, 130, ["compound", "strength"], ["machine-shoulder-press", "db-shoulder-press"]),
        exercise("lateral-raise", "Ridicări laterale", "Shoulders", "Dumbbell", "LateralRaise", "Beginner", all_goals, 3, 12, 18, 70, ["side-delt", "isolation"], ["cable-lateral-raise"]),
        exercise("cable-lateral-raise", "Ridicări laterale la cablu", "Shoulders", "Cable", "LateralRaise", "Intermediate", all_goals, 3, 12, 18, 70, ["side-delt", "constant-tension"], ["lateral-raise"]),
        exercise("rear-delt-fly", "Reverse fly pentru deltoid posterior", "Shoulders", "Machine", "RearDelt", "Beginner", all_goals, 3, 12, 18, 70, ["rear-delt"], ["face-pull"]),
        exercise("face-pull", "Face pull", "Shoulders", "Cable", "RearDelt", "Beginner", all_goals, 3, 12, 18, 70, ["rear-delt", "shoulder-health"], ["rear-delt-fly"]),

        # Arms
        exercise("cable-curl", "Flexii biceps la cablu", "Arms", "Cable", "Curl", "Beginner", all_goals, 3, 10, 15, 70, ["biceps"], ["db-curl"]),
        exercise("db-curl", "Flexii biceps cu gantere", "Arms", "Dumbbell", "Curl", "Beginner", all_goals, 3, 10, 14, 70, ["biceps"], ["cable-curl"]),
        exercise("hammer-curl", "Hammer curl", "Arms", "Dumbbell", "Curl", "Beginner", all_goals, 3, 10, 14, 70, ["biceps", "forearm"], ["rope-hammer-curl"]),
        exercise("triceps-pushdown", "Extensii triceps la cablu", "Arms", "Cable", "ElbowExtension", "Beginner", all_goals, 3, 10, 15, 70, ["triceps"], ["overhead-triceps-extension"]),
        exercise("overhead-triceps-extension", "Extensii triceps deasupra capului", "Arms", "Cable", "ElbowExtension", "Intermediate", all_goals, 3, 10, 14, 75, ["triceps", "long-head"], ["triceps-pushdown"]),
        exercise("dip-assisted", "Dips asistate", "Arms", "Machine", "Dip", "Intermediate", ["MuscleGain", "Definition", "Fitness"], 3, 8, 12, 100, ["triceps", "chest"], ["triceps-pushdown"]),

        # Core
        exercise("plank", "Plank", "Core", "Bodyweight", "AntiExtension", "Beginner", all_goals, 3, 30, 45, 60, ["core", "safe"], ["dead-bug"]),
        exercise("dead-bug", "Dead bug", "Core", "Bodyweight", "AntiExtension", "Beginner", all_goals, 3, 10, 14, 45, ["core", "control"], ["plank"]),
        exercise("cable-crunch", "Crunch la cablu", "Core", "Cable", "Crunch", "Intermediate", all_goals, 3, 12, 16, 60, ["abs"], ["machine-crunch"]),
        exercise("machine-crunch", "Crunch la aparat", "Core", "Machine", "Crunch", "Beginner", all_goals, 3, 12, 16, 60, ["abs", "safe"], ["cable-crunch"]),
        exercise("hanging-leg-raise", "Ridicări picioare la bară", "Core", "Bodyweight", "LegRaise", "Advanced", ["Definition", "Fitness"], 3, 8, 14, 70, ["abs", "advanced"], ["lying-leg-raise"]),
        exercise("lying-leg-raise", "Ridicări picioare culcat", "Core", "Bodyweight", "LegRaise", "Beginner", all_goals, 3, 10, 14, 60, ["abs"], ["hanging-leg-raise"]),
        exercise("farmer-walk", "Farmer walk", "Core", "Dumbbell", "Carry", "Intermediate", all_goals, 3, 30, 45, 75, ["core", "grip", "conditioning"], ["plank"]),

        # Cardio
        exercise("treadmill-walk", "Bandă mers alert", "Cardio", "CardioMachine", "SteadyState", "Beginner", fat_loss, 1, 15, 30, 60, ["cardio", "low-impact"], ["bike-steady"]),
        exercise("treadmill-incline", "Bandă înclinație", "Cardio", "CardioMachine", "SteadyState", "Beginner", fat_loss, 1, 12, 25, 60, ["cardio", "fat-loss"], ["treadmill-walk"]),
        exercise("bike-steady", "Bicicletă staționară", "Cardio", "CardioMachine", "SteadyState", "Beginner", fat_loss, 1, 15, 35, 60, ["cardio", "low-impact"], ["elliptical"]),
        exercise("elliptical", "Eliptică", "Cardio", "CardioMachine", "SteadyState", "Beginner", fat_loss, 1, 15, 35, 60, ["cardio", "low-impact"], ["bike-steady"]),
        exercise("stairmaster", "Stairmaster", "Cardio", "CardioMachine", "Conditioning", "Intermediate", ["FatLoss", "Definition", "Fitness"], 1, 8, 20, 60, ["cardio", "hard"], ["treadmill-incline"]),
        exercise("rowing-machine", "Aparat de vâslit", "Cardio", "CardioMachine", "Conditioning", "Intermediate", ["FatLoss", "Definition", "Fitness"], 1, 8, 20, 60, ["cardio", "full-body"], ["bike-steady"]),
    ]


def write_jsonl(path: Path, exercises: List[Exercise]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for item in exercises:
            handle.write(json.dumps(item, ensure_ascii=False, separators=(",", ":")))
            handle.write("\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    exercises = catalog()
    write_jsonl(args.output, exercises)
    print(f"Generated {len(exercises)} exercises -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
