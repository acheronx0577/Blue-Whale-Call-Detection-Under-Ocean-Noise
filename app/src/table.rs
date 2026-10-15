use serde::Deserialize;

#[derive(Clone, Debug, PartialEq)]
pub struct SoundRow {
    pub sample_id: String,
    pub candidate_id: String,
    pub picture_start_s: String,
    pub picture_end_s: String,
    pub bat: String,
    pub baf: String,
    pub sound_label: String,
    pub image_file: String,
    pub laya_choice: String,
    pub laya_probability: String,
    pub mix_label: String,
    pub mix_reason: String,
}

#[derive(Debug, Deserialize)]
struct RawScore {
    #[serde(default)]
    sample_id: String,
    #[serde(default)]
    candidate_id: String,
    #[serde(default)]
    status: String,
    #[serde(default)]
    bat: String,
    #[serde(default)]
    bat_score: String,
    #[serde(default)]
    baf: String,
    #[serde(default)]
    baf_score: String,
    #[serde(default)]
    centered_window_start_s: String,
    #[serde(default)]
    picture_start_s: String,
    #[serde(default)]
    proposal_start_s: String,
    #[serde(default)]
    centered_window_end_s: String,
    #[serde(default)]
    picture_end_s: String,
    #[serde(default)]
    proposal_end_s: String,
    #[serde(default)]
    image_file: String,
    #[serde(default)]
    laya_choice: String,
    #[serde(default)]
    laya_probability: String,
}

fn first_present(values: &[String]) -> String {
    values
        .iter()
        .find(|value| !value.is_empty())
        .cloned()
        .unwrap_or_default()
}

fn score_text(primary: &str, alias: &str) -> Option<f64> {
    let text = if !primary.is_empty() { primary } else { alias };
    if text.is_empty() {
        None
    } else {
        text.parse().ok()
    }
}

pub fn rows_from_blue_a(path: &std::path::Path) -> Result<Vec<SoundRow>, csv::Error> {
    let mut reader = csv::Reader::from_path(path)?;
    let mut rows = Vec::new();
    for record in reader.deserialize() {
        let raw: RawScore = record?;
        let status = if raw.status.is_empty() {
            "scored".to_string()
        } else {
            raw.status
        };
        if status != "scored" {
            continue;
        }
        let Some(bat) = score_text(&raw.bat, &raw.bat_score) else {
            continue;
        };
        let Some(baf) = score_text(&raw.baf, &raw.baf_score) else {
            continue;
        };
        let sound = crate::mix::sound_label(bat, baf).to_string();
        let mut row = SoundRow {
            sample_id: raw.sample_id,
            candidate_id: raw.candidate_id,
            picture_start_s: first_present(&[
                raw.centered_window_start_s,
                raw.picture_start_s,
                raw.proposal_start_s,
            ]),
            picture_end_s: first_present(&[
                raw.centered_window_end_s,
                raw.picture_end_s,
                raw.proposal_end_s,
            ]),
            bat: format!("{bat:.6}"),
            baf: format!("{baf:.6}"),
            sound_label: sound,
            image_file: raw.image_file,
            laya_choice: raw.laya_choice,
            laya_probability: raw.laya_probability,
            mix_label: String::new(),
            mix_reason: String::new(),
        };
        apply_saved_laya(&mut row);
        rows.push(row);
    }
    Ok(rows)
}

pub fn apply_saved_laya(row: &mut SoundRow) {
    let probability = row.laya_probability.parse::<f64>().unwrap_or(0.0);
    let (label, reason) = crate::mix::mix_label(&row.sound_label, &row.laya_choice, probability);
    if !row.laya_choice.is_empty() {
        row.laya_probability = format!("{probability:.6}");
    }
    row.mix_label = label;
    row.mix_reason = reason;
}

#[cfg(test)]
mod tests {
    use super::rows_from_blue_a;
    use std::io::Write;

    #[test]
    fn blue_a_csv_skips_unscored_rows() {
        let dir = std::env::temp_dir().join(format!("whale-mix-{}", std::process::id()));
        std::fs::create_dir_all(&dir).unwrap();
        let path = dir.join("scores.csv");
        let mut file = std::fs::File::create(&path).unwrap();
        writeln!(
            file,
            "sample_id,candidate_id,status,bat_score,baf_score,centered_window_start_s,centered_window_end_s,image_file"
        )
        .unwrap();
        writeln!(
            file,
            "sample-a,sample-a-004,scored,0.507124,0.492876,92.416,98.56,a.jpg"
        )
        .unwrap();
        writeln!(file, "sample-b,sample-b-001,not_scored: edge,,,,,").unwrap();
        let rows = rows_from_blue_a(&path).unwrap();
        assert_eq!(rows.len(), 1);
        assert_eq!(rows[0].sound_label, "call");
        assert_eq!(rows[0].picture_start_s, "92.416");
        assert_eq!(rows[0].bat, "0.507124");
        let _ = std::fs::remove_dir_all(&dir);
    }

    #[test]
    fn saved_laya_choice_sets_the_mix_label() {
        let mut row = super::SoundRow {
            sample_id: "sample-c".to_string(),
            candidate_id: String::new(),
            picture_start_s: String::new(),
            picture_end_s: String::new(),
            bat: "0.030000".to_string(),
            baf: "0.970000".to_string(),
            sound_label: "not-call".to_string(),
            image_file: String::new(),
            laya_choice: "not-call".to_string(),
            laya_probability: "0.91".to_string(),
            mix_label: String::new(),
            mix_reason: String::new(),
        };
        super::apply_saved_laya(&mut row);
        assert_eq!(row.mix_label, "not-call");
        assert_eq!(row.mix_reason, "agree");
        assert_eq!(row.laya_probability, "0.910000");
    }
}
