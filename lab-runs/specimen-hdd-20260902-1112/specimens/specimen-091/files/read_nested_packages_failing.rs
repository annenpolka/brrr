// Reduced excerpt of read_nested_packages on failing_ref
// src/cargo/sources/path.rs
// visited is HashSet<PathBuf> (lexical). Nested path= edges are collapsed.

fn read_nested_packages(
    path: &Path,
    all_packages: &mut HashMap<PackageId, Vec<Package>>,
    source_id: SourceId,
    gctx: &GlobalContext,
    visited: &mut HashSet<PathBuf>,
    errors: &mut Vec<anyhow::Error>,
) -> CargoResult<()> {
    if !visited.insert(path.to_path_buf()) {
        return Ok(());
    }

    let manifest_path = find_project_manifest_exact(path, "Cargo.toml")?;
    // ...
    let pkg = Package::new(manifest, &manifest_path);
    let pkg_id = pkg.package_id();
    all_packages.entry(pkg_id).or_default().push(pkg);

    // We normalize the path here ensure that we don't infinitely walk around
    // looking for crates. By normalizing we ensure that we visit this crate at
    // most once.
    if !source_id.is_registry() {
        for p in nested.iter() {
            let path = paths::normalize_path(&path.join(p));
            let result =
                read_nested_packages(&path, all_packages, source_id, gctx, visited, errors);
