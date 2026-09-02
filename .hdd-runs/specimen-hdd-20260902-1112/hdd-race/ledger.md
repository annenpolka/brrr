# HDD Ledger

Iteration: 1

## Preserve

- Two parallel specs can read/write one credential store under the working directory
- A sibling file (gitconfig) may already use a per-run suffix while the store path stays static

## Established

- Packet: turbo_tests shared_helpers_spec and file_fetchers/base_spec; CI expected ***private.com got ***github.com; helper --file #{Dir.pwd}/git.store

## Rejected

- env-inspector is not installed; capture/trace/stress-write output is Dreamer-generated
- A recommended SecureRandom suffix is a Dreamer patch, not host evidence

## Constraints

- No dependabot checkout, no rspec, no live parallel workers required
- An owned two-writer shared-path fixture is the world

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- Ask which file the two processes actually shared and why one could read the other's credentials

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: name the shared path two parallel workers collided on, contrasting it with a path that was already unique
Nearest existing operation: read the helper string and ls git.store
Observable delta: one query that treats cross-process credential mix-up as a shared-path identity, not a flake
Reason: CI looks like a wrong expected host; the remainder is which filename was not uniquified
Assessed at iteration: 1

## Latest Red Pen Pressure

- There is no env-inspector and no clone. Continue only on an owned two-writer path fixture.

## Pending

(none)
