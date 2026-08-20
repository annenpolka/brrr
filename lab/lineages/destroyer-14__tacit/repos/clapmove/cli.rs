enum Command {
    HookPostTool {
        #[arg(long, default_value = "cursor")]
        agent: String,
    },
}
fn examples() {
    let a = "kizu hook-post-tool --agent claude-code";
    let b = "kizu hook-post-tool --agent cursor";
    let c = "kizu hook-post-tool";
}
