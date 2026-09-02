# HDD Ledger

Iteration: 2

## Preserve

- A find/cache can key the wrong interpreter path
- PYTHONEXECUTABLE can change interpreter metadata while a path-only cache key still hits
- Two python paths can collapse to one cache row if the key ignores env

## Established

- Packet: uv python find / PYTHONEXECUTABLE
- Packet: first find with PYTHONEXECUTABLE=.venv returns .venv; second find with env removed still prints .venv
- Packet: PYTHONEXECUTABLE vs uv python find

## Rejected

- Invented dual venv commands are not host-executed
- Invented msgpack cache dumps and uv python find transcripts are not host evidence
- Simulated hashlib of interpreter_cache_entry.rs is not host evidence

## Constraints

- No uv
- No uv. Owned key-component list: path vs env. Transfer onto freshmiss/lockident
- Owned two-path fixture

## Open Questions

- (none)

## Human Pressure

- No uv. Continue on two path strings and one cache key. Show requested vs cached interpreter.

## Harvest Candidates

- Which interpreter path the cache used
- Which env component was omitted from the interpreter cache key
- requested path vs cached path

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: name requested interpreter path vs cached path
Nearest existing operation: ls two venvs
Observable delta: which path the cache hit used
Reason: two pythons one row
Assessed at iteration: 2

## Latest Red Pen Pressure

- (none)

## Pending

(none)
