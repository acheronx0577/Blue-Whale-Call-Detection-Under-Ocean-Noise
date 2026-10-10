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
            with path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(
                    handle,
                    fieldnames=["sample_id", "candidate_id", "status", "bat_score", "baf_score", "centered_window_start_s", "centered_window_end_s", "image_file"],
                )
                writer.writeheader()
                writer.writerow(
                    {
                        "sample_id": "sample-a",
                        "candidate_id": "sample-a-004",
                        "status": "scored",
                        "bat_score": "0.507124",
                        "baf_score": "0.492876",
                        "centered_window_start_s": "92.416",
                        "centered_window_end_s": "98.56",
                        "image_file": "a.jpg",
                    }
                )
                writer.writerow(
                    {
                        "sample_id": "sample-b",
                        "candidate_id": "sample-b-001",
                        "status": "not_scored: edge",
                        "bat_score": "",
                        "baf_score": "",
                        "centered_window_start_s": "",
                        "centered_window_end_s": "",
                        "image_file": "",
                    }
                )
            rows = rows_from_blue_a(path)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["sound_label"], "call")
        self.assertEqual(rows[0]["picture_start_s"], "92.416")

    def test_sort_uses_the_agent_once_per_row(self):
        class Agent:
            def predict(self, state, questions):
                self.state = state
                self.questions = questions
                return {"answers": {"label": {"choice": "not-call", "probability": 0.91}}}

        agent = Agent()
        mixed = sort_rows(
            [{"sample_id": "sample-c", "bat": "0.030000", "baf": "0.970000", "sound_label": "not-call"}],
            agent,
        )
        self.assertEqual(mixed[0]["mix_label"], "not-call")
        self.assertEqual(mixed[0]["mix_reason"], "agree")
        self.assertIn("bat 0.030000", agent.state)

    def test_export_writes_three_formats(self):
        rows = [
            {
                "sample_id": "sample-a",
                "candidate_id": "sample-a-004",
                "picture_start_s": "92.416",
                "picture_end_s": "98.56",
                "bat": "0.507124",
                "baf": "0.492876",
                "sound_label": "call",
                "laya_choice": "call",
                "laya_probability": "0.800000",
                "mix_label": "call",
                "mix_reason": "agree",
                "image_file": "a.jpg",
            }
        ]
        with tempfile.TemporaryDirectory() as tmp:
