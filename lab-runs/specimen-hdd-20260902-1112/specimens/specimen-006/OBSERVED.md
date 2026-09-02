# OBSERVED

Public astral-sh/uv#20774.

- Action: `cache-workspace-crates` remains wanted.
- Symptom: after lockfile updates, fallback cache restores retain older fingerprints for workspace members alongside new artifacts.
- External dependencies should remain cached.
- Growth is observed on Linux CI across successive lockfile updates.
