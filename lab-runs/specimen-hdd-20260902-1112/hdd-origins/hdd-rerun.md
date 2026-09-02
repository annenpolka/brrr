# Harvest: hdd-rerun

- Core Affordance: For a rerun, report whether the test class instance was reused and what attributes leaked.
- Affordance Classification: USEFUL_COMPOSITION
- Nearest Existing Operation: print id(self) in setup/call/teardown
- Observable Delta: one query whose object is leftover instance identity across attempts
- Surviving Abstractions: item-scoped instance vs attempt-scoped instance
- Removed Magic: plugin checkout, recursive test calls, invented object ids
- Reality Mapping: owned attempt loop that reuses one instance
- Research Boundary: does not implement pytest-rerunfailures
- Smallest Useful Artifact: CLI/fixture runner that prints instance identity per attempt
- Why Existing Tools Are or Are Not Enough: rerun output shows pass/fail, not instance reuse
- Source Specimens: specimen-030
- Origin trial: hdd-rerun
