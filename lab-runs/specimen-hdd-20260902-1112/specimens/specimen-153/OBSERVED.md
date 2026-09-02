# OBSERVED

Public hexpm/hex#821 (closed 2021-01-05). PR 843 squash `90aa44fa8a1e59f2ae65f490edb984e4d6c853d1` (parent `6639c0ad8921fdaf0468d86cc51525c8237e357a`). Local hex was not performed on this lab host.

Issue body: mix hex.update / deps.get CaseClauseError `no case clause matching: {:ok, <<...>>}` at Hex.SCM.fetch after a republished package. Workaround: delete the cached tarball.

On failing_ref, fetch pins `{:ok, ^outer_checksum}` as cached and `{:error, _}` as network fetch. A leftover tarball with a different checksum has no clause.

Not this packet: specimen-074 rubygems frozen lockfile platform identity. specimen-021 poetry leftover.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
