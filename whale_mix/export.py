"""Write the mixed table as CSV, JSON, and one folder per label."""

import json
from pathlib import Path

from whale_mix.sound import write_rows

EXPORT_COLUMNS = (
    "sample_id",
    "candidate_id",
    "picture_start_s",
    "picture_end_s",
    "bat",
    "baf",
    "sound_label",
    "laya_choice",
    "laya_probability",
    "mix_label",
    "mix_reason",
    "image_file",
)

LABELS = ("call", "not-call", "review")


def export_rows(rows, out_dir):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    write_rows(out_dir / "decisions.csv", rows, EXPORT_COLUMNS)
    payload = []
    for row in rows:
        payload.append({key: row.get(key, "") for key in EXPORT_COLUMNS})
    (out_dir / "decisions.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
