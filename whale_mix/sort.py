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
