# HDD Ledger

Iteration: 2

## Preserve

- The operator was trying to understand a repository that used to work and now does not.
- The tool's first output was a project-level mismatch status rather than a file list.
- The CLI stopped inventing sha256 oracles and showed commit-pointer divergence.

## Established

- An installed CLI named repo-tool answered repo-tool, inspect, logs --since=24h, resolve, and inspect validation.
- The session claimed a SYNC_FAILURE (code 409), a local/remote engine checksum mismatch, a dependency_integrity failure, and a SECURE_BINDINGS finding in core/auth.gw.
- inspect manifest --diff, inspect external/llm-api, resolve --dry-run, logs --type=SYNC.

## Rejected

- Unsupported precise values: version v3.7.2, sha256 prefixes aa74/cfd3, timestamps 2024-06-10 08:12:03 and 08:15:22, and 'report generated at 2024-06-10T09:03:17Z' were asserted without an observable source.
- resolve claimed to re-acquire a valid checksum because 'source verified' with no shown verification procedure.
- Still-fabricated commit abbreviations, timestamps, and a remote that is not this machine.

## Constraints

- This environment has no hidden product registry and no checksum oracle. Continue using the same CLI on a real local working tree.
- The CLI cannot automatically repair, re-download, or semantically verify dependencies. Use it anyway.
- Do not invent a security-policy scanner to explain the breakage.

## Open Questions

- After stripping registry/checksum/auto-repair, what single query still answers why the project used to work and now does not?
- Is the object of inquiry a manifest, a working-tree, a test outcome, or something else?

## Human Pressure

- (none)

## Harvest Candidates

- Ask why a project that previously satisfied some implicit last-known-good state no longer does, as one operation.

## Affordance Assessment

Classification: THIN_WRAPPER
Core operation: show that a pinned dependency commit no longer matches the remote/manifest pointer
Nearest existing operation: git submodule status, cargo/npm lockfile diff, git diff on a lockfile
Observable delta: none that requires a new verb
Reason: capability removal left ordinary pin/lockfile comparison; no untested delta remains that would change this class
Assessed at iteration: 2

## Latest Red Pen Pressure

- (none)

## Pending

(none)
