# OBSERVED

Public moonrepo/moon#481 (closed 2022-11-30). PR 482 squash `2959d6f0bcc9dbe12fb3f35e54186d245b44586a` (parent `5468dd6fb24ee98cbf6e4c05e3421e6a17e73199`). Local moon was not performed on this lab host.

Issue body: `.env` listed as an input does not break cache; leftover cached output is reused after the file changes.

On failing_ref, `expand_env` does not add `env_file` to `inputs`. `Git::get_file_hashes` skips `is_file_ignored`. `allow_ignored` is **not** on the failing revision. It is added by PR 482.

Not this packet: specimen-119 pixi leftover task cache filename omitting args. specimen-115 go-task leftover wildcard MATCH. turbo leftover env (no merged leftover-identity pair this run). specimen-133 stylelint leftover cache hashing empty CLI config.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
