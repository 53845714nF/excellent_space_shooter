"""
Highscore Manager Module.
Handles loading, saving, sorting and querying highscores over time.
"""
import json
import os
import time
from datetime import datetime
from paths import get_save_path

DEFAULT_SCORES = [
    {
        "name": "STAR ACE",
        "score": 200,
        "level": 2,
        "date": "02.11.2026 14:30",
        "timestamp": 1793630000.0,
    },
    {
        "name": "ROOKIE",
        "score": 80,
        "level": 1,
        "date": "03.11.2026 11:15",
        "timestamp": 1793705000.0,
    },
]


class HighscoreManager:
    """
    Manages persistent highscore data.
    """

    def __init__(self, filepath=None):
        self.filepath = filepath or get_save_path("highscores.json")
        self.scores = []
        self.load()

    def load(self):
        """
        Loads highscores from JSON file. If file does not exist or is corrupted,
        falls back to default highscores and saves them.
        """
        if not os.path.exists(self.filepath):
            self.scores = list(DEFAULT_SCORES)
            self.save()
            return

        try:
            with open(self.filepath, "r", encoding="utf-8") as file:
                data = json.load(file)
                if isinstance(data, list):
                    valid_scores = []
                    for item in data:
                        if isinstance(item, dict) and "score" in item:
                            valid_scores.append({
                                "name": str(item.get("name", "PILOT"))[:12].strip() or "PILOT",
                                "score": int(item.get("score", 0)),
                                "level": int(item.get("level", 1)),
                                "date": str(item.get("date", "Unbekannt")),
                                "timestamp": float(item.get("timestamp", 0.0)),
                            })
                    self.scores = valid_scores
                else:
                    self.scores = list(DEFAULT_SCORES)
        except (json.JSONDecodeError, OSError, ValueError):
            self.scores = list(DEFAULT_SCORES)

        self._sort()

    def save(self):
        """
        Saves highscores to JSON file.
        """
        try:
            temp_path = f"{self.filepath}.tmp"
            with open(temp_path, "w", encoding="utf-8") as file:
                json.dump(self.scores, file, indent=2, ensure_ascii=False)
            os.replace(temp_path, self.filepath)
        except OSError as exc:
            print(f"Warnung: Highscores konnten nicht gespeichert werden: {exc}")

    def _sort(self):
        """
        Sorts highscores by score descending, then by timestamp descending.
        """
        self.scores.sort(
            key=lambda item: (-item.get("score", 0), -item.get("timestamp", 0.0))
        )

    def add_score(self, name: str, score: int, level: int):
        """
        Adds a new highscore entry, saves it, and returns (rank, entry).
        Rank is 1-based (e.g. 1 for 1st place).
        """
        clean_name = str(name).strip().upper()[:12] if str(name).strip() else "PILOT"
        now = datetime.now()
        timestamp = time.time()
        date_str = now.strftime("%d.%m.%Y %H:%M")

        entry = {
            "name": clean_name,
            "score": int(score),
            "level": int(level),
            "date": date_str,
            "timestamp": timestamp,
        }

        self.scores.append(entry)
        self._sort()

        # Keep top 100 historical entries
        if len(self.scores) > 100:
            self.scores = self.scores[:100]

        self.save()

        # Find 1-based rank
        rank = 1
        for idx, item in enumerate(self.scores):
            if item is entry or (
                item["timestamp"] == timestamp and item["score"] == entry["score"]
            ):
                rank = idx + 1
                break

        return rank, entry

    def get_top_scores(self, limit=10):
        """
        Returns top scores sorted by score descending.
        """
        return self.scores[:limit]

    def get_recent_scores(self, limit=10):
        """
        Returns scores sorted by timestamp descending (history over time).
        """
        sorted_recent = sorted(
            self.scores, key=lambda item: -item.get("timestamp", 0.0)
        )
        return sorted_recent[:limit]

    def get_best_score(self) -> int:
        """
        Returns the highest score recorded, or 0.
        """
        if self.scores:
            return self.scores[0].get("score", 0)
        return 0

    def is_new_record(self, score: int) -> bool:
        """
        Returns True if the given score beats the all-time top score.
        """
        return score > self.get_best_score()

    def clear(self):
        """
        Clears all highscores.
        """
        self.scores = []
        self.save()
