# Fossil: hdd-wait

- At: 2026-09-01 22:31:50 JST
- Decision: KILL
- Classification: THIN_WRAPPER
- Core operation: report a process's wait channel and blocking file descriptor
- Nearest existing operation: ps -o wchan, lsof -p, /proc/PID/fd
- Observable delta: bundled wording; no new query object after removing invented session lore
- Reason: capability removal left ordinary process inspection; no untested delta that would change the class
- Iteration: 2
- Do not send back to R1 with "make this more novel".
