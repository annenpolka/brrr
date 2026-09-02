KNOWN FIX (sealed): rust-lang/cargo PR 17204 squash merge 5bf4c0cf6aed9e3f3c7b020edca95d8ef541451b.

failing_ref is merge first parent 3d357a9dd6576d7108be731802282176e560d70f.

GitSource handed RecursivePathSource the raw checkout PathBuf under CARGO_HOME. A home path containing `..` stayed in that string for the filesystem walk. Nested path= edges from the same git manifests were joined and collapsed by cargo_util::paths::normalize_path, so visited (HashSet of PathBuf) and the per-PackageId Vec recorded two Packages for one git identity. first_package then emitted skipping-duplicate.

Repair in read_packages: bind the walk root through paths::normalize_path before walk/visited, so the walk and the nested path= recursion share one PathBuf. Added tests/testsuite/git.rs no_duplicate_package_warning_with_dotdot_cargo_home (git dep with a path member; CARGO_HOME = home/../cargo-home; stderr has no duplicate warning). Case C (two real directories, same name) is unchanged.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
