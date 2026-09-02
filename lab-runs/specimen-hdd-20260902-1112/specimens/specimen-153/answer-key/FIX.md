KNOWN FIX (sealed): hexpm/hex PR 843 squash 90aa44fa8a1e59f2ae65f490edb984e4d6c853d1.

failing_ref is parent 6639c0ad8921fdaf0468d86cc51525c8237e357a.

Hex.SCM.fetch treated {:ok, ^outer_checksum} as cached and {:error, _} as fetch. A leftover tarball with a different checksum had no clause (CaseClauseError). Cache path is package-version, not checksum.

PR repair: {:ok, other_outer_checksum} warns and do_fetch.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
