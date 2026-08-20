fn apply_fail(stderr: &str) -> Result<(), String> {
    Err(format!("git diff single file failed: {}", stderr.trim()))
}

fn header(rest: &str) -> Result<(), String> {
    Err(format!("unparseable `diff --git` header: {rest}"))
}

fn synth(display: &str) -> String {
    format!("diff --git a/{display} b/{display}\n")
}
