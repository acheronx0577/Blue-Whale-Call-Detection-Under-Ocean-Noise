"""Ask Laya, in one pass per row, which pile the written scores belong in."""

from whale_mix.mix import LAYA_MIN_PROBABILITY, laya_fields, mix_label

QUESTION = {
    "label": {
        "type": "choice",
        "instructions": (
            "A 25-second ocean-sound picture has two scores. "
            "bat is the call score. baf is the not-a-call score. "
            "Which pile should this picture go in?"
        ),
        "criteria": {
            "call": "bat is greater than baf",
            "not-call": "baf is greater than or equal to bat",
        },
    }
}


def state_for(row):
    return (
        f"sample {row.get('sample_id', '')}. "
        f"picture {row.get('picture_start_s', '')} to {row.get('picture_end_s', '')} seconds. "
        f"bat {row.get('bat', '')}. baf {row.get('baf', '')}. "
        f"Blue A label {row.get('sound_label', '')}."
    )


def sort_rows(rows, agent, min_probability=LAYA_MIN_PROBABILITY):
    """Add Laya's choice and the mixed label. `agent.predict` is called once per row."""
    sorted_rows = []
    for row in rows:
        result = agent.predict(state_for(row), QUESTION)
        answer = (result.get("answers") or {}).get("label") or {}
        choice, probability = laya_fields(answer)
        label, reason = mix_label(row.get("sound_label"), choice, probability, min_probability)
        mixed = dict(row)
        mixed["laya_choice"] = choice
        mixed["laya_probability"] = f"{probability:.6f}"
