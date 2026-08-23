use crate::{BehavioralSignature, PackCertificate, PackManifest};
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CurriculumStage {
    pub id: String,
    pub benchmark_suite_id: String,
    pub min_score: f64,
    pub max_calibration_error: Option<f64>,
    pub max_behavior_distance: Option<f64>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Curriculum {
    pub school_id: String,
    pub task_family: String,
    pub stages: Vec<CurriculumStage>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ParticipantRun {
    pub participant_agent_id: String,
    pub claimed_model: String,
    pub model_proof_ref: Option<String>,
    pub consent_trace_reuse: bool,
    pub curriculum_stage: String,
    pub score: f64,
    pub signature: BehavioralSignature,
    pub trace_commitment: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GraduationArtifact {
    pub school_id: String,
    pub pack: PackManifest,
    pub certificate: PackCertificate,
}
