use crate::commitment;
use anyhow::Result;
use serde::{Deserialize, Serialize};
use std::collections::BTreeMap;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WorldSnapshot {
    pub world_id: String,
    pub tick: u64,
    pub timestamp_ms: i64,
    pub instruments: BTreeMap<String, InstrumentState>,
    pub macro_features: BTreeMap<String, f64>,
    pub hidden_future_commitment: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct InstrumentState {
    pub price: f64,
    pub return_1: f64,
    pub volatility: f64,
    pub volume_z: f64,
    pub regime_direction: f64,
    pub regime_strength: f64,
    pub regime_confidence: f64,
    pub direction_change: f64,
    pub strength_change: f64,
    pub volatility_change: f64,
}

impl WorldSnapshot {
    pub fn id(&self) -> Result<String> {
        commitment("COGYM:WORLD-SNAPSHOT:v1", self)
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Decision {
    pub action: String,
    pub target_exposure: f64,
    pub forecast: f64,
    pub confidence: f64,
    pub claims: Vec<String>,
    pub falsifiers: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DecisionRecord {
    pub snapshot_id: String,
    pub agent_id: String,
    pub pack_id: Option<String>,
    pub compiled_context_id: String,
    pub private_decision: Decision,
    pub public_decision: Option<Decision>,
    pub peer_context_commitment: Option<String>,
}
