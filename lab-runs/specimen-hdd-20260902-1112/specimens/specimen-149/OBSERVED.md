# OBSERVED

Public docker/compose#11962 (closed 2024-07-10). compose-spec/compose-go PR 654 squash `6adefd584b8088e0c6817bf54f5715595dd41301` (parent `65600cee45d45771a1faa6ddaf87b23ca4d2400c`). docker/compose PR 11965 bumps compose-go and adds e2e `TestUnsetEnv`. Local compose-go was not performed on this lab host.

Issue body: image `ENV VAR "default"`; compose `environment: - VAR` (no value). Before v2.24.7 the variable was unset from the container. After, leftover image default stayed. `VAR=` (equals, empty) is empty in the container on both sides.

On failing_ref, `Normalize` calls `resolve` for environment and build args with one signature. Listed-without-equals and no user-env match is dropped. Build args are supposed to keep Dockerfile defaults; environment listed-without-equals is supposed to unset.

Not this packet: specimen-010 local-fixture env-empty-vs-unset. specimen-031 pip empty user `proxy =` vs global proxy. specimen-079 helm null vs omitempty.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
