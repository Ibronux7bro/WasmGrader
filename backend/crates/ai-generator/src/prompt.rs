use moodle_wasm_common::AIGenerateRequest;

pub fn build_system_prompt() -> &'static str {
    r#"You are an expert Computer Science Professor and Automated Assessment Designer.
Your task is to generate high-quality, comprehensive test cases for a student programming assignment.

Guidelines for generated test cases:
1. Include basic happy path / standard input cases.
2. Include edge cases (e.g. 0, negative numbers, empty or whitespace strings, boundary values, single element vs large inputs).
3. The input format must strictly match standard competitive programming conventions (e.g., newline-delimited inputs).
4. The expected_output must be deterministic and exact.
5. Distribute is_hidden: true for secret test cases (for grading) and false for public sample cases.

Respond ONLY with valid JSON matching the schema provided."#
}

pub fn build_user_prompt(req: &AIGenerateRequest) -> String {
    let ref_sol_text = match &req.reference_solution {
        Some(sol) => format!("\nReference Solution:\n```\n{}\n```\n", sol),
        None => String::new(),
    };

    format!(
        r#"Generate exactly {} test cases for the following assignment:

Title: {}
Language: {:?}
Description:
{}
{}
Output schema:
{{
  "test_cases": [
    {{
      "id": 1,
      "name": "Standard test case",
      "input": "...",
      "expected_output": "...",
      "is_hidden": false,
      "weight": 10.0,
      "test_type": "standard"
    }}
  ]
}}"#,
        req.number_of_tests,
        req.assignment_title,
        req.language,
        req.assignment_description,
        ref_sol_text
    )
}
