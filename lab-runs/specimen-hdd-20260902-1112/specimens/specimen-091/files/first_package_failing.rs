// Reduced excerpt of first_package on failing_ref
// src/cargo/sources/path.rs
// Warns when one PackageId mapped to more than one Package.

fn first_package<'p>(
    pkg_id: PackageId,
    pkgs: &'p Vec<Package>,
    warned_duplicate: &mut HashSet<PackageId>,
    gctx: &GlobalContext,
) -> &'p Package {
    if pkgs.len() != 1 && warned_duplicate.insert(pkg_id) {
        let ignored = pkgs[1..]
            .iter()
            .filter(|pkg| pkg.publish().is_none())
            .collect::<Vec<_>>();
        if !ignored.is_empty() {
            let _ = writeln!(&mut msg, "skipping duplicate package{plural} `{pkg_id}`:");
            for ignored in ignored {
                let _ = writeln!(&mut msg, "  {manifest_path}");
            }
            let _ = writeln!(&mut msg, "in favor of {manifest_path}");
            let _ = gctx.shell().warn(msg);
        }
    }
    &pkgs[0]
}
