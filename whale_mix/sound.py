"""Read a Blue A score table and name each 25-second picture."""

import csv
from pathlib import Path


COLUMNS = (
    "sample_id",
    "candidate_id",
    "picture_start_s",
    "picture_end_s",
    "bat",
    "baf",
    "sound_label",
    "image_file",
)


def _float(row, *keys):
    for key in keys:
        if row.get(key) not in (None, ""):
            return float(row[key])
    raise ValueError("a score row is missing bat or baf")


def _start(row):
    for key in ("centered_window_start_s", "picture_start_s", "proposal_start_s"):
        if row.get(key) not in (None, ""):
            return row[key]
    return ""


def _end(row):
    for key in ("centered_window_end_s", "picture_end_s", "proposal_end_s"):
