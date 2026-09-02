# Reduced excerpt of load_global_rustc on failing_ref
# src/cargo/util/context/mod.rs

pub fn load_global_rustc(&self, ws: Option<&Workspace<'_>>) -> CargoResult<Rustc> {
    let cache_location = ws.map(|ws| {
        ws.target_dir()
            .join(".rustc_info.json")
            .into_path_unlocked()
    });
    let wrapper = self.maybe_get_tool("rustc_wrapper", &self.build_config()?.rustc_wrapper);
    let rustc_workspace_wrapper = self.maybe_get_tool(
        "rustc_workspace_wrapper",
        &self.build_config()?.rustc_workspace_wrapper,
    );

    Rustc::new(
        self.get_tool(Tool::Rustc, &self.build_config()?.rustc),
        wrapper,
        rustc_workspace_wrapper,
        &self
            .home()
            .join("bin")
            .join("rustc")
            .into_path_unlocked()
            .with_extension(env::consts::EXE_EXTENSION),
        if self.cache_rustc_info {
            cache_location
        } else {
            None
        },
        self,
    )
}

// cache_rustc_info is false only when env CARGO_CACHE_RUSTC_INFO is "0"
