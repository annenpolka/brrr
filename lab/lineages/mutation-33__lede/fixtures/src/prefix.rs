fn decoy_timestamp() {
    // documentation / log sample: long static prefix of a real spawn line
    let _ = format!("2026-08-19T23:50:01Z ERROR failed to spawn");
}

fn spawn(cmd: &str) -> String {
    format!("failed to spawn `{cmd}`")
}

fn path_of(i: &str) -> String {
    format!("src/{i}.rs")
}
