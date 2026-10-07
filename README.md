# Blue Whale Call Detection Under Ocean Noise

An independent research project examining whether MBARI's published blue-whale A-call workflow makes different errors in different low-frequency sound conditions.

## The question

Does the existing workflow miss more calls or produce more false alarms in higher low-frequency-noise intervals than in comparable quieter intervals?

Reliable call counts matter when researchers use automated detections to study whale presence. This project will measure where the workflow is reliable; it will not assume that noise is caused by vessels or that it changes whale behavior.

## Approach

Manually label a bounded set of short audio windows without viewing model scores, then compare the existing call-detection workflow across matched noise conditions. Report call-level recall and false alarms per hour on independently labeled audio. Report candidate-classifier precision and recall separately: MBARI's published blueA classifier labels proposed detections, so its reported F1 score does not measure calls missed in continuous audio.

MBARI's 63 Hz sound metric is a low-frequency-noise proxy. Whale-call harmonics and recorder movement can affect it, so high values alone do not establish vessel noise.

## Data and licensing

- The [Pacific Sound archive](https://www.mbari.org/project/open-acoustic-data/) provides daily 2 kHz recordings. The [AWS Open Data registry](https://registry.opendata.aws/pacific-sound/) lists the recordings under **CC BY 4.0**. Attribute MBARI and record the access date when using the data.
- MBARI's [blueA model documentation](https://docs.mbari.org/pacific-sound/models/) reports F1 0.9454 for candidate detections. The model weights have a separate license status that must be confirmed before redistribution.
- MBARI's [shipping-noise notebook](https://docs.mbari.org/pacific-sound/notebooks/shippingnoise/PacificSoundShippingNoiseAnalysis/) marks its code GPL-3.0. This repository does not include that code, audio, model weights, or downloaded data.
- The MIT license in this repository applies only to original materials here. It does not change the terms for MBARI data, models, notebooks, or other third-party materials.

## Status

Project setup only. No audio has been downloaded, no labels or measurements have been produced, and no result is claimed.

This is an independent student project; it is not an official MBARI project or endorsement.

## Sources

- [MBARI Pacific Sound quickstart](https://docs.mbari.org/pacific-sound/quickstart/)
- [Pacific Sound data registry and license](https://registry.opendata.aws/pacific-sound/)
- [Blue A-call model metrics and validation counts](https://docs.mbari.org/pacific-sound/models/)
- [Shipping-noise metric and known confounds](https://docs.mbari.org/pacific-sound/notebooks/shippingnoise/PacificSoundShippingNoiseAnalysis/)
