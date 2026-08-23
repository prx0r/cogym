use crate::{commitment, BehavioralSignature};
use anyhow::Result;
use serde::{Deserialize, Serialize};
use std::collections::BTreeMap;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ContentRef {
    pub hash: String,
    pub media_type: String,
    pub role: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RetrievalRecipe {
    pub query_template: String,
    pub top_k: u16,
    pub memory_kind: String,
    pub ordering: String,
    pub metadata_filters: BTreeMap<String, String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct InductionStep {
    pub name: String,
    pub instruction_ref: ContentRef,
    pub required: bool,
    pub max_tokens: Option<u32>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct OutputContract {
    pub schema_ref: ContentRef,
    pub invariants: Vec<String>,
}

/// A Pack is a portable context program. It does not contain model weights and does not
/// claim an internal mental state. It defines how to construct context and what behavioral
/// phenotype was empirically observed on a benchmark suite.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PackManifest {
    pub protocol: String,
    pub name: String,
    pub version: String,
    pub task_family: String,
    pub induction: Vec<InductionStep>,
    pub exemplars: Vec<ContentRef>,
    pub retrieval: Vec<RetrievalRecipe>,
    pub tool_policy_refs: Vec<ContentRef>,
    pub output_contract: OutputContract,
    pub target_signature: Option<BehavioralSignature>,
    pub provenance: BTreeMap<String, String>,
}

impl PackManifest {
    pub fn id(&self) -> Result<String> {
        commitment("COGYM:PACK:v1", self)
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CompiledContext {
    pub pack_id: String,
    pub model_family: String,
    pub messages: Vec<CompiledMessage>,
    pub retrieved_memory_ids: Vec<String>,
    pub tool_schema_hashes: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CompiledMessage {
    pub role: String,
    pub content: String,
}

impl CompiledContext {
    pub fn id(&self) -> Result<String> {
        commitment("COGYM:CONTEXT:v1", self)
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PackCertificate {
    pub pack_id: String,
    pub benchmark_suite_id: String,
    pub model_commitment: String,
    pub trials: u32,
    pub baseline_score: f64,
    pub packed_score: f64,
    pub behavior_distance: Option<f64>,
    pub inference_proof_refs: Vec<String>,
    pub evaluator_commitment: String,
}
