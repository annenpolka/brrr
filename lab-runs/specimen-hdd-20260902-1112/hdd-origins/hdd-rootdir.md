# Harvest: hdd-rootdir

- Core Affordance: For each collected item, show which conftest/config objects actually apply.
- Affordance Classification: USEFUL_COMPOSITION
- Nearest Existing Operation: pytest --collect-only plus reading conftest files
- Observable Delta: one query that shows a visibility hole when collection path is not a descendant of rootdir
- Surviving Abstractions: rootdir vs collection path; bind vs load
- Removed Magic: --trace-config dumps, public issue citations
- Reality Mapping: owned two-directory fixture specimen-055
- Research Boundary: does not reimplement pytest collection
- Smallest Useful Artifact: CLI that, given rootdir and item path, says whether the rootdir conftest binds
- Why Existing Tools Are or Are Not Enough: collect-only lists items, not which conftest they bound
- Source Specimens: specimen-002, specimen-055
- Origin trial: hdd-rootdir
