use reqwest::Client;
use serde_json::json;

use moodle_wasm_common::{
    AIGenerateRequest, AIGenerateResponse, EvaluatorError, Result, TestCase,
};

use crate::prompt::{build_system_prompt, build_user_prompt};

pub struct AITestGeneratorClient {
    client: Client,
    api_key: String,
    model: String,
}

impl AITestGeneratorClient {
    pub fn new() -> Result<Self> {
        let api_key = std::env::var("GEMINI_API_KEY")
            .or_else(|_| std::env::var("AI_API_KEY"))
            .unwrap_or_default();

        let model = std::env::var("AI_MODEL").unwrap_or_else(|_| "gemini-1.5-flash".to_string());

        Ok(Self {
            client: Client::new(),
            api_key,
            model,
        })
    }

    pub async fn generate_test_cases(&self, req: &AIGenerateRequest) -> Result<AIGenerateResponse> {
        if self.api_key.is_empty() {
            tracing::warn!("AI API key not set; generating mock standard test cases");
            return Ok(Self::generate_fallback_cases(req));
        }

        let url = format!(
            "https://generativelanguage.googleapis.com/v1beta/models/{}:generateContent?key={}",
            self.model, self.api_key
        );

        let system_prompt = build_system_prompt();
        let user_prompt = build_user_prompt(req);

        let payload = json!({
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        { "text": format!("{}\n\n{}", system_prompt, user_prompt) }
                    ]
                }
            ],
            "generationConfig": {
                "response_mime_type": "application/json",
                "temperature": 0.2
            }
        });

        let resp = self
            .client
            .post(&url)
            .json(&payload)
            .send()
            .await
            .map_err(|e| EvaluatorError::AIGenerationFailed(e.to_string()))?;

        if !resp.status().is_success() {
            let status = resp.status();
            let body = resp.text().await.unwrap_or_default();
            return Err(EvaluatorError::AIGenerationFailed(format!(
                "API request failed (status {}): {}",
                status, body
            )));
        }

        let resp_json: serde_json::Value = resp
            .json()
            .await
            .map_err(|e| EvaluatorError::AIGenerationFailed(e.to_string()))?;

        let text_content = resp_json["candidates"][0]["content"]["parts"][0]["text"]
            .as_str()
            .ok_or_else(|| {
                EvaluatorError::AIGenerationFailed("Invalid response structure from AI".to_string())
            })?;

        let parsed: AIGenerateResponse = serde_json::from_str(text_content).map_err(|e| {
            EvaluatorError::AIGenerationFailed(format!(
                "Failed to parse AI output into TestCase schema: {}. Raw: {}",
                e, text_content
            ))
        })?;

        Ok(parsed)
    }

    fn generate_fallback_cases(req: &AIGenerateRequest) -> AIGenerateResponse {
        let mut test_cases = Vec::new();
        for i in 1..=req.number_of_tests {
            test_cases.push(TestCase {
                id: i as u32,
                name: format!("Auto-generated case {}", i),
                input: format!("{}\n", i * 10),
                expected_output: format!("{}\n", i * 10),
                is_hidden: i > 2,
                weight: 10.0,
                test_type: if i == 1 {
                    "standard".to_string()
                } else {
                    "boundary".to_string()
                },
            });
        }
        AIGenerateResponse { test_cases }
    }
}
