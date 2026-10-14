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
        if row.get(key) not in (None, ""):
            return row[key]
    return ""


def rows_from_blue_a(path):
    """Turn a Blue A candidate-scores CSV into sound rows.

    Rows that Blue A did not score are left out. This reads the table.
    It does not run the neural net and it does not rewrite the source file.
    """
    path = Path(path)
    rows = []
    with path.open(newline="", encoding="utf-8") as handle:
        for raw in csv.DictReader(handle):
            status = raw.get("status", "scored")
            if status and status != "scored":
                continue
            bat = _float(raw, "bat", "bat_score")
            baf = _float(raw, "baf", "baf_score")
            from whale_mix.mix import sound_label

