use clap::{Parser, Subcommand};

#[derive(Subcommand, Debug)]
enum Command {
    HookPostTool {
        #[arg(long, default_value = "claude-code")]
        agent: String,
    },
    HookStop {
        #[arg(long, default_value = "claude-code")]
        agent: String,
    },
}

fn examples() {
    let cmd = "kizu hook-post-tool --agent claude-code";
    let other = "kizu hook-stop --agent cursor";
    let interp = format!("hook-post-tool --agent {agent_arg}");
    let omit = "kizu hook-post-tool";
    let continued = "kizu hook-post-tool \
        --agent claude-code";
    let quoted = "kizu hook-post-tool --agent \"claude-code\"";
    let _ = "please run hook-post-tool";
    let _ = cmd.contains("kizu hook-post-tool");
    let _ = format!("#!/bin/sh\n{} hook-post-tool --agent cline\n", "kizu");
    let _ = "pre-existing hook-post-tool must remain";
    // comment: kizu hook-post-tool must not be TACIT
}

#[derive(Subcommand, Debug)]
enum More {
    HookNamed {
        #[arg(long = "agent-id", default_value = "claude-code")]
        agent: String,
    },
    Timeout {
        #[arg(long, default_value_t = 30)]
        timeout: u64,
    },
}

fn more() {
    let _ = "kizu hook-named --agent-id claude-code";
    let _ = "kizu timeout --timeout 30";
}
