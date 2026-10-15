use eframe::egui;
use std::env;
use std::path::PathBuf;
use std::process::ExitCode;

fn main() -> ExitCode {
    let args: Vec<String> = env::args().skip(1).collect();
    if args.is_empty() {
        return run_window();
    }
    let mut scores: Option<PathBuf> = None;
    let mut out: Option<PathBuf> = None;
    let mut index = 0;
    while index < args.len() {
        match args[index].as_str() {
            "--scores" => {
                index += 1;
                scores = args.get(index).map(PathBuf::from);
            }
            "--out" => {
                index += 1;
                out = args.get(index).map(PathBuf::from);
            }
            other => {
                eprintln!("unknown argument {other}");
                return ExitCode::from(2);
            }
        }
        index += 1;
    }
    let (Some(scores), Some(out)) = (scores, out) else {
        eprintln!("pass --scores and --out");
        return ExitCode::from(2);
    };
    match whale_mix::table::rows_from_blue_a(&scores) {
        Ok(rows) => {
            if let Err(error) = whale_mix::export::export_rows(&rows, &out) {
                eprintln!("{error}");
                return ExitCode::from(1);
            }
            if let Err(error) =
                whale_mix::export::write_report(&rows, &out, &std::collections::HashMap::new())
            {
                eprintln!("{error}");
                return ExitCode::from(1);
            }
            println!("{}", out.display());
            ExitCode::SUCCESS
        }
        Err(error) => {
            eprintln!("{error}");
            ExitCode::from(1)
        }
    }
}

fn run_window() -> ExitCode {
    let options = eframe::NativeOptions {
        viewport: egui::ViewportBuilder::default().with_inner_size([1100.0, 720.0]),
        ..Default::default()
    };
    match eframe::run_native(
        "Whale Mix",
        options,
        Box::new(|_cc| Ok(Box::new(WhaleApp::default()))),
    ) {
        Ok(()) => ExitCode::SUCCESS,
        Err(error) => {
            eprintln!("{error}");
            ExitCode::from(1)
        }
    }
}

struct WhaleApp {
    rows: Vec<whale_mix::table::SoundRow>,
    status: String,
}

impl Default for WhaleApp {
    fn default() -> Self {
        Self {
            rows: Vec::new(),
            status: "Open a Blue A score CSV.".to_string(),
        }
    }
}

impl eframe::App for WhaleApp {
    fn update(&mut self, ctx: &egui::Context, _frame: &mut eframe::Frame) {
        egui::CentralPanel::default().show(ctx, |ui| {
            ui.heading("Whale Mix");
            ui.label("Blue A names each picture. A saved Laya choice can move a row to review.");
            ui.horizontal(|ui| {
                if ui.button("Open scores CSV").clicked() {
                    if let Some(path) = rfd::FileDialog::new().add_filter("CSV", &["csv"]).pick_file() {
                        match whale_mix::table::rows_from_blue_a(&path) {
                            Ok(rows) => {
                                self.status = format!("{} pictures from {}", rows.len(), path.display());
                                self.rows = rows;
                            }
                            Err(error) => self.status = error.to_string(),
                        }
                    }
                }
                if ui.button("Export report").clicked() {
                    if self.rows.is_empty() {
                        self.status = "Open a score CSV first.".to_string();
                    } else if let Some(folder) = rfd::FileDialog::new().pick_folder() {
                        let exported = whale_mix::export::export_rows(&self.rows, &folder);
                        let reported = whale_mix::export::write_report(
                            &self.rows,
                            &folder,
                            &std::collections::HashMap::new(),
                        );
                        self.status = match (exported, reported) {
                            (Ok(counts), Ok(_)) => format!(
                                "Wrote {} pictures to {} (call {}, not-call {}, review {})",
                                counts.rows,
                                folder.display(),
                                counts.call,
                                counts.not_call,
                                counts.review
                            ),
                            (Err(error), _) | (_, Err(error)) => error.to_string(),
                        };
                    }
                }
            });
            ui.label(&self.status);
            egui::ScrollArea::vertical().show(ui, |ui| {
                for row in &self.rows {
                    ui.label(format!(
                        "{}  {}–{} s  bat {}  baf {}  {}  ({})",
                        row.sample_id,
                        row.picture_start_s,
                        row.picture_end_s,
                        row.bat,
                        row.baf,
                        row.mix_label,
                        row.mix_reason
                    ));
                }
            });
        });
    }
}
