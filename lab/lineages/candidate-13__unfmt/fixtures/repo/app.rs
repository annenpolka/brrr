use anyhow::{anyhow, Context};

fn revert(stderr: &str) -> anyhow::Result<()> {
    Err(anyhow!("`git apply --reverse` failed: {}", stderr.trim()))
}

fn spawn() -> anyhow::Result<()> {
    Err(anyhow!("failed to spawn `git apply --reverse`"))
}

fn synth(rel: &str) -> String {
    format!("synthesizing untracked snapshot {}", rel)
}

fn header(rest: &str) -> anyhow::Result<()> {
    Err(anyhow!("unparseable `diff --git` header: {rest}"))
}
