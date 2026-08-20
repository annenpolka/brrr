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
}
