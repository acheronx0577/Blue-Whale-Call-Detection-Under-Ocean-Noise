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
    for label in LABELS:
        folder = out_dir / label
        folder.mkdir(parents=True, exist_ok=True)
        lines = []
        for row in rows:
            if row.get("mix_label") != label:
                continue
            name = row.get("candidate_id") or row.get("image_file") or row.get("sample_id")
            lines.append(
                f"{name}\t{row.get('sample_id', '')}\t{row.get('picture_start_s', '')}\t{row.get('picture_end_s', '')}"
            )
        (folder / "manifest.txt").write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
    counts = {label: sum(row.get("mix_label") == label for row in rows) for label in LABELS}
    counts["rows"] = len(rows)
    return counts
