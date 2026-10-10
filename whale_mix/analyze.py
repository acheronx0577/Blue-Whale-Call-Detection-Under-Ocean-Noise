"""Turn a finished sort table into counts, then ask Laya to read those counts."""

from whale_mix.mix import laya_fields


PATTERN_QUESTION = {
    "pattern": {
        "type": "choice",
        "instructions": (
            "Using only the counts in the state, how does the call score sit "
            "across the pictures?"
        ),
        "criteria": {
            "flat": "the call scores stay in the same low band across samples",
            "one-spike": "one picture is near one half and the rest stay low",
            "too-few": "there are not two call pictures in two different noise levels",
        },
    },
    "rate_ready": {
        "type": "noul",
        "instructions": (
            "Do these counts support a miss rate, a false-alarm rate, "
            "or a noise comparison?"
        ),
        "criteria": {
            "false": "the table has fewer than two trusted call pictures in each noise level",
            "true": "the table has at least two trusted call pictures in a quieter level and a noisier level",
        },
    },
}


