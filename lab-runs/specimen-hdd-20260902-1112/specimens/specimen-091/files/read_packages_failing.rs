// Reduced excerpt of read_packages on failing_ref
// src/cargo/sources/path.rs
// 3d357a9dd6576d7108be731802282176e560d70f
// Walks `path` as given (the git checkout PathBuf). No collapse of `..` here.

fn read_packages(
    path: &Path,
    source_id: SourceId,
    gctx: &GlobalContext,
) -> CargoResult<HashMap<PackageId, Vec<Package>>> {
    let mut all_packages = HashMap::default();
    let mut visited = HashSet::<PathBuf>::default();
    let mut errors = Vec::<anyhow::Error>::new();

    walk(path, &mut |dir| {
        if has_manifest(dir) {
            read_nested_packages(
                dir,
                &mut all_packages,
                source_id,
                gctx,
                &mut visited,
                &mut errors,
            )?;
        }
        Ok(true)
    })?;
