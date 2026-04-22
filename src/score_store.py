from __future__ import annotations

import json
from pathlib import Path


SCORES_FILE = Path(__file__).resolve().parent.parent / "scores.json"


def load_scores() -> list[dict[str, int | str]]:
    if not SCORES_FILE.exists():
        return []

    try:
        with SCORES_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except (OSError, json.JSONDecodeError):
        return []

    if not isinstance(data, list):
        return []

    scores = []
    for item in data:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name", "AAA")).upper()[:8]
        score = int(item.get("score", 0))
        scores.append({"name": name, "score": score})

    scores.sort(key=lambda item: int(item["score"]), reverse=True)
    return scores[:8]


def save_score(name: str, score: int) -> list[dict[str, int | str]]:
    scores = load_scores()
    scores.append({
        "name": name.upper()[:8] or "AAA",
        "score": max(0, int(score)),
    })
    scores.sort(key=lambda item: int(item["score"]), reverse=True)
    scores = scores[:8]

    with SCORES_FILE.open("w", encoding="utf-8") as file:
        json.dump(scores, file, indent=2)

    return scores
