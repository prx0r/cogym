use anyhow::{Context, Result};
use cogym_core::commitment;
use serde::{Deserialize, Serialize};
use std::path::{Path, PathBuf};
use std::process::Command;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct InferenceClaim {
    pub model_commitment: String,
    pub compiled_context_commitment: String,
    pub output_commitment: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ProofReceipt {
    pub claim: InferenceClaim,
    pub prover: String,
    pub proof_path: PathBuf,
    pub proof_commitment: String,
}

/// Thin adapter intentionally avoids depending on unstable DeepProve internals.
/// Configure a reviewed wrapper command that accepts claim JSON and emits a proof file.
pub fn prove_with_command(wrapper: &Path, claim: &InferenceClaim, out: &Path) -> Result<ProofReceipt> {
    let claim_json = serde_json::to_string(claim)?;
    let status = Command::new(wrapper)
        .arg("prove")
        .arg("--claim-json").arg(&claim_json)
        .arg("--out").arg(out)
        .status().context("failed to execute DeepProve wrapper")?;
    if !status.success() { anyhow::bail!("DeepProve wrapper failed: {status}"); }
    let bytes = std::fs::read(out)?;
    Ok(ProofReceipt {
        claim: claim.clone(),
        prover: "deep-prove".into(),
        proof_path: out.to_path_buf(),
        proof_commitment: commitment("COGYM:PROOF:v1", &bytes)?,
    })
}
