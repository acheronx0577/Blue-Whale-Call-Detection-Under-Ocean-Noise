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
    if args.image:
        args.out = str(out / "sound.csv")
        command_score(args)
        sound_path = out / "sound.csv"
    else:
        sound_rows = rows_from_blue_a(args.scores)
        sound_path = out / "sound.csv"
        write_rows(sound_path, sound_rows, COLUMNS)
    from whale_mix.analyze import load_noise, write_report
    from whale_mix.sort import load_laya, sort_rows

    agent = load_laya(args.laya)
    mixed = sort_rows(_read_table(sound_path), agent)
    write_rows(out / "sorted.csv", mixed, EXPORT_COLUMNS)
    counts = export_rows(mixed, out)
    noise = load_noise(args.noise) if args.noise else None
    write_report(mixed, out, agent, noise)
    print(json.dumps({"out": str(out), "report": str(out / "report.md"), **counts}, indent=2))


def build_parser():
    parser = argparse.ArgumentParser(
        prog="whale_mix",
        description=(
            "Blue A names each 25-second picture. Laya sorts each written row, then reads the counts. "
            "One command does all of that and writes a plain report after the table. "
            "score, sort, export, and analyze also run alone."
        ),
    )
    sub = parser.add_subparsers(dest="command", required=True)

    score = sub.add_parser("score", help="Read a Blue A score CSV, or score one image.")
    score.add_argument("--scores", help="Blue A candidate-scores.csv")
    score.add_argument("--image", help="One spectrogram image to score with Blue A")
    score.add_argument("--model", default=str(DEFAULT_BLUE_A), help="Blue A SavedModel directory")
    score.add_argument("--python", default=str(DEFAULT_BLUE_A_PYTHON), help="Python that has TensorFlow")
    score.add_argument("--out", help="CSV path for the sound rows")
    score.set_defaults(func=command_score)

    sort = sub.add_parser("sort", help="Ask Laya which pile each written row belongs in.")
    sort.add_argument("--table", required=True, help="Sound CSV from the score command")
    sort.add_argument("--laya", default=str(DEFAULT_LAYA), help="Local Laya checkpoint directory")
    sort.add_argument("--out", help="CSV path for the mixed rows")
    sort.set_defaults(func=command_sort)

    export = sub.add_parser("export", help="Write CSV, JSON, and call / not-call / review folders.")
    export.add_argument("--table", required=True)
    export.add_argument("--out", required=True)
    export.set_defaults(func=command_export)

    analyze = sub.add_parser("analyze", help="Write a plain report from a finished sort table.")
    analyze.add_argument("--table", required=True, help="Sorted CSV, usually decisions.csv or sorted.csv")
    analyze.add_argument("--out", required=True, help="Folder for report.md")
    analyze.add_argument("--laya", default=str(DEFAULT_LAYA), help="Local Laya checkpoint directory")
    analyze.add_argument("--noise", help="Optional CSV with sample_id and noise_db")
    analyze.set_defaults(func=command_analyze)

    run = sub.add_parser("run", help="Score, sort, export, and write the readable report.")
    run.add_argument("--scores", help="Blue A candidate-scores.csv")
    run.add_argument("--image", help="Score this one image instead of a CSV")
    run.add_argument("--model", default=str(DEFAULT_BLUE_A))
    run.add_argument("--python", default=str(DEFAULT_BLUE_A_PYTHON))
    run.add_argument("--laya", default=str(DEFAULT_LAYA))
    run.add_argument("--noise", help="Optional CSV with sample_id and noise_db")
    run.add_argument("--out", required=True)
    run.set_defaults(func=command_run)
