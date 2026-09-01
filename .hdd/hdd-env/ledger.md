# HDD Ledger

Iteration: 2

## Preserve

- A command failure was attributed to a specific file line that overrode a variable, not to a missing compiler.
- run --capture printed OVERRIDE_SOURCE: .env (line 2).
- DIAGNOSTIC listed LIBRARY_PATH empty, OVERRIDE_SOURCE .env:2, SYSTEM DEFAULT not applied.
- env --filter showed the active override without claiming a live runtime.

## Established

- Commands: devcli env, state scan, state inspect, run --capture, state edit.
- state inspect, run --diagnose, run --env, env --filter.

## Rejected

- Invented checksum 4f6e21a, commit a1b2c3d, and a successful rebuild after edit.
- Successful make build after --env is unverified fiction; grounding must run a real command.

## Constraints

- The CLI cannot edit files to 'fix' the environment. Report only.
- No hidden env parser beyond reading files and the process environment actually present.
- Operate on a real command that fails because of env/files in this tree.

## Open Questions

- Can a one-shot CLI print, for a failed command, which file or parent environment supplied each relevant variable?

## Human Pressure

- (none)

## Harvest Candidates

- For a command invocation, show the provenance of effective environment variables (file, line, inherited, unset).
- For selected variables, show provenance: file:line override, inherited, unset.

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: show where effective environment variables come from (file, inherited, unset) possibly at a command invocation
Nearest existing operation: env, bash -x, direnv status
Observable delta: per-variable source, not only the value
Reason: composition of reading .env/files plus process env; harvestable
Assessed at iteration: 2

## Latest Red Pen Pressure

- (none)

## Pending

(none)
