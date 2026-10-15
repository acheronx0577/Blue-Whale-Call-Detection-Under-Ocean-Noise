use std::env;
use std::path::PathBuf;
use std::process::ExitCode;

fn main() -> ExitCode {
    let args: Vec<String> = env::args().skip(1).collect();
    if args.is_empty() {
        eprintln!("window arrives in the next task");
        return ExitCode::from(2);
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
