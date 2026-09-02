# OBSERVED

Public astral-sh/ruff#12264 (closed 2024-08-07). PR 12727 squash `a631d600acf3fa26c744ff00909f9891365e7ed4` (parent `90e5bc2bd95e15086a3af81589cc2a1af298b6b2`). Also fixes #12721. Local ruff was not performed on this lab host.

Issue body: after commenting nested ignore, cached check names only t3.py; `--no-cache` names t2.py and t3.py.

On failing_ref, Resolver::add inserts `{path}/{*filepath}` only. Directory query misses. Nested pyproject.toml is not the cache identity for files whose route missed.

Inserting the directory path itself is **not** on the failing revision. It is added by PR 12727.

Not this packet: specimen-001/002/003 (pytest assertion/collection/fixture). specimen-107 (pytest leftover cache-dir without .gitignore). ruff#1589 / PR 1595 (flake8-pytest-style settings omitted from hash; different leftover: config hash, not nested directory route).

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
