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
        line = completed.stdout.strip().splitlines()[-1]
        row = json.loads(line)
        if args.out:
            write_rows(args.out, [row], COLUMNS)
        print(json.dumps(row, indent=2))
        return
    if not args.scores:
        raise SystemExit("pass --scores with a Blue A CSV, or --image with one spectrogram")
    rows = rows_from_blue_a(args.scores)
    if args.out:
        write_rows(args.out, rows, COLUMNS)
    print(json.dumps({"rows": len(rows), "out": str(args.out or "")}, indent=2))


def command_sort(args):
    from whale_mix.sort import load_laya, sort_rows

    rows = _read_table(args.table)
    agent = load_laya(args.laya)
    mixed = sort_rows(rows, agent)
    out = args.out or args.table
    write_rows(out, mixed, EXPORT_COLUMNS)
    print(json.dumps({"rows": len(mixed), "out": str(out)}, indent=2))


def command_export(args):
    rows = _read_table(args.table)
    counts = export_rows(rows, args.out)
    print(json.dumps(counts, indent=2))


def command_analyze(args):
    from whale_mix.analyze import load_noise, write_report
    from whale_mix.sort import load_laya

    rows = _read_table(args.table)
    noise = load_noise(args.noise) if args.noise else None
    summary, _text = write_report(rows, args.out, load_laya(args.laya), noise)
    print(json.dumps({"out": str(Path(args.out) / "report.md"), "rows": summary["rows"]}, indent=2))


def command_run(args):
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
