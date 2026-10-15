use std::process::Command;

#[test]
fn scores_flag_writes_report() {
    let dir = std::env::temp_dir().join(format!("whale-mix-cli-{}", std::process::id()));
    let _ = std::fs::remove_dir_all(&dir);
    std::fs::create_dir_all(&dir).unwrap();
    let scores = dir.join("scores.csv");
    std::fs::write(
        &scores,
        "sample_id,candidate_id,status,bat_score,baf_score,centered_window_start_s,centered_window_end_s,image_file\n\
sample-a,sample-a-004,scored,0.507124,0.492876,92.416,98.56,a.jpg\n",
    )
    .unwrap();
    let out = dir.join("mix");
    let status = Command::new(env!("CARGO_BIN_EXE_whale-mix"))
        .args(["--scores", scores.to_str().unwrap(), "--out", out.to_str().unwrap()])
        .status()
        .unwrap();
    assert!(status.success());
    let report = std::fs::read_to_string(out.join("report.md")).unwrap();
    assert!(report.contains("This report covers 1 picture."));
    assert!(report.contains("1 picture went to call."));
    let _ = std::fs::remove_dir_all(&dir);
}
