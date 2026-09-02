
impl Commit {
    pub(crate) fn from_repository(path: &Path) -> Result<Self, GitInfoError> {
        let git_dir = path
            .ancestors()
            .map(|ancestor| ancestor.join(".git"))
            .find(|git_dir| git_dir.exists())
            .ok_or_else(|| GitInfoError::MissingGitDir(path.to_path_buf()))?;

        let git_head_path =
            git_head(&git_dir).ok_or_else(|| GitInfoError::MissingHead(git_dir.clone()))?;
        let git_head_contents = fs_err::read_to_string(git_head_path)?;

        let mut git_ref_parts = git_head_contents.split_whitespace();
        let commit_or_ref = git_ref_parts
            .next()
            .ok_or_else(|| GitInfoError::InvalidRef(git_dir.clone(), git_head_contents.clone()))?;
        let commit = if let Some(git_ref) = git_ref_parts.next() {
            let git_ref_path = git_dir.join(git_ref);
            let commit = fs_err::read_to_string(git_ref_path)?;
            commit.trim().to_string()
        } else {
            commit_or_ref.to_string()
        };
        // ... length/hex checks ...
        Ok(Self(commit))
    }
}

fn git_head(git_dir: &Path) -> Option<PathBuf> {
    let git_head_path = git_dir.join("HEAD");
    if git_head_path.exists() {
        return Some(git_head_path);
    }
    if !git_dir.is_file() {
        return None;
    }
    // worktree .git file: "gitdir: /path/to/.git/worktrees/pr2"
    let contents = fs_err::read_to_string(git_dir).ok()?;
    let (label, worktree_path) = contents.split_once(':')?;
    if label != "gitdir" {
        return None;
    }
    Some(PathBuf::from(worktree_path.trim()))
}
