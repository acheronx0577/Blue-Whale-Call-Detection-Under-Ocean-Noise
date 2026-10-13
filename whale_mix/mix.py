"""Pure rules for the Blue A score, the Laya check, and the exported label."""

LAYA_MIN_PROBABILITY = 0.6


def sound_label(bat, baf):
    """Blue A's label for one 25-second picture. The bigger score wins."""
    if float(bat) > float(baf):
        return "call"
    return "not-call"


def mix_label(sound, laya_choice, laya_probability, min_probability=LAYA_MIN_PROBABILITY):
    """Combine the two answers.

    A confident Laya answer that matches Blue A keeps that label.
    A low Laya probability keeps Blue A's label.
    A confident disagreement goes to review, and both scores stay on the row.
    """
    sound = sound or "not-call"
    probability = float(laya_probability)
    if probability < min_probability or not laya_choice:
        return sound, "blue-a"
    if laya_choice == sound:
        return sound, "agree"
    return "review", "disagree"


def laya_fields(answer):
    """Pull the choice and its probability out of one Laya answer object.

    The choice probability lives on ``probabilities`` and ``answer_confidence``.
    Laya's separate ``confidence`` field is a different number, so it is not used here.
    """
    if not isinstance(answer, dict):
        return "", 0.0
    choice = str(answer.get("choice") or "")
    probs = answer.get("probs") or answer.get("probabilities") or {}
    if isinstance(probs, dict) and choice in probs:
        return choice, float(probs[choice])
    for key in ("answer_confidence", "probability", "prob"):
        value = answer.get(key)
        if isinstance(value, (int, float)):
            return choice, float(value)
    return choice, 0.0
