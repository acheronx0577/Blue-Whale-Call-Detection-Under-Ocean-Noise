import csv
import json
import tempfile
import unittest
from pathlib import Path

from whale_mix.analyze import render_report, summarize
from whale_mix.export import export_rows
from whale_mix.mix import laya_fields, mix_label, sound_label
from whale_mix.sound import rows_from_blue_a
from whale_mix.sort import sort_rows


class MixTests(unittest.TestCase):
    def test_bigger_score_is_the_sound_label(self):
        self.assertEqual(sound_label(0.507, 0.493), "call")
        self.assertEqual(sound_label(0.03, 0.97), "not-call")
        self.assertEqual(sound_label(0.5, 0.5), "not-call")

    def test_agreement_disagreement_and_low_probability(self):
        self.assertEqual(mix_label("call", "call", 0.8), ("call", "agree"))
        self.assertEqual(mix_label("not-call", "call", 0.9), ("review", "disagree"))
        self.assertEqual(mix_label("not-call", "call", 0.4), ("not-call", "blue-a"))

    def test_laya_probability_from_probs_map(self):
        choice, probability = laya_fields({"choice": "call", "probs": {"call": 0.75, "not-call": 0.25}})
        self.assertEqual(choice, "call")
        self.assertAlmostEqual(probability, 0.75)

    def test_choice_probability_wins_over_the_other_confidence_field(self):
        choice, probability = laya_fields(
            {
                "choice": "call",
                "probabilities": {"call": 0.7432, "not-call": 0.2568},
                "confidence": 0.1781,
                "answer_confidence": 0.7432,
            }
        )
        self.assertEqual(choice, "call")
        self.assertAlmostEqual(probability, 0.7432)

    def test_blue_a_csv_skips_unscored_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "scores.csv"
