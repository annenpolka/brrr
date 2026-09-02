KNOWN FIX (sealed): rust-lang/cargo#14761. Bors-approved head b5acf4ce4763ff90fd8bd92494490184a37fa24e verified. failing_ref is merge first parent 40d6078bafd61645f13086f697104c360b25b7d3; fixed_ref is bors merge 0310497822a7a673a330a5dd068b7aaa579a265e.

hash_exe hashed only resolved path + mtime. Fedora clamps mtimes, so /usr/bin/rustc at 2024-10-17 00:00:00 matched across Fedora 39–42 rustc 1.82 packages whose verbose_version Fedora suffixes and LLVM differed. Cache::load then reused .rustc_info.json (including cached rustc -vV) and cargo proceeded against rlibs from the other compiler (E0514). verbose_version / commit-hash / distro suffix never entered rustc_fingerprint.

Repair in hash_exe: one metadata() call, then hash len, FileTime::from_creation_time, and FileTime::from_last_modification_time (mtime still hashed; creation is optional per filesystem). The rustup arm on the same revision still hashes only mtime of $RUSTUP_HOME/toolchains/$RUSTUP_TOOLCHAIN/bin/rustc (not hash_exe). Wrappers go through hash_exe.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
