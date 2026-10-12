"""One command for the whole mix, plus score, sort, and export on their own."""

import argparse
import csv
import json
import os
import subprocess
import sys
from pathlib import Path

from whale_mix.export import EXPORT_COLUMNS, export_rows
from whale_mix.sound import COLUMNS, rows_from_blue_a, write_rows

DEFAULT_LAYA = Path(os.environ.get("WHALE_LAYA", r"D:\Models\laya"))
DEFAULT_BLUE_A = Path(
    os.environ.get(
        "WHALE_BLUE_A_MODEL",
        r"D:\Code\Projects\Marine-Science\MBARI-Blue-A\models\1",
    )
)
DEFAULT_BLUE_A_PYTHON = Path(
    os.environ.get(
        "WHALE_BLUE_A_PYTHON",
        r"D:\Code\Projects\Marine-Science\MBARI-Blue-A\.venv\Scripts\python.exe",
    )
)


def _read_table(path):
    with Path(path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def command_score(args):
    if args.image:
        script = Path(__file__).resolve().parent / "score_image.py"
        python = Path(args.python)
        if not python.is_file():
            raise SystemExit(f"Blue A Python was not found at {python}")
        completed = subprocess.run(
            [str(python), str(script), "--model", str(args.model), "--image", str(args.image)],
            check=False,
            capture_output=True,
            text=True,
        )
        if completed.returncode != 0:
            sys.stderr.write(completed.stderr)
            raise SystemExit(completed.returncode)
