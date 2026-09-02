# HDD Ledger

Iteration: 2

## Preserve

- A child can treat CTRL-C as a clean exit 0 outside the session runner
- The same CTRL-C under the session runner can make the session exit 130
- Parent interrupt and child interrupt can produce different session outcomes
- Parent interrupt and child interrupt can disagree about session outcome

## Established

- Packet: nox -s app Interrupted... / Session interrupted; Nox exits 130; child flask run exits 0 when started outside Nox
- Packet: nox child process termination
- Packet: nox child termination

## Rejected

- pstree PIDs, kill experiments, and CHILD EXIT STATUS 143 were not captured on this host
- A recommended SIGTERM-before-wait patch is not specimen evidence
- pstree PIDs and flask run logs are Dreamer-generated
- Invented child_ignore_sigint scripts are not host evidence until owned

## Constraints

- No flask/nox checkout required
- An owned parent/child interrupt fixture is the world
- No nox/flask
- subprocess Popen fixture only
- Ground with subprocess Popen fixture

## Open Questions

- (none)

## Human Pressure

- No nox. Continue on a subprocess that ignores SIGINT vs one that does not. Did wait look at the child?

## Harvest Candidates

- Ask whether the child exited successfully, which signal the parent sent after interrupt, and why session status disagrees
- Did wait look at the child, or only at the parent's signal?
- Did wait look at the child or only at the parent signal

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: distinguish parent-signal abort from child-observed exit
Nearest existing operation: ps and wait
Observable delta: names who was observed
Reason: exit 130 conflates those cases
Assessed at iteration: 2

## Latest Red Pen Pressure

- (none)

## Pending

(none)
