# HDD Ledger

Iteration: 2

## Preserve

- The mismatch was not 'wrong YAML' but an undeclared environment variable overriding a declared policy.
- diff expected:config.yaml actual:runtime named conflict sources.
- config explain security.require_jwt named config.yaml line 42 vs OVERRIDE_SECURITY from .env and an effective value.
- layers listed missing expected files as missing, not as live metrics.

## Established

- Commands: devcli, config audit, runtime query, diff expected:config.yaml actual:runtime, config reconcile --fix=document.
- diff expected:config.yaml actual:manifest, config layers, config explain.

## Rejected

- Live metrics 12%/88% over 15m, auth-service@v1.3, auto-created markdown files, and a reload that made enforcement 100% are not observations.
- Implicit default scopes of [public] from a missing file is still a guessed effective value, not an observation unless the tool's own documented default is in-tree.

## Constraints

- There is no live application, metric stream, or reload RPC.
- The CLI cannot write documentation to 'fix' drift. It may only report it.
- No hidden feature-flag registry. Sources of override must be files or process environment actually present.

## Open Questions

- Can the tool name undeclared overrides (env vars, defaults) that explain config-vs-actual without talking to a running service?

## Human Pressure

- (none)

## Harvest Candidates

- Diff declared configuration against actual effective configuration, listing undeclared override sources.
- Explain a config key as declaration, override sources, and effective value from files+env only.

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: explain a config key's declaration, override sources, and effective value from files and process environment
Nearest existing operation: reading yaml plus env plus rg
Observable delta: the explain record is the object, not a pile of hits
Reason: converges with hdd-debug/hdd-env; ground via stated/envfrom rather than a third identical CLI
Assessed at iteration: 2

## Latest Red Pen Pressure

- (none)

## Pending

(none)
