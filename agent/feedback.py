"""Logs each run's rating/comment to a local CSV so you have real feedback
data for the Week 2-3 rubric without needing extra API credentials up
front. To centralize this in a Google Sheet instead, install `gspread`,
share a sheet with a service account, and swap the body of log() for a
sheet.append_row(...) call -- everything else in the app stays the same.
"""

import csv
import os
from datetime import datetime, timezone

LOG_PATH = os.path.join(os.path.dirname(__file__), "..", "eval", "feedback_log.csv")


def log(topic: str, final_map: str, rating: int, comment: str) -> None:
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    file_exists = os.path.isfile(LOG_PATH)
    with open(LOG_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["timestamp", "topic", "final_map", "rating", "comment"])
        writer.writerow(
            [datetime.now(timezone.utc).isoformat(), topic, final_map, rating, comment]
        )
