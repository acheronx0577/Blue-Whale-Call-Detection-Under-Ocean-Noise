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
