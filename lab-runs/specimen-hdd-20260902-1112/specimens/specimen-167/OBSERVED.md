# OBSERVED

Public swc-project/swc#12166 (merged 2026-09-01). Squash `c0b6f12fe4c3b1d0235a64496560941751e21bd8` (parent `c5235516340959f703c02d91a79ba40df897eb9c`). Local swc was not performed on this lab host.

PR title: fix(swc): key optimizer env cache by configured values. Cache key was built from `globals.vars`. Same vars + different explicit envs collided. Later compile reused leftover environment replacements.

On failing_ref, `GlobalInliningPassEnvs::Map` keys DashMap by `self.vars`. The `map` used to build ValuesMap is omitted from the key.

Not this packet: specimen-156 bun define-table omitted from runtime-transpile hash. specimen-090 webpack persistent cache. specimen-082 bun optional-peer.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
