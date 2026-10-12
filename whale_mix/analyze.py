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
            {
                "sample_id": sample,
                "pictures": slot["pictures"],
                "highest_bat": slot["highest_bat"],
                "call": slot["call"],
                "noise_db": noise.get(sample),
            }
        )
    return {
        "rows": len(rows),
        "labels": by_label,
        "reasons": by_reason,
        "samples": samples,
        "highest": best,
        "noise_attached": any(item["noise_db"] is not None for item in samples),
    }


def _count(n, word):
    if int(n) == 1:
        return f"1 {word}"
    return f"{n} {word}s"


def state_for(summary):
    """One short text block. Laya has to answer from these counts."""
    labels = summary["labels"]
    lines = [
        f"{summary['rows']} pictures.",
        (
            f"call {labels['call']}. not-call {labels['not-call']}. "
            f"review {labels['review']}."
        ),
        (
            f"agreed {summary['reasons']['agree']}. "
            f"blue-a kept {summary['reasons']['blue-a']}. "
            f"disagreed {summary['reasons']['disagree']}."
        ),
    ]
    highest = summary["highest"]
    if highest:
        lines.append(
            f"highest bat {highest['bat']:.3f} on {highest['sample_id']} "
            f"from {highest['picture_start_s']} to {highest['picture_end_s']} seconds."
        )
    for sample in summary["samples"]:
        bat = sample["highest_bat"]
        bat_text = f"{bat:.3f}" if bat is not None else "none"
        noise = sample["noise_db"]
        noise_text = f", 63 Hz {noise}" if noise is not None else ""
        lines.append(
            f"{sample['sample_id']}: {sample['pictures']} pictures, "
            f"highest bat {bat_text}, call rows {sample['call']}{noise_text}."
        )
    if summary["noise_attached"]:
        lines.append("63 Hz levels are attached by sample.")
    else:
        lines.append("63 Hz levels were not attached.")
    return " ".join(lines)


PATTERN_PLAIN = {
    "one-spike": "One picture stands out as a call. The rest stay low.",
    "flat": "The call scores stay low from picture to picture.",
    "too-few": "There are not enough call pictures to compare a quieter hour with a noisier hour.",
}


def render_report(summary, reading=None):
    """Plain report. Blue A's scores come first. Laya's sort follows. Then Laya reads the counts."""
    labels = summary["labels"]
    reasons = summary["reasons"]
    if summary["rows"] == 1:
        opening = "This report covers 1 picture."
    else:
        opening = f"This report covers {summary['rows']} pictures."
    lines = [
        "# Report",
        "",
        opening,
        "",
        "It uses two tables.",
        "",
        "Blue A's table scores each 25-second picture. `bat` is the call score. `baf` is the not-a-call score. The bigger number is Blue A's answer for that picture.",
        "",
        "Laya's table sorts those written rows. Each row lands in call, not-call, or review.",
        "",
        "## What the tables say",
        "",
    ]
    pile_bits = []
    if labels["call"]:
        pile_bits.append(f"{_count(labels['call'], 'picture')} went to call.")
    if labels["not-call"]:
        pile_bits.append(f"{_count(labels['not-call'], 'picture')} went to not-call.")
    if labels["review"]:
        pile_bits.append(f"{_count(labels['review'], 'picture')} went to review.")
    if not pile_bits:
        pile_bits.append("No picture received a label.")
    lines.append(" ".join(pile_bits))
    lines.append("")
    highest = summary["highest"]
    if highest:
        baf = highest["baf"]
        baf_text = f"{baf:.3f}" if baf is not None else "missing"
        lines.append(
            f"The highest call score in Blue A's table is {highest['bat']:.3f} "
            f"on {highest['sample_id']}, from {highest['picture_start_s']} to "
            f"{highest['picture_end_s']} seconds. The not-a-call score on that same picture is {baf_text}."
        )
        lines.append("")
    agree_bits = []
    if reasons["agree"]:
        agree_bits.append(f"On {_count(reasons['agree'], 'picture')}, Blue A and Laya gave the same answer.")
    if reasons["blue-a"]:
        agree_bits.append(f"On {_count(reasons['blue-a'], 'picture')}, Laya was unsure, so Blue A's answer stayed.")
    if reasons["disagree"]:
        agree_bits.append(f"On {_count(reasons['disagree'], 'picture')}, they disagreed, so the row went to review.")
    if agree_bits:
        lines.append(" ".join(agree_bits))
        lines.append("")
    lines.append("## Each sample")
    lines.append("")
    for sample in summary["samples"]:
        bat = sample["highest_bat"]
        bat_text = f"{bat:.3f}" if bat is not None else "none"
        noise = ""
        if sample["noise_db"] is not None:
            noise = f" The 63 Hz level for this sample is {sample['noise_db']}."
        call_text = (
            f"{_count(sample['call'], 'picture')} sorted as call."
            if sample["call"]
            else "None sorted as call."
        )
        lines.append(
            f"- {sample['sample_id']}: {_count(sample['pictures'], 'picture')}. "
            f"Highest call score {bat_text}. "
            f"{call_text}{noise}"
        )
    lines.append("")
    if summary["noise_attached"]:
        lines.append("A 63 Hz level was written next to each sample that had one. That number stands for low-frequency noise.")
    else:
        lines.append("No 63 Hz level was attached to this table.")
    lines.append("")
    lines.append(
        "These numbers come from the two tables. A miss rate, or a comparison of quieter hours and noisier hours, needs the call shape more than once in a quieter hour and more than once in a noisier hour."
    )
    if reading:
        pattern = reading.get("pattern", "")
        plain = PATTERN_PLAIN.get(pattern, "")
        pattern_line = f"Laya's pattern word is {pattern}."
        if plain:
            pattern_line = f"{pattern_line} {plain}"
        lines.extend(
            [
                "",
                "## What Laya said about these counts",
                "",
                (
                    f"{pattern_line} "
                    f"The chance Laya gave that word is {reading.get('pattern_probability', 0):.3f}."
                ),
                "",
                (
                    "Can these tables support a miss rate or a noise comparison? "
                    f"Laya said {reading.get('rate_ready', 'no')}. "
                    f"The chance of yes was {reading.get('rate_ready_probability', 0):.3f}."
                ),
                "",
                "Laya read the counts from the two tables. It did not listen to the recordings.",
            ]
        )
    lines.append("")
    return "\n".join(lines)


def read_laya(summary, agent):
    result = agent.predict(state_for(summary), PATTERN_QUESTION)
    answers = result.get("answers") or {}
    pattern_choice, pattern_probability = laya_fields(answers.get("pattern") or {})
    rate = answers.get("rate_ready") or {}
    rate_probability = float(rate.get("noul") or 0.0)
    ready = "yes" if rate_probability >= 0.5 else "no"
    return {
        "pattern": pattern_choice,
        "pattern_probability": pattern_probability,
        "rate_ready": ready,
        "rate_ready_probability": rate_probability,
    }


def load_noise(path):
    import csv
    from pathlib import Path

    noise = {}
    with Path(path).open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            sample = row.get("sample_id") or ""
            raw = row.get("noise_db") or row.get("median_db") or ""
            if sample and raw:
                noise[sample] = raw
    return noise


def write_report(rows, out_dir, agent=None, noise=None):
    from pathlib import Path

    summary = summarize(rows, noise)
    reading = read_laya(summary, agent) if agent is not None else None
    text = render_report(summary, reading)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "report.md").write_text(text, encoding="utf-8")
    return summary, text
