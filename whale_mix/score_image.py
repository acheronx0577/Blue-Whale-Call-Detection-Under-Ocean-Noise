"""Score one spectrogram image with the local Blue A SavedModel.

Run this file with the MBARI Blue A virtualenv. The mix command calls it
when you pass an image. It prints one JSON object and does not write the
pilot score tables.
"""

import argparse
import json
from pathlib import Path

import cv2
import numpy as np
import tensorflow as tf


def score_image(model_dir, image_path):
    model_dir = Path(model_dir)
    config = json.loads((model_dir / "config.json").read_text(encoding="utf-8"))
    model = tf.keras.models.load_model(model_dir)
    image_bgr = cv2.imread(Path(image_path).as_posix())
    if image_bgr is None:
        raise RuntimeError(f"could not read {image_path}")
    image = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    image_float = np.asarray(image).astype("float32") / 255.0
    mean = np.asarray(config["image_mean"], dtype=np.float32)
    std = np.asarray(config["image_std"], dtype=np.float32)
    image_float = (image_float - mean) / (std + 1.0e-9)
