# DESTROYER lockown

Target: `lineages/candidate-lockown/lockown`

Demo two threads, one `OwnedLock`, prints `owner holder` / `waiter blocked`.

## Attacks

- Happy path: labels match the scene (`holder` vs `blocked`, `held true`).
- The names are thread names the CLI assigned, not discovered from `threading.Lock` (stdlib lock has no owner).
- Cannot attach to an existing foreign lock; it always runs its own scene.

## Primitive

The join “who owns vs who waits” is real relative to a timeout error that names neither. The implementation is a labeled scene, not a tracer.

## Decision

**KEEP** as a fixture-scale query. **MUTATE** if we need attach-to-existing-lock. Do not KILL: the object is owner-vs-waiter, which jstack approximates but does not print as one row.
