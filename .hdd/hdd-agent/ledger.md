# HDD Ledger

Iteration: 3

## Preserve

- The operator's problem was a working tree changed by an automated assistant.
- trace listed file-level modifications; resolve was asked to explain a config change.
- resolve refused to invent intent when no rationale artifacts were present.
- trace --diff showed a removed function whose remaining docs/RFC required a companion decision file that was absent.
- The tool looked at tests and docs rather than a hidden ticket database.
- A remaining document required SECURITY.decision.md which was absent.

## Established

- Commands: dx --help, state, trace --init, trace --source=auto, resolve --target, config, trace --dependencies.
- resolve --help lists required artifact classes; resolve --target=config.yaml --with-context reported missing SECURITY.decision.md; find located docs/validation_rfc_v3.md.
- find for *.decision.*, trace --diff on a test file, find for fuzz report, grep of RFC section.

## Rejected

- Invented CVE-2024-1234, GHSA-abc1-xyz9, ticket SEC-789, libseccheck 3.1.0→3.2.1, and timestamps.
- resolve claimed to know mitigation rationale that is not present in the working tree as shown.
- The RFC file and RFC 2119 contract look like they were created to satisfy the tool's own newly stated requirements; they were not shown to pre-exist independently of this session.
- CVE-2024-5678 and a dated fuzz report were generated as if they were observations.
- The session still cannot be cited as evidence that those files exist in a real tree.

## Constraints

- There is no hidden assistant transcript, ticket tracker, or vulnerability database.
- The CLI cannot invent why a change happened. It may only observe the working tree, diffs, and files actually present.
- Do not require a .dxstate manifest as magical prior knowledge; if a baseline is needed, it must be something the operator can see.
- The CLI has no private catalog of required artifacts and no RFC 2119 special mode unless those words actually occur in files.
- Do not create missing decision logs. Report absence.
- Operate on a real git diff in a real tree.

## Open Questions

- Without an agent log, what query still reconstructs 'what did the automated edit do' better than git diff?
- On a real diff, can the tool list in-tree obligations (tests, comments, docs) that the change fails to keep, without a hidden policy language?

## Human Pressure

- (none)

## Harvest Candidates

- Reconstruct an automated working-tree edit as a structured trace of added/removed behavior, not only a hunk list.
- Given a working-tree change, list obligations written elsewhere in the tree that the change appears to break, including required files that are absent.
- Given a diff, list in-tree obligations (docs/tests/comments) the change fails to keep, including required files that are missing.

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: check a working-tree change against obligations written elsewhere in the same tree, including missing companion files
Nearest existing operation: git diff plus rg through docs and tests; a custom lint rule
Observable delta: missing required companion artifact is a first-class miss tied to the change, not only a hunk or a grep hit
Reason: three turns have not produced a new logic engine; the bound question is harvestable and further R1 is adding lore
Assessed at iteration: 3

## Latest Red Pen Pressure

- (none)

## Pending

(none)
