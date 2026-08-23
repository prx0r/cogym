use anyhow::Result;
use serde::Serialize;
use serde_json::{Map, Value};
use sha3::{Digest, Keccak256};

pub fn canonicalize(value: Value) -> Value {
    match value {
        Value::Object(map) => {
            let mut pairs: Vec<(String, Value)> = map.into_iter().collect();
            pairs.sort_by(|a, b| a.0.cmp(&b.0));
            let mut out = Map::new();
            for (k, v) in pairs {
                out.insert(k, canonicalize(v));
            }
            Value::Object(out)
        }
        Value::Array(xs) => Value::Array(xs.into_iter().map(canonicalize).collect()),
        other => other,
    }
}

pub fn canonical_json<T: Serialize>(value: &T) -> Result<Vec<u8>> {
    let v = serde_json::to_value(value)?;
    Ok(serde_json::to_vec(&canonicalize(v))?)
}

pub fn commitment<T: Serialize>(domain: &str, value: &T) -> Result<String> {
    let payload = canonical_json(value)?;
    let mut hasher = Keccak256::new();
    hasher.update(domain.as_bytes());
    hasher.update([0u8]);
    hasher.update(payload);
    Ok(format!("0x{}", hex::encode(hasher.finalize())))
}
