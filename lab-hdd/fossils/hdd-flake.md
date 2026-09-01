# Fossil: hdd-flake

- At: 2026-09-01 22:23:21 JST
- Decision: KILL
- Classification: THIN_WRAPPER
- Core operation: rerun a failing test and print a last-failure snapshot
- Nearest existing operation: pytest --lf / rerunfailures, a CI flake chart
- Observable delta: none demonstrated on a real flaky test
- Reason: invented percentages and contention; no new question
- Iteration: 1
- Do not send back to R1 with "make this more novel".
