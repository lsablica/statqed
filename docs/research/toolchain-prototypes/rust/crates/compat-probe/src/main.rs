#![forbid(unsafe_code)]

use clap::Parser;
use statqed_rust_compat_probe::observe_candidate_apis;

#[derive(Debug, Parser)]
#[command(about = "Observe candidate Rust dependency APIs", version)]
struct Cli {
    /// Emit compact JSON observations.
    #[arg(long)]
    json: bool,
}

fn main() -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
    let cli = Cli::parse();
    let observed = observe_candidate_apis()?;
    if cli.json {
        println!("{}", serde_json::to_string(&observed)?);
    } else {
        println!("{observed:#?}");
    }
    Ok(())
}
