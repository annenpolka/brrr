# Harvest: hdd-nox

- Core Affordance: For a session interrupt, report child exit, parent-sent signal, and session status as three labeled facts.
- Affordance Classification: USEFUL_COMPOSITION
- Nearest Existing Operation: echo $? after the session plus a standalone child run
- Observable Delta: one query that treats the three-status disagreement as the object
- Surviving Abstractions: child-handled interrupt vs session 130
- Removed Magic: live flask, pstree, public patch
- Reality Mapping: owned parent/child interrupt fixture
- Research Boundary: does not reimplement nox
- Smallest Useful Artifact: CLI that prints child_exit, parent_signal, session_status
- Why Existing Tools Are or Are Not Enough: 130 looks like the whole tree failed
- Source Specimens: specimen-040
- Origin trial: hdd-nox
