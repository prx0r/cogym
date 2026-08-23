use serde::{Deserialize, Serialize};
use std::collections::BTreeMap;

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct BehavioralSignature {
    /// Named, normalized metrics in [0,1]. Examples: risk_aversion, confidence,
    /// revision_rate, evidence_demand, contrarianism.
    pub metrics: BTreeMap<String, f64>,
    pub sample_count: u32,
}

impl BehavioralSignature {
    /// Mean absolute distance across shared dimensions. 0 == identical phenotype.
    pub fn distance(&self, other: &Self) -> Option<f64> {
        let mut total = 0.0;
        let mut n = 0usize;
        for (k, a) in &self.metrics {
            if let Some(b) = other.metrics.get(k) {
                total += (a - b).abs();
                n += 1;
            }
        }
        (n > 0).then_some(total / n as f64)
    }

    pub fn in_basin(&self, target: &Self, max_distance: f64) -> bool {
        self.distance(target).is_some_and(|d| d <= max_distance)
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct InductionMeasurement {
    pub compiled_context_commitment: String,
    pub tokens_consumed: u64,
    pub turns_consumed: u32,
    pub signature: BehavioralSignature,
    pub target_distance: Option<f64>,
    /// Number of subsequent neutral tasks before phenotype exits the target basin.
    pub retention_steps: Option<u32>,
}
