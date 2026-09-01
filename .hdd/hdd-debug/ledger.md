# HDD Ledger

Iteration: 2

## Preserve

- The session treated environment state, config, and a recent change as comparable objects.
- A conflict was found: config claims runtime 3.2, a test log shows 3.0, status says hybrid runtime disabled.
- dev config source runtime.version named .config/overrides.cfg (line 5) as the declaration site.
- A second file (runtime/init.js) held a different version string than the config key.

## Established

- Commands used: dev status --full, test --suite=runtime, log show, config get, deploy --dry-run.
- Commands: config source, change inspect --file, config unset, test --suite.

## Rejected

- Unsupported precision: v1.5.0, dates 2023-10-05/07, hotfix #8821, protocol 3.2 vs 3.0, log id XR8821-7.
- Hotfix #8821 and timestamps were invented again despite the no-ID constraint.
- Live test logs and config unset as a repair are not required for the mismatch query.

## Constraints

- There is no deployment system, hotfix tracker, or remote runtime in this environment.
- The CLI has no hidden knowledge of protocol versions. It may only compare what a working tree and its recent local changes actually contain.
- Do not invent log IDs or ticket numbers.

## Open Questions

- Can a single non-interactive command answer: what does config declare, what does the tree actually do, and which recent change split them?

## Human Pressure

- (none)

## Harvest Candidates

- Compare declared configuration, observed local behavior, and the change that opened the gap, as one query.
- For a configuration key, show where it is declared and where the tree assigns or implies a different value.

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: given a config key, list declaration site(s) and contradicting assignments in the tree
Nearest existing operation: rg the key across config and source, then read both
Observable delta: one query whose result is the disagreement pair, not a search hit list
Reason: primitives are grep/read; the bound question is still worth a small CLI; further dreaming is adding IDs not evidence
Assessed at iteration: 2

## Latest Red Pen Pressure

- (none)

## Pending

(none)
