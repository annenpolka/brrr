# OBSERVED

Public go-task/task#1795 (closed 2025-09-11). PR 1808 squash `48039be12cdfc6b6871dbe9f1d6977027d660889` (parent `1e2121a99f6414e3bf4565e5736a116bef10be91`). Local task was not performed on this lab host.

Issue: wildcard parameter is not on the fingerprint cache key. Two MATCH instantiations share leftover checksum identity.

On failing_ref, compiledTask copies origTask.Task as the name. MATCH is a var, not the checksum key. FullName is **not** on the failing revision. It is added by PR 1808 (`fullName` replaces `*` with MATCH; `Name()` prefers FullName).

Not this packet: specimen-076/088/104 (gradle compiler fingerprints). pants leftover fingerprint (job-0464 hunt: no leftover-identity merged pair). cargo leftover (091/099/101).

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
