use anyhow::{Context, Result};
use reqwest::{Client, StatusCode};
use serde::{Deserialize, Serialize};
use serde_json::{json, Value};
use std::time::Duration;

#[derive(Clone)]
pub struct HydraClient {
    http: Client,
    base_url: String,
    api_key: String,
    tenant_id: String,
    sub_tenant_id: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RecalledMemory {
    pub id: String,
    pub text: String,
    pub score: Option<f64>,
    pub raw: Value,
}

impl HydraClient {
    pub fn new(base_url: impl Into<String>, api_key: impl Into<String>, tenant_id: impl Into<String>, sub_tenant_id: Option<String>) -> Result<Self> {
        let http = Client::builder().timeout(Duration::from_secs(30)).build()?;
        Ok(Self { http, base_url: base_url.into().trim_end_matches('/').into(), api_key: api_key.into(), tenant_id: tenant_id.into(), sub_tenant_id })
    }

    async fn post_json(&self, path: &str, body: Value) -> Result<Value> {
        let mut delay_ms = 250u64;
        for attempt in 0..5 {
            let res = self.http.post(format!("{}{}", self.base_url, path))
                .bearer_auth(&self.api_key)
                .json(&body)
                .send().await.context("HydraDB request failed")?;
            if res.status() == StatusCode::TOO_MANY_REQUESTS && attempt < 4 {
                tokio::time::sleep(Duration::from_millis(delay_ms)).await;
                delay_ms *= 2;
                continue;
            }
            let status = res.status();
            let value: Value = res.json().await.context("invalid HydraDB JSON")?;
            if !status.is_success() { anyhow::bail!("HydraDB {}: {}", status, value); }
            return Ok(value);
        }
        unreachable!()
    }

    /// Store only distilled experience/method lessons, not raw market ticks.
    pub async fn add_memory(&self, text: &str) -> Result<Value> {
        let mut body = json!({
            "tenant_id": self.tenant_id,
            "memories": [{ "text": text, "infer": true }],
            "upsert": true
        });
        if let Some(sub) = &self.sub_tenant_id { body["sub_tenant_id"] = json!(sub); }
        self.post_json("/memories/add_memory", body).await
    }

    pub async fn recall(&self, query: &str, max_results: u16) -> Result<Value> {
        let mut body = json!({
            "tenant_id": self.tenant_id,
            "query": query,
            "max_results": max_results,
            "mode": "thinking"
        });
        if let Some(sub) = &self.sub_tenant_id { body["sub_tenant_id"] = json!(sub); }
        self.post_json("/recall/recall_preferences", body).await
    }
}
