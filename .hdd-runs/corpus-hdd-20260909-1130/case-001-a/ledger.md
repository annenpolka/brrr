# HDD Ledger

Iteration: 3

## Preserve

- The useful question is what state differs between two reported invocations of the same command on the same supplied files.
- The supplied package.json contains an empty-string dependency key with value ".".
- The supplied transcript reports first-run stdout foo and a second-run lockfile deserialize error mentioning Invalid package requirement '@.'
- Comparing what changes between two identical invocations remains the live question.
- The surviving question is which working-directory files appear after the first of two identical command invocations, and whether the second invocation then fails.

## Established

- An unfamiliar developer CLI is already installed in this environment and is not a thin wrapper around a familiar Unix tool.
- The two input files are reported inputs, not a verified local reproduction of Deno 2.6.8.
- Typing a command named cli with run/info flags did not demonstrate a process that actually printed those bytes in this environment.
- Matching the supplied transcript, including the placeholder [reporter-local-path-omitted], is not an observation of this environment.

## Rejected

- Treating deno as the unfamiliar installed CLI.
- Treating generated deno eval or deno info output as observations of this environment.
- Claiming the lockfile is currently absent, or that a JSR cache path was inspected, as a repository fact.
- Invented CLI usage text, invented lockfile.json bytes, invented jsr:@std/testing/bdd version 0.1.0, and invented Lockfile validation failed output.
- Hand-writing a lockfile with --lock=lockfile.json and then treating cat of that file as investigation of the supplied world.
- Using eval plus Deno.readFileSync as if that were the unfamiliar CLI.
- unfamiliar.lock at 128 bytes as an observed file in this environment.
- Pasting the supplied OBSERVED.md error block as this environment's stderr.

## Constraints

- Command outputs that are not in the supplied transcript are not verified repository facts.
- The already-installed unfamiliar CLI is not named deno, git, cat, or jq.
- The generated deno.lock, resolved JSR version, full working directory, cache, and OS/build details remain unavailable and must not be invented.
- Stdout and stderr shown for the unfamiliar CLI must be the exact bytes a process in this environment printed on that invocation.
- Matching the supplied transcript does not make generated text an observation of this environment.
- Do not create, write, or pass --lock files. If a file appears after an invocation, only list its name and size; do not open or reconstruct it as a theory of the report.
- No further Dreamer turns on this trial unless a new in-world fact can be produced by a real process. Host grounding of the twice-run directory snapshot is allowed.

## Open Questions

- What does the already-installed unfamiliar CLI print when pointed at these two reported invocations and the two supplied files?
- After one real invocation of the already-installed unfamiliar CLI on the supplied files, which working-directory entries exist that did not exist before that invocation?

## Human Pressure

- (none)

## Harvest Candidates

- A possible operation is: run the same command twice and report working-directory files that appeared between the two invocations, without explaining why they appeared.
- runpair: run the same command twice in one directory and report added/removed/changed regular files after each invocation, without opening those files.

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: run the same command twice and report working-directory files that appeared or changed between the two invocations
Nearest existing operation: run CMD; ls; run CMD again, or an inotify watcher plus a second run
Observable delta: one contract binds first-run sidecar files to second-run exit status; ordinary ls after the fact does not record that the sidecar appeared between two identical commands
Reason: the fictional CLI name is a thin wrapper; the twice-run directory delta is a composition of existing run and stat primitives with a practical binding
Assessed at iteration: 3

## Latest Red Pen Pressure

- This environment will not treat transcript-identical stderr as a new observation.
- Do not invent lockfile names or sizes.
- Further use of a fictional unfamiliar-cli is unnecessary; the twice-run directory snapshot can be performed with ordinary process execution.

## Pending

(none)
