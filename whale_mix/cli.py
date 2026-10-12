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
