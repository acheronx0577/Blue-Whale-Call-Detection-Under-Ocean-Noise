#[derive(Clone, Debug)]
pub struct Reading {
    pub pattern: String,
    pub pattern_probability: f64,
    pub rate_ready: String,
    pub rate_ready_probability: f64,
}

#[derive(Clone, Debug, Default)]
pub struct SampleCount {
    pub sample_id: String,
    pub pictures: usize,
    pub highest_bat: Option<f64>,
    pub call: usize,
    pub noise_db: Option<String>,
}

#[derive(Clone, Debug, Default)]
pub struct Highest {
    pub bat: f64,
    pub baf: Option<f64>,
    pub sample_id: String,
    pub picture_start_s: String,
    pub picture_end_s: String,
}

#[derive(Clone, Debug, Default)]
pub struct Summary {
    pub rows: usize,
    pub call: usize,
    pub not_call: usize,
    pub review: usize,
    pub agree: usize,
    pub blue_a: usize,
    pub disagree: usize,
    pub samples: Vec<SampleCount>,
    pub highest: Option<Highest>,
    pub noise_attached: bool,
}

fn count_phrase(n: usize, word: &str) -> String {
    if n == 1 {
        format!("1 {word}")
    } else {
        format!("{n} {word}s")
    }
}

pub fn summarize(rows: &[crate::table::SoundRow], noise: &std::collections::HashMap<String, String>) -> Summary {
    use std::collections::BTreeMap;
    let mut samples: BTreeMap<String, SampleCount> = BTreeMap::new();
    let mut summary = Summary {
        rows: rows.len(),
        ..Summary::default()
    };
    for row in rows {
        match row.mix_label.as_str() {
            "call" => summary.call += 1,
            "not-call" => summary.not_call += 1,
            "review" => summary.review += 1,
            _ => {}
        }
        match row.mix_reason.as_str() {
            "agree" => summary.agree += 1,
            "blue-a" => summary.blue_a += 1,
            "disagree" => summary.disagree += 1,
            _ => {}
        }
        let sample_id = if row.sample_id.is_empty() {
            "(no sample)".to_string()
        } else {
            row.sample_id.clone()
        };
        let slot = samples.entry(sample_id.clone()).or_insert_with(|| SampleCount {
            sample_id,
            ..SampleCount::default()
        });
        slot.pictures += 1;
        if row.mix_label == "call" {
            slot.call += 1;
        }
        if let Ok(bat) = row.bat.parse::<f64>() {
            if slot.highest_bat.map(|current| bat > current).unwrap_or(true) {
                slot.highest_bat = Some(bat);
            }
            let replace = summary
                .highest
                .as_ref()
                .map(|current| bat > current.bat)
                .unwrap_or(true);
            if replace {
                summary.highest = Some(Highest {
                    bat,
                    baf: row.baf.parse().ok(),
                    sample_id: slot.sample_id.clone(),
                    picture_start_s: row.picture_start_s.clone(),
                    picture_end_s: row.picture_end_s.clone(),
                });
            }
        }
    }
    for (sample_id, mut slot) in samples {
        slot.noise_db = noise.get(&sample_id).cloned();
        if slot.noise_db.is_some() {
            summary.noise_attached = true;
        }
        summary.samples.push(slot);
    }
    summary
}

pub fn render_report(summary: &Summary, reading: Option<&Reading>) -> String {
    let opening = if summary.rows == 1 {
        "This report covers 1 picture.".to_string()
    } else {
        format!("This report covers {} pictures.", summary.rows)
    };
    let mut lines = vec![
        "# Report".to_string(),
        String::new(),
        opening,
        String::new(),
        "It uses two tables.".to_string(),
        String::new(),
        "Blue A's table scores each 25-second picture. `bat` is the call score. `baf` is the not-a-call score. The bigger number is Blue A's answer for that picture.".to_string(),
        String::new(),
        "Laya's table sorts those written rows. Each row lands in call, not-call, or review.".to_string(),
        String::new(),
        "## What the tables say".to_string(),
        String::new(),
    ];
    let mut piles = Vec::new();
    if summary.call > 0 {
        piles.push(format!("{} went to call.", count_phrase(summary.call, "picture")));
    }
    if summary.not_call > 0 {
        piles.push(format!("{} went to not-call.", count_phrase(summary.not_call, "picture")));
    }
    if summary.review > 0 {
        piles.push(format!("{} went to review.", count_phrase(summary.review, "picture")));
    }
    if piles.is_empty() {
        piles.push("No picture received a label.".to_string());
    }
    lines.push(piles.join(" "));
    lines.push(String::new());
    if let Some(highest) = &summary.highest {
        let baf_text = highest
            .baf
            .map(|value| format!("{value:.3}"))
            .unwrap_or_else(|| "missing".to_string());
        lines.push(format!(
            "The highest call score in Blue A's table is {:.3} on {}, from {} to {} seconds. The not-a-call score on that same picture is {}.",
            highest.bat, highest.sample_id, highest.picture_start_s, highest.picture_end_s, baf_text
        ));
        lines.push(String::new());
    }
    let mut agree = Vec::new();
    if summary.agree > 0 {
        agree.push(format!(
            "On {}, Blue A and Laya gave the same answer.",
            count_phrase(summary.agree, "picture")
        ));
    }
    if summary.blue_a > 0 {
        agree.push(format!(
            "On {}, Laya was unsure, so Blue A's answer stayed.",
            count_phrase(summary.blue_a, "picture")
        ));
    }
    if summary.disagree > 0 {
        agree.push(format!(
            "On {}, they disagreed, so the row went to review.",
            count_phrase(summary.disagree, "picture")
        ));
    }
    if !agree.is_empty() {
        lines.push(agree.join(" "));
        lines.push(String::new());
    }
    lines.push("## Each sample".to_string());
    lines.push(String::new());
    for sample in &summary.samples {
        let bat_text = sample
            .highest_bat
            .map(|value| format!("{value:.3}"))
            .unwrap_or_else(|| "none".to_string());
        let call_text = if sample.call > 0 {
            format!("{} sorted as call.", count_phrase(sample.call, "picture"))
        } else {
            "None sorted as call.".to_string()
        };
        let noise = sample
            .noise_db
            .as_ref()
            .map(|value| format!(" The 63 Hz level for this sample is {value}."))
            .unwrap_or_default();
        lines.push(format!(
            "- {}: {}. Highest call score {bat_text}. {call_text}{noise}",
            sample.sample_id,
            count_phrase(sample.pictures, "picture")
        ));
    }
    lines.push(String::new());
    if summary.noise_attached {
        lines.push("A 63 Hz level was written next to each sample that had one. That number stands for low-frequency noise.".to_string());
    } else {
        lines.push("No 63 Hz level was attached to this table.".to_string());
    }
    lines.push(String::new());
    lines.push("These numbers come from the two tables. A miss rate, or a comparison of quieter hours and noisier hours, needs the call shape more than once in a quieter hour and more than once in a noisier hour.".to_string());
    if let Some(reading) = reading {
        let plain = match reading.pattern.as_str() {
            "one-spike" => " One picture stands out as a call. The rest stay low.",
            "flat" => " The call scores stay low from picture to picture.",
            "too-few" => " There are not enough call pictures to compare a quieter hour with a noisier hour.",
            _ => "",
        };
        lines.push(String::new());
        lines.push("## What Laya said about these counts".to_string());
        lines.push(String::new());
        lines.push(format!(
            "Laya's pattern word is {}.{} The chance Laya gave that word is {:.3}.",
            reading.pattern, plain, reading.pattern_probability
        ));
        lines.push(String::new());
        lines.push(format!(
            "Can these tables support a miss rate or a noise comparison? Laya said {}. The chance of yes was {:.3}.",
            reading.rate_ready, reading.rate_ready_probability
        ));
        lines.push(String::new());
        lines.push("Laya read the counts from the two tables. It did not listen to the recordings.".to_string());
    }
    lines.push(String::new());
    lines.join("\n")
}

#[cfg(test)]
mod tests {
    use super::{render_report, summarize, Reading};
    use crate::table::SoundRow;
    use std::collections::HashMap;

    fn row(
        sample: &str,
        candidate: &str,
        start: &str,
        end: &str,
        bat: &str,
        baf: &str,
        label: &str,
    ) -> SoundRow {
        SoundRow {
            sample_id: sample.to_string(),
            candidate_id: candidate.to_string(),
            picture_start_s: start.to_string(),
            picture_end_s: end.to_string(),
            bat: bat.to_string(),
            baf: baf.to_string(),
            sound_label: label.to_string(),
            image_file: String::new(),
            laya_choice: label.to_string(),
            laya_probability: "0.800000".to_string(),
            mix_label: label.to_string(),
            mix_reason: "agree".to_string(),
        }
    }

    #[test]
    fn report_states_the_counts_before_any_reading() {
        let rows = vec![
            row("sample-a", "sample-a-004", "92.416", "98.56", "0.507124", "0.492876", "call"),
            row("sample-c", "sample-c-001", "0.256", "3.84", "0.032918", "0.967082", "not-call"),
        ];
        let summary = summarize(&rows, &HashMap::new());
        let text = render_report(
            &summary,
            Some(&Reading {
                pattern: "one-spike".to_string(),
                pattern_probability: 0.7,
                rate_ready: "no".to_string(),
                rate_ready_probability: 0.2,
            }),
        );
        let cover = text.find("This report covers 2 pictures.").unwrap();
        let reading = text.find("What Laya said").unwrap();
        assert!(cover < reading);
        assert!(text.contains("highest call score in Blue A's table is 0.507"));
        assert!(text.contains("1 picture went to call."));
        assert!(text.contains("None sorted as call."));
        assert!(!text.contains("0 pictures"));
        assert!(text.contains("Laya said no."));
        assert!(text.contains("No 63 Hz level was attached"));
        assert!(text.contains("One picture stands out as a call."));
    }
}
