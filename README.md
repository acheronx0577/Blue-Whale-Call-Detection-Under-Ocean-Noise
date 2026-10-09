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

