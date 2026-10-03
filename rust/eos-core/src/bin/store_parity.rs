use eos_core::{EventEnvelope, storage};
use serde_json::{Value, json};
use std::env;

fn fail(e: impl std::fmt::Display) -> ! {
    eprintln!("{e}");
    std::process::exit(3)
}

fn main() {
    let a: Vec<String> = env::args().collect();
    if a.len() < 3 {
        fail("BAD_ARGS");
    }
    match a[1].as_str() {
        "append" => {
            let e: EventEnvelope = serde_json::from_str(&a[4]).unwrap_or_else(|e| fail(e));
            let v: u64 = a[3].parse().unwrap_or_else(|e| fail(e));
            storage::append_event_cas(&a[2], &e, Some(v)).unwrap_or_else(|e| fail(e));
            println!("OK")
        }
        "read" => {
            let x = storage::read_events(&a[2]).unwrap_or_else(|e| fail(e));
            println!("{}", serde_json::to_string(&x).unwrap())
        }
        "snapshot-write" => {
            let seq: u64 = a[3].parse().unwrap_or_else(|e| fail(e));
            let state: Value = serde_json::from_str(&a[4]).unwrap_or_else(|e| fail(e));
            let x = storage::write_snapshot(&a[2], seq, &state).unwrap_or_else(|e| fail(e));
            println!("{}", serde_json::to_string(&x).unwrap())
        }
        "snapshot-read" => {
            let x = storage::read_snapshot(&a[2]).unwrap_or_else(|e| fail(e));
            println!("{}", serde_json::to_string(&x).unwrap())
        }
        _ => {
            println!("{}", json!({"error":"bad command"}));
            std::process::exit(2)
        }
    }
}
