use anyhow::Result;
use clap::{Parser, Subcommand};
use cogym_core::{commitment, PackManifest};
use std::path::PathBuf;

#[derive(Parser)]
#[command(name="cogym", version, about="Deterministic cognition gym + portable cognitive packs")]
struct Cli { #[command(subcommand)] cmd: Cmd }

#[derive(Subcommand)]
enum Cmd {
    PackId { manifest: PathBuf },
    Commit { domain: String, json: PathBuf },
}

fn main() -> Result<()> {
    let cli = Cli::parse();
    match cli.cmd {
        Cmd::PackId { manifest } => {
            let pack: PackManifest = serde_json::from_slice(&std::fs::read(manifest)?)?;
            println!("{}", pack.id()?);
        }
        Cmd::Commit { domain, json } => {
            let v: serde_json::Value = serde_json::from_slice(&std::fs::read(json)?)?;
            println!("{}", commitment(&domain, &v)?);
        }
    }
    Ok(())
}
