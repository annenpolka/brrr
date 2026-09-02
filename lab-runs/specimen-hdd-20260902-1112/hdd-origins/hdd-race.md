# Harvest: hdd-race

- Core Affordance: Name the shared path two parallel workers collided on, contrasting it with a path that was already unique.
- Affordance Classification: USEFUL_COMPOSITION
- Nearest Existing Operation: read the helper string and ls git.store
- Observable Delta: one query that treats cross-process credential mix-up as a shared-path identity, not a flake
- Surviving Abstractions: uniquified sibling vs static store path
- Removed Magic: env-inspector, live rspec, public PR patch
- Reality Mapping: owned two-writer shared-path fixture
- Research Boundary: does not run dependabot
- Smallest Useful Artifact: CLI that reports which filename was shared and which was unique
- Why Existing Tools Are or Are Not Enough: CI looks like a wrong expected host
- Source Specimens: specimen-053
- Origin trial: hdd-race
