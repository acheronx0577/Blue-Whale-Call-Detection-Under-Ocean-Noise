# Blue Whale Call Detection Under Ocean Noise

An independent student project. This repository holds a program that reads MBARI Blue A scores for 25-second pictures, asks Laya to check each written row in one pass, and exports the rows. It is not an official MBARI project or endorsement.

## The question

Does the call score change when the 63 Hz level is higher?

The 63 Hz level is MBARI's stand-in for low-frequency noise. A whale-call harmonic or the recorder can raise it, so a high number does not by itself prove a ship was present. The six clips scored so far are too few to answer the question.

## What this program does

Blue A reads a 25-second picture from an original 2 kHz recording and returns two scores. `bat` is the call score. `baf` is the not-a-call score. The bigger score is Blue A's label for that picture.

Laya reads the written row and answers in one pass. After the rows are sorted, Laya reads the counts once and that reading is written under the counts. The mix keeps both answers:

- When they agree, the row keeps that label.
- When Laya's choice probability is under 0.6, Blue A's label stays.
- When they disagree and Laya is confident, the row goes to `review`.

Recordings come from the Pacific Sound archive. The picture step and the starting weights are MBARI's Blue A model. The one-pass check is Laya.

## Commands

One command scores, sorts, and exports:

```bash
python -m whale_mix run --scores path\to\candidate-scores.csv --out out\mix
```

Each step also runs alone:

```bash
python -m whale_mix score --scores path\to\candidate-scores.csv --out out\sound.csv
python -m whale_mix sort --table out\sound.csv --out out\sorted.csv
python -m whale_mix export --table out\sorted.csv --out out\mix
python -m whale_mix analyze --table out\mix\decisions.csv --out out\mix
```

`score --image picture.jpg` scores one spectrogram with the local Blue A weights. The export writes the technical files first: `decisions.csv`, `decisions.json`, and `call`, `not-call`, and `review` folders. `report.md` is written after those files. It states the counts in sentences, then Laya's reading of those counts. An optional `--noise` CSV with `sample_id` and `noise_db` attaches a 63 Hz level to each sample in that report.

Audio, pictures, score tables, Blue A weights, and Laya weights stay outside this repository.

## Data and licensing

