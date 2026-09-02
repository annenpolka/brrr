# OBSERVED

Public crystal-lang/crystal#16810. PR 16958 squash `ac82b6ba7dcdc83f72199e8827f68417d61b88c4` (parent `c9e867a6703979d8e09abd2a3c1d9a7d55ae945d`). Local crystal was not performed on this lab host.

PR title: Fix interpreter multidispatch cache collision. Cache key was `(obj_type, call_signature)`; second site reused the first site's dispatch chain after a new type appeared.

On failing_ref, `Context::MultidispatchKey` has two fields. `multidispatch.cr` returns `cached_def` on that key. Newly resolved types fall through the leftover chain.

Not this packet: specimen-054 cpython. specimen-154 mix same-length rewrite omitted digest. specimen-159 gleam leftover cache after move+restore.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
