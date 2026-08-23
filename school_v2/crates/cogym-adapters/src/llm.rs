use anyhow::{Context, Result};
use async_trait::async_trait;
use cogym_core::{CompiledContext, Decision};
use reqwest::Client;
use serde_json::{json, Value};

#[async_trait]
pub trait DecisionModel: Send + Sync {
    fn model_id(&self) -> &str;
    async fn decide(&self, context: &CompiledContext) -> Result<Decision>;
}

/// Minimal OpenAI-compatible adapter. Providers remain replaceable; Cogym owns the
/// context compiler and output contract, not provider-specific orchestration.
pub struct OpenAiCompatible {
    client: Client,
    base_url: String,
    api_key: String,
    model: String,
}

impl OpenAiCompatible {
    pub fn new(base_url: impl Into<String>, api_key: impl Into<String>, model: impl Into<String>) -> Self {
        Self { client: Client::new(), base_url: base_url.into().trim_end_matches('/').into(), api_key: api_key.into(), model: model.into() }
    }
}

#[async_trait]
impl DecisionModel for OpenAiCompatible {
    fn model_id(&self) -> &str { &self.model }

    async fn decide(&self, context: &CompiledContext) -> Result<Decision> {
        let messages: Vec<Value> = context.messages.iter().map(|m| json!({"role":m.role,"content":m.content})).collect();
        let res = self.client.post(format!("{}/chat/completions", self.base_url))
            .bearer_auth(&self.api_key)
            .json(&json!({
                "model": self.model,
                "temperature": 0,
                "messages": messages,
                "response_format": {"type":"json_object"}
            }))
            .send().await.context("LLM request failed")?;
        let status = res.status();
        let v: Value = res.json().await?;
        if !status.is_success() { anyhow::bail!("LLM {}: {}", status, v); }
        let text = v.pointer("/choices/0/message/content").and_then(Value::as_str).context("missing model output")?;
        Ok(serde_json::from_str(text).context("decision did not match output contract")?)
    }
}
