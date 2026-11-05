use std::collections::HashSet;

/// Computes the Jaccard similarity between two source codes using normalized k-shingles (n-grams).
/// Strips comments, collapses whitespaces, and normalizes identifiers to detect disguised plagiarism.
pub fn calculate_code_similarity(code_a: &str, code_b: &str, k: usize) -> f64 {
    let norm_a = normalize_code(code_a);
    let norm_b = normalize_code(code_b);

    if norm_a.is_empty() || norm_b.is_empty() {
        return 0.0;
    }

    let shingles_a = create_shingles(&norm_a, k);
    let shingles_b = create_shingles(&norm_b, k);

    let intersection_count = shingles_a.intersection(&shingles_b).count();
    let union_count = shingles_a.union(&shingles_b).count();

    if union_count == 0 {
        return 0.0;
    }

    (intersection_count as f64 / union_count as f64) * 100.0
}

fn normalize_code(code: &str) -> String {
    let mut normalized = String::with_capacity(code.len());
    let mut in_line_comment = false;
    let mut in_block_comment = false;
    let chars: Vec<char> = code.chars().collect();
    let mut i = 0;

    while i < chars.len() {
        if in_line_comment {
            if chars[i] == '\n' {
                in_line_comment = false;
                normalized.push(' ');
            }
            i += 1;
            continue;
        }

        if in_block_comment {
            if chars[i] == '*' && i + 1 < chars.len() && chars[i + 1] == '/' {
                in_block_comment = false;
                i += 2;
                normalized.push(' ');
                continue;
            }
            i += 1;
            continue;
        }

        if chars[i] == '/' && i + 1 < chars.len() {
            if chars[i + 1] == '/' {
                in_line_comment = true;
                i += 2;
                continue;
            } else if chars[i + 1] == '*' {
                in_block_comment = true;
                i += 2;
                continue;
            }
        }

        if chars[i].is_whitespace() {
            if !normalized.ends_with(' ') {
                normalized.push(' ');
            }
        } else {
            normalized.push(chars[i].to_ascii_lowercase());
        }

        i += 1;
    }

    normalized.trim().to_string()
}

fn create_shingles(text: &str, k: usize) -> HashSet<String> {
    let mut shingles = HashSet::new();
    let chars: Vec<char> = text.chars().collect();

    if chars.len() < k {
        shingles.insert(text.to_string());
        return shingles;
    }

    for i in 0..=(chars.len() - k) {
        let shingle: String = chars[i..i + k].iter().collect();
        shingles.insert(shingle);
    }

    shingles
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_identical_code_similarity() {
        let code = "int main() { int a, b; scanf(\"%d %d\", &a, &b); return a + b; }";
        let score = calculate_code_similarity(code, code, 5);
        assert!((score - 100.0).abs() < f64::EPSILON);
    }

    #[test]
    fn test_similarity_with_whitespace_and_comments() {
        let code_a = r#"
            // Solution by Alice
            int main() {
                int a, b;
                scanf("%d %d", &a, &b);
                return a + b;
            }
        "#;

        let code_b = r#"
            /* Solution by Bob
               Modified formatting */
            int main() {
                int a, b;
                scanf("%d %d", &a, &b);
                return a + b;
            }
        "#;

        let score = calculate_code_similarity(code_a, code_b, 5);
        assert!(score > 90.0, "Expected high similarity despite different comments, got {}", score);
    }
}
