# Harvest: hdd-env-empty

- Core Affordance: For one environment key, show inherited value, file assignment (including empty), skip-empty loader result, assign-all loader result, and process env, labeled by layer.
- Affordance Classification: USEFUL_COMPOSITION
- Nearest Existing Operation: printenv + reading the dotenv file + reading loader source
- Observable Delta: one query that distinguishes empty assignment from unset and names the winning layer
- Surviving Abstractions: layer provenance; empty ≠ unset
- Removed Magic: process attach, envprobe, POSIX-empty-means-unset oracle
- Reality Mapping: read a dotenv-style file and two explicit loader policies; print a table
- Research Boundary: does not infer which policy a third-party tool actually used unless that tool is the fixture
- Smallest Useful Artifact: CLI that prints the layer table for KEY given inherited env + file
- Why Existing Tools Are or Are Not Enough: printenv cannot see the file's empty assignment once a loader skipped it; `env | grep` conflates missing and empty
- Source Specimens: specimen-010
- Origin trial: hdd-env-empty
