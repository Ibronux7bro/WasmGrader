use std::io::{self, Read};

fn main() {
    let mut input = String::new();
    if io::stdin().read_to_string(&mut input).is_ok() {
        let parts: Vec<i64> = input
            .split_whitespace()
            .filter_map(|s| s.parse().ok())
            .collect();

        if parts.len() >= 2 {
            println!("{}", parts[0] + parts[1]);
        }
    }
}
