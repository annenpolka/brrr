# OBSERVED

Public gleam-lang/gleam#4320 (closed 2025-03-20). PR 4325 rebase-merge last commit `b3e1ceb15118c3b4abb0909ef1f2baca6abacd37` (first PR commit on main `588caed189988e96ff51f5e209c4d35151a396cd`, parent `3767575d05372e4b823c132afacb28e52fbe3aa1`). Local gleam was not performed on this lab host.

Issue body: temporarily removed file does not always get recompiled. Cache files of missing sources are not deleted. mtime is not enough when restored content matches the leftover fingerprint. Follow-on of #3873 (mark removed modules stale without deleting cache).

On failing_ref, `PackageLoader::run` adds missing cache modules to `stale_modules`. `ModuleLoader::load` returns `Input::Cached` when fingerprint matches. Restored same-name `a.gleam` JOINs with leftover cache.

Not this packet: specimen-054 cpython. specimen-154 mix same-length rewrite omitted digest. specimen-155 clangd leftover BMI.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
