"""Turn a finished sort table into counts, then ask Laya to read those counts."""

from whale_mix.mix import laya_fields


PATTERN_QUESTION = {
    "pattern": {
        "type": "choice",
        "instructions": (
            "Using only the counts in the state, how does the call score sit "
