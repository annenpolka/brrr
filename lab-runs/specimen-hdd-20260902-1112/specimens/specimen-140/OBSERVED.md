# OBSERVED

Public microsoft/rushstack#4400 (closed 2024-10-17). PR 4476 merge `3530cb21a03927ec8b06072ee89a91466dc6beb3` (parent `300fcd107dea176ef503ffa073776bff47ee17a1`). Local rush was not performed on this lab host.

Issue body: `dependsOnEnvVars`, `dependsOnAdditionalFiles`, and CLI parameters that affect some phases do not affect cache keys of dependent operations. Cache key computed from project dependencies, not operation dependencies.

On failing_ref, `_getCacheIdAsync` walks `dependencyProjects`. Runtime operation graph is **not** in that walk. PR 4476 moves hash computation onto the operation graph.

Not this packet: specimen-136 pants leftover process cache vs git hash. specimen-134 moon leftover .env inputs. nx leftover .env (no merged leftover-identity pair this run).

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
