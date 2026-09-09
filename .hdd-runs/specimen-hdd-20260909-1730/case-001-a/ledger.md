# HDD Ledger

Iteration: 3

## Preserve

- The useful question is what state differs between two reported invocations of the same command on the same supplied files.
- The supplied package.json contains an empty-string dependency key with value ".".
- The supplied transcript reports first-run stdout foo and a second-run lockfile deserialize error mentioning Invalid package requirement '@.'
- The useful question remains what state differs between two reported invocations of the same command on the same supplied files.
- The two supplied files and the two reported invocation outcomes remain reports, not this environment's process output.

## Established

- An unfamiliar developer CLI is already installed in this environment and is not a thin wrapper around a familiar Unix tool.
- The two input files are reported inputs, not a verified local reproduction of Deno 2.6.8.
- The already-installed unfamiliar CLI is not named tool, deno, git, cat, or jq.

## Rejected

- Treating deno as the unfamiliar installed CLI.
- Treating generated deno cache, deno info, or deno lint output as observations of this environment.
- Claiming a lockfile was written by deno cache after moving package.json aside, as a repository fact.
- Claiming deno.lock currently exists or is absent in this workspace as a verified fact.
- Treating invented `tool run`, `tool validate`, `tool resolve`, `tool lock generate`, `tool explain-requirement`, or `tool repair` text as observations of this environment.
- Reprinting the supplied OBSERVED.md transcript as if it were this environment's CLI output.
- Claiming package.json was repaired and that both runs now succeed.
- Treating invented commands list-executables, javix, javix-run, javix-lock, javix workspace status, javix lock regenerate, javix explain-error, or javix lock clear as observations.
- Claiming a lockfile named .javix_lock was created, cleared, or read in this workspace.
- Claiming both runs now print foo after clearing CLI state.

## Constraints

- Command outputs that are not in the supplied transcript are not verified repository facts.
- The already-installed unfamiliar CLI is not named deno, git, cat, or jq.
- The generated deno.lock, resolved JSR version, full working directory, cache, and OS/build details remain unavailable and must not be invented.
- Only command lines actually invoked in this environment, with the exact bytes they printed, count as observations.
- The supplied transcript remains a report. It is not this environment's process output.
- No lockfile, repaired package.json, or generated cache may be asserted as a current workspace fact.
- No further invented CLI names. The already-installed unfamiliar CLI has not been observed.
- The supplied transcript must not be reprinted as command output.

## Open Questions

- What does the already-installed unfamiliar CLI print when pointed at these two reported invocations and the two supplied files?
- What exact argv does the already-installed unfamiliar CLI accept on files/package.json and files/a.js, and what exact bytes does it print on a failure?

## Human Pressure

- (none)

## Harvest Candidates

- (none)

## Affordance Assessment

Classification: THIN_WRAPPER
Core operation: run the same command twice and notice that the second run differs
Nearest existing operation: invoke the command twice and inspect the working directory
Observable delta: none demonstrated: the Dreamer restated the supplied transcript under three invented CLI names
Reason: Turns 1-3 produced deno, tool, and javix wrappers with fabricated outputs. No real argv or bytes from this environment. Reality-stripped, only the ordinary two-invocation comparison remains, and it was not shown as a new first-class operation.
Assessed at iteration: 3

## Latest Red Pen Pressure

- Stop inventing CLI names. If the already-installed unfamiliar CLI cannot be invoked with a real argv on the two supplied files, do not fabricate another wrapper.

## Pending

(none)
