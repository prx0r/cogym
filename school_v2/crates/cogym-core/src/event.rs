use crate::commitment;
use anyhow::Result;
use serde::{Deserialize, Serialize};
use serde_json::Value;
use uuid::Uuid;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Event {
    pub id: Uuid,
    pub kind: String,
    pub timestamp_ms: i64,
    pub parent: Option<Uuid>,
    pub payload: Value,
    pub previous_commitment: Option<String>,
}

impl Event {
    pub fn commitment(&self) -> Result<String> {
        commitment("COGYM:EVENT:v1", self)
    }
}
