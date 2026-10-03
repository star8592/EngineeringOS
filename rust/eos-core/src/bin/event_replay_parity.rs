use std::io::{self, Read};
use eos_core::{EventEnvelope,replay_events};
fn main(){let mut s=String::new();io::stdin().read_to_string(&mut s).unwrap();let e:Vec<EventEnvelope>=serde_json::from_str(&s).unwrap();let out=replay_events(&e).unwrap();println!("{}",serde_json::to_string(&out).unwrap());}
