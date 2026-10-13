"""Read a Blue A score table and name each 25-second picture."""

import csv
from pathlib import Path


COLUMNS = (
    "sample_id",
    "candidate_id",
    "picture_start_s",
    "picture_end_s",
    "bat",
