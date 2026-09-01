# HDD Ledger

Iteration: 1

## Preserve

- The Dreamer actually placed the CLI in pipelines with jq, diff, tee, grep.

## Established

- analyze --format json, transform --rule, generate --template, verify --rules, stdin --input -.

## Rejected

- Cyclomatic/cognitive scores, lodash missing warning, accessibility contrast failure without a real file.

## Constraints

- (none)

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- (none)

## Affordance Assessment

Classification: THIN_WRAPPER
Core operation: analyze, transform, generate, and verify source, optionally via pipes
Nearest existing operation: eslint, jscodeshift, a compiler, jq
Observable delta: none beyond being pipe-friendly
Reason: the seed was pipeline use; the artifact is a conventional codegen/lint suite
Assessed at iteration: 1

## Latest Red Pen Pressure

- (none)

## Pending

(none)
