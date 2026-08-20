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
    HookNamed {
        #[arg(long = "agent-id", default_value = "claude-code")]
        agent: String,
    },
    Timeout {
        #[arg(long, default_value_t = 30)]
        timeout: u32,
    },
}

fn examples() {
    let a = "kizu hook-post-tool --agent claude-code";
    let b = "kizu hook-post-tool --agent=claude-code";
    let c = "kizu hook-post-tool --agent \"claude-code\"";
    let d = "kizu hook-post-tool --agent 'claude-code'";
    let e = "kizu hook-post-tool";
    let f = "please run hook-post-tool later";
    let g = "command: hook-post-tool";
    let h = "$ hook-post-tool";
    let i = "kizu hook-post-tool \
        --agent claude-code";
    let j = format!("hook-post-tool --agent {agent_arg}");
    let k = "kizu hook-stop --agent cursor";
    let l = "kizu hook-named --agent-id claude-code";
    let m = "kizu hook-named --agent claude-code";
    let n = "kizu timeout --timeout 30";
    let o = "kizu hook-post-tool --agent cline\n";
    // comment: kizu hook-post-tool rides the default
    let p = "older kizu install of hook-post-tool";
}
