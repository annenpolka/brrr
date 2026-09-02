repository: gleam-lang/gleam
issue: https://github.com/gleam-lang/gleam/issues/4320
pr: https://github.com/gleam-lang/gleam/pull/4325
failing_ref (parent of first rebased PR commit on main): 3767575d05372e4b823c132afacb28e52fbe3aa1
fixed_ref (rebase-merge last commit, cache files deleted on source removal): b3e1ceb15118c3b4abb0909ef1f2baca6abacd37
merged_at: 2025-03-20T12:46:13Z
pr_author: sbergen
merged_by: lpil
changed_files: compiler-core/src/build/package_loader.rs, compiler-core/src/build/module_loader.rs, compiler-core/src/build/package_loader/tests.rs, compiler-core/src/build/module_loader/tests.rs, compiler-core/src/build.rs, compiler-core/src/codegen.rs, compiler-core/src/erlang.rs, compiler-core/src/io.rs, CHANGELOG.md
pr_title: Fix and clarify cache file handling
scout_note: not 054/154/155. leftover same-name gleam cache after source moved out then restored. unique vs 001-155.
