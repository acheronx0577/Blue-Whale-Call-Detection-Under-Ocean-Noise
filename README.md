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

- The [Pacific Sound archive](https://www.mbari.org/project/open-acoustic-data/) provides daily 2 kHz recordings. The [AWS Open Data registry](https://registry.opendata.aws/pacific-sound/) lists the recordings and `s3://pacific-sound-models` under **CC BY 4.0**. Attribute Monterey Bay Aquarium Research Institute, link the registry and the [model page](https://docs.mbari.org/pacific-sound/models/), and note changes. The full text is in [LICENSE-CC-BY-4.0](LICENSE-CC-BY-4.0).
- MBARI's published blueA validation F1 is 0.9454 for candidate pictures. That number is MBARI's, measured on their validation set. It is not a result from this project.
- MBARI's [shipping-noise notebook](https://docs.mbari.org/pacific-sound/notebooks/shippingnoise/PacificSoundShippingNoiseAnalysis/) is GPL-3.0. This repository does not include that notebook.
- Laya's English checkpoint is Apache-2.0: [convaiinnovations/laya](https://huggingface.co/convaiinnovations/laya). This repository does not include those weights.
- Original code in this repository is under the MIT license in [LICENSE](LICENSE). That license does not replace the CC BY 4.0 terms for MBARI material or the Apache-2.0 terms for Laya.

No registration is required to use these licenses. The credit above is the requirement.

## Status

Recorded 2026-10-13. Six five-minute clips from the 2025-11-01 Pacific Sound file, Samples A through F. Blue A scored 69 pictures on the original files. One picture scored higher for `bat`: Sample A, 92.4–98.6 seconds, `bat` 0.507 and `baf` 0.493. The other 68 scored higher for `baf`. None reached 0.7.

| Sample | Pictures | Bigger `bat` | Highest `bat` |
| --- | --- | --- | --- |
| A | 7 | 1 | 0.507 |
| B | 9 | 0 | 0.030 |
| C | 6 | 0 | 0.073 |
| D | 20 | 0 | 0.044 |
| E | 22 | 0 | 0.034 |
| F | 5 | 0 | 0.041 |

Calibrated 63 Hz medians for the first four clips, dB re 1 μPa²/Hz: A 70.622, C 71.485, B 76.229, D 77.448. The call score stays near 0.03 in both the quieter pair and the noisier pair.

