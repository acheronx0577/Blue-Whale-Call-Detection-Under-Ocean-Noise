"""Write the mixed table as CSV, JSON, and one folder per label."""

import json
from pathlib import Path

from whale_mix.sound import write_rows

EXPORT_COLUMNS = (
    "sample_id",
    "candidate_id",
    "picture_start_s",
