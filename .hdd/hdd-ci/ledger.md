# HDD Ledger

Iteration: 2

## Preserve

- The problem was a job that passed locally and failed remotely.
- The CLI's verbs were capture, diff, and replay rather than 'debug the test'.
- Two local working directories were the objects of capture.
- diff reported a modified env var and a file hash mismatch as separate sections.
- Replay applied env vars without starting extra services.

## Established

- Commands: ci-debug --version, --help, capture --label, capture --from-tar, diff, replay --command.
- capture --label --cwd --output plain, diff, replay --command, replay --target-dir.

## Rejected

- Invented snapshot IDs, API_KEY values, security-daemon PID 204, and a successful replay after a fictional config modify.
- Invented file counts, core dump path, and a passing npm test after swapping API_KEY.

## Constraints

- There is no CI artifact tarball, vault, or remote daemon in this environment.
- Replay cannot magically reconstruct Postgres+TLS. It may only export and apply environment variables and files that were actually captured.
- Operate on two real local directories or processes.

## Open Questions

- After removing tar-import and fictional replay success, is capture+diff of two local environments still a distinct verb from env|sort and diff?

## Human Pressure

- (none)

## Harvest Candidates

- Capture two execution environments and diff them as first-class objects; optionally re-run a command under one capture's exported env.
- Snapshot two directories' environment files and selected metadata, then diff them as first-class captures.

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: capture two execution environments (files+env) and diff them; optionally run a command with one capture's env
Nearest existing operation: diff -ru two trees; env; direnv; docker
Observable delta: environment is the compared object (labeled captures) rather than ad hoc dumps
Reason: primitives exist; the bound capture/diff/replay CLI is enough to ground; further dreaming is adding CI lore
Assessed at iteration: 2

## Latest Red Pen Pressure

- (none)

## Pending

(none)
