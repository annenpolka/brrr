# Harvest: hdd-gradlerace

- Core Affordance: Name the shared cache, the concurrent compilers, and that the crashing project need not be the writer.
- Affordance Classification: USEFUL_COMPOSITION
- Nearest Existing Operation: read the stack and retry the build
- Observable Delta: one query that treats misattributed concurrent cache corruption as the object
- Surviving Abstractions: shared mutable cache; misattribution
- Removed Magic: Gradle checkout, ConcurrentHashMap recipe as evidence
- Reality Mapping: owned concurrent map fixture with colliding keys
- Research Boundary: does not rebuild Gradle
- Smallest Useful Artifact: CLI/fixture that reports which thread corrupted which map and which label was blamed
- Why Existing Tools Are or Are Not Enough: retry success hides which map and which threads
- Source Specimens: specimen-042
- Origin trial: hdd-gradlerace
