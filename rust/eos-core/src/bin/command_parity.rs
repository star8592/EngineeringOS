use eos_core::{EventEnvelope, command_retry_decision, replay_command_events};
use serde::Deserialize;
use serde_json::json;
use std::io::{self, Read};
#[derive(Deserialize)]
struct Input {
    command_id: String,
    events: Vec<EventEnvelope>,
}
fn main() {
    let mut s = String::new();
    io::stdin().read_to_string(&mut s).unwrap();
    let i: Input = serde_json::from_str(&s).unwrap();
    let st = replay_command_events(&i.events, &i.command_id).unwrap();
    println!(
        "{}",
        json!({"state":st,"retry_decision":command_retry_decision(st.as_ref())})
    );
}
