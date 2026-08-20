pub fn diff_single_file(root: &Path, baseline_sha: &str, file_path: &Path) -> Result<String> {
    let rel = file_path.strip_prefix(root).unwrap_or(file_path);
    let output = Command::new("git").output()?;
    if !output.status.success() {
        let stderr = String::from_utf8_lossy(&output.stderr);
        if stderr.contains("bad object") {
            return Err(anyhow!("missing baseline"));
        }
        return Err(anyhow!("git diff single file failed: {}", stderr.trim()));
    }
    let raw = String::from_utf8_lossy(&output.stdout).into_owned();
    if raw.is_empty() {
        match classify(root, rel) {
            Kind::Untracked => {
                if let Ok(text) = synthesize(root, rel) {
                    return Ok(text);
                }
            }
            Kind::Ignored => return Ok(String::new()),
            Kind::Tracked => {}
        }
    }
    Ok(raw)
}

fn classify(root: &Path, rel: &Path) -> Kind {
    match probe(root, rel) {
        Some(k) if k.alive() => k,
        Some(_) => Kind::Ignored,
        None => Kind::Tracked,
    }
}
