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


def _num(row, key):
    try:
        return float(row.get(key, ""))
    except (TypeError, ValueError):
        return None


def summarize(rows, noise=None):
    """Count the sort. `noise` maps sample_id to a 63 Hz level when one was supplied."""
    noise = noise or {}
    by_label = {"call": 0, "not-call": 0, "review": 0}
    by_reason = {"agree": 0, "blue-a": 0, "disagree": 0}
    by_sample = {}
    best = None
    for row in rows:
        label = row.get("mix_label") or row.get("sound_label") or ""
        if label in by_label:
            by_label[label] += 1
        reason = row.get("mix_reason") or ""
        if reason in by_reason:
            by_reason[reason] += 1
        sample = row.get("sample_id") or "(no sample)"
        slot = by_sample.setdefault(sample, {"pictures": 0, "highest_bat": None, "call": 0})
        slot["pictures"] += 1
        if label == "call":
            slot["call"] += 1
        bat = _num(row, "bat")
        if bat is None:
            continue
        if slot["highest_bat"] is None or bat > slot["highest_bat"]:
            slot["highest_bat"] = bat
        if best is None or bat > best["bat"]:
            best = {
                "bat": bat,
                "baf": _num(row, "baf"),
                "sample_id": sample,
                "picture_start_s": row.get("picture_start_s", ""),
                "picture_end_s": row.get("picture_end_s", ""),
                "candidate_id": row.get("candidate_id", ""),
            }
    samples = []
    for sample in sorted(by_sample):
        slot = by_sample[sample]
        samples.append(
