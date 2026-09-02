CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

# TASK

Linux CI Rust caches for a workspace grow across lockfile updates. Fallback restores keep older fingerprints for workspace members next to newly compiled artifacts. Disk usage climbs; it is unclear which cache entries are still live for the current lockfile.

The developer wants to distinguish current workspace outputs from superseded fingerprints without deleting the whole cache.

# OBSERVED

Public astral-sh/uv#20774.

- Action: `cache-workspace-crates` remains wanted.
- Symptom: after lockfile updates, fallback cache restores retain older fingerprints for workspace members alongside new artifacts.
- External dependencies should remain cached.
- Growth is observed on Linux CI across successive lockfile updates.

# COMMANDS

CI restore of Rust cache after a lockfile bump; compare fingerprint directories for workspace members before/after. Not executed on the lab host.

workspace members + target/ + CI rust cache

RELEVANT MATERIAL

KNOWN FACTS
Only the observations above are established. Do not assume a root cause.

UNKNOWN
What relation, provenance, or question would make this failure smaller to investigate?

OPERATOR REQUEST
An unfamiliar developer CLI is already installed in this environment.
It is not a thin wrapper around a familiar Unix tool.
Use it on the problem below. Operate what is present rather than proposing a product.
Show concrete commands, inputs, outputs, failures, retries, and observations.
Do not invent repository facts that contradict the supplied material.
