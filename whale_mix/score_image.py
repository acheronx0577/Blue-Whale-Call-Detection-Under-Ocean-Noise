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
    scores = model(image_float[np.newaxis, :, :]).numpy()[0]
    baf = float(scores[0])
    bat = float(scores[1])
    return {
        "sample_id": "",
        "candidate_id": Path(image_path).stem,
        "picture_start_s": "",
        "picture_end_s": "",
        "bat": f"{bat:.6f}",
        "baf": f"{baf:.6f}",
        "sound_label": "call" if bat > baf else "not-call",
        "image_file": Path(image_path).name,
        "classes": config.get("classes", ["baf", "bat"]),
    }


def main():
    parser = argparse.ArgumentParser(description="Score one image with Blue A.")
    parser.add_argument("--model", required=True)
    parser.add_argument("--image", required=True)
    args = parser.parse_args()
    print(json.dumps(score_image(args.model, args.image)))
