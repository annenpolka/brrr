# OBSERVED

Public stylelint/stylelint#2908 (closed 2022-09-27). PR 6356 squash `5be33b779b93761d86cb871dfd70f34686b5f6c5` (parent `3df16ba23b1cdb7b3257fa4b4979b8d0b3ffbb66`). Local stylelint was not performed on this lab host.

Issue body: a config change is not detected when using `--cache`.

On failing_ref, standalone hashes the CLI `config` argument (often undefined when a file config is used) and filters paths before `lintSource`. `calcHashOfConfig` on the resolved config is **not** on the failing revision. It is added by PR 6356.

Not this packet: specimen-132 eslint leftover cache plugin name@version omitted from toJSON. specimen-114 ruff leftover cache vs nested pyproject. specimen-107 pytest leftover cache-dir supporting files.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
