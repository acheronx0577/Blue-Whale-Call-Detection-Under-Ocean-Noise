use crate::table::SoundRow;
use std::path::Path;

pub struct ExportCounts {
    pub call: usize,
    pub not_call: usize,
    pub review: usize,
    pub rows: usize,
}

pub fn export_rows(rows: &[SoundRow], out_dir: &Path) -> std::io::Result<ExportCounts> {
    std::fs::create_dir_all(out_dir)?;
    let mut writer = csv::Writer::from_path(out_dir.join("decisions.csv"))?;
    writer.write_record([
        "sample_id",
        "candidate_id",
        "picture_start_s",
        "picture_end_s",
        "bat",
        "baf",
        "sound_label",
        "laya_choice",
        "laya_probability",
        "mix_label",
        "mix_reason",
        "image_file",
    ])?;
    let mut payload = Vec::new();
    for row in rows {
        writer.write_record([
            &row.sample_id,
            &row.candidate_id,
            &row.picture_start_s,
            &row.picture_end_s,
            &row.bat,
            &row.baf,
            &row.sound_label,
            &row.laya_choice,
            &row.laya_probability,
            &row.mix_label,
            &row.mix_reason,
            &row.image_file,
        ])?;
        payload.push(serde_json::json!({
            "sample_id": row.sample_id,
            "candidate_id": row.candidate_id,
            "picture_start_s": row.picture_start_s,
            "picture_end_s": row.picture_end_s,
            "bat": row.bat,
            "baf": row.baf,
            "sound_label": row.sound_label,
            "laya_choice": row.laya_choice,
            "laya_probability": row.laya_probability,
            "mix_label": row.mix_label,
            "mix_reason": row.mix_reason,
            "image_file": row.image_file,
        }));
    }
    writer.flush()?;
    std::fs::write(
        out_dir.join("decisions.json"),
        serde_json::to_string_pretty(&payload).unwrap(),
    )?;
    let mut counts = ExportCounts {
        call: 0,
        not_call: 0,
        review: 0,
        rows: rows.len(),
    };
    for label in ["call", "not-call", "review"] {
        let folder = out_dir.join(label);
        std::fs::create_dir_all(&folder)?;
        let mut lines = Vec::new();
        for row in rows {
            if row.mix_label != label {
                continue;
            }
            match label {
                "call" => counts.call += 1,
                "not-call" => counts.not_call += 1,
                "review" => counts.review += 1,
                _ => {}
            }
            let name = if !row.candidate_id.is_empty() {
                &row.candidate_id
            } else if !row.image_file.is_empty() {
                &row.image_file
            } else {
                &row.sample_id
            };
            lines.push(format!(
                "{name}\t{}\t{}\t{}",
                row.sample_id, row.picture_start_s, row.picture_end_s
            ));
        }
        let text = if lines.is_empty() {
            String::new()
        } else {
            format!("{}\n", lines.join("\n"))
        };
        std::fs::write(folder.join("manifest.txt"), text)?;
    }
    Ok(counts)
}

pub fn write_report(
    rows: &[SoundRow],
    out_dir: &Path,
    noise: &std::collections::HashMap<String, String>,
) -> std::io::Result<String> {
    let summary = crate::report::summarize(rows, noise);
    let text = crate::report::render_report(&summary, None);
    std::fs::create_dir_all(out_dir)?;
    std::fs::write(out_dir.join("report.md"), &text)?;
    Ok(text)
}

#[cfg(test)]
mod tests {
    use super::export_rows;
    use crate::table::SoundRow;

    fn sample() -> SoundRow {
        SoundRow {
            sample_id: "sample-a".to_string(),
            candidate_id: "sample-a-004".to_string(),
            picture_start_s: "92.416".to_string(),
            picture_end_s: "98.56".to_string(),
            bat: "0.507124".to_string(),
            baf: "0.492876".to_string(),
            sound_label: "call".to_string(),
            image_file: "a.jpg".to_string(),
            laya_choice: "call".to_string(),
            laya_probability: "0.800000".to_string(),
            mix_label: "call".to_string(),
            mix_reason: "agree".to_string(),
        }
    }

    #[test]
    fn export_writes_three_formats() {
        let dir = std::env::temp_dir().join(format!("whale-mix-export-{}", std::process::id()));
        let _ = std::fs::remove_dir_all(&dir);
        let counts = export_rows(&[sample()], &dir).unwrap();
        assert_eq!(counts.call, 1);
        assert!(dir.join("decisions.csv").is_file());
        let payload: serde_json::Value =
            serde_json::from_str(&std::fs::read_to_string(dir.join("decisions.json")).unwrap()).unwrap();
        assert_eq!(payload[0]["mix_label"], "call");
        let manifest = std::fs::read_to_string(dir.join("call").join("manifest.txt")).unwrap();
        assert!(manifest.contains("sample-a-004"));
        assert_eq!(
            std::fs::read_to_string(dir.join("not-call").join("manifest.txt")).unwrap(),
            ""
        );
        let _ = std::fs::remove_dir_all(&dir);
    }
}
