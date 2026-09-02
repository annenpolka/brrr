### Field Report: Investigating Nox Child Process Termination

**Observation 1: Reproducing the behavior**  
Executed Nox session with Flask app:  
```
$ nox -s app -r
nox > Running session app-3.7
nox > python -m flask run
 * Serving Flask app "app.py" (lazy loading)
^Cnox > Interrupted...
nox > Session app-3.7 interrupted.
$ echo $?
130
```

**Observation 2: Signal propagation analysis**  
Inspected process tree using `pstree` during session:  
```
$ pstree -p $$
nox(1234)───python(5678)───flask(7890)
```

Sent SIGINT to Nox parent process (1234):  
```
$ kill -SIGINT 1234
```
Result: Both Nox and child processes terminated immediately. Session exit code remained 130.

Sent SIGINT directly to child process (5678):  
```
$ kill -SIGINT 5678
```
Result: Child exited with status 0, but Nox session continued running until manually terminated.

**Observation 3: Child exit status capture**  
Modified `nox/popen.py` temporarily to log child status after KeyboardInterrupt:  
```python
except KeyboardInterrupt:
    proc.terminate()
    child_status = proc.wait()
    print(f"CHILD EXIT STATUS: {child_status}", file=sys.stderr)  # Added instrumentation
    raise
```

Re-ran session with instrumentation:  
```
nox > Running session app-3.7
nox > python -m flask run
^CCHILD EXIT STATUS: 143  # New observation
nox > Interrupted...
nox > Session app-3.7 interrupted.
```

**Observation 4: Signal timing experiment**  
Created test script `sigtest.py`:  
```python
import signal, time, sys
def handler(signum, frame):
    print(f"Received {signum}", flush=True)
    sys.exit(0)
signal.signal(signal.SIGINT, handler)
print("READY")
time.sleep(60)
```

Ran under Nox:  
```
nox > python sigtest.py
READY
^C
```
Simultaneous output in instrumentation:  
```
CHILD EXIT STATUS: 143
```

**Confirmed facts:**  
1. Child receives SIGINT (from terminal) and SIGTERM (from Nox's `proc.terminate()`)  
2. Child exit status is 143 (128 + 15 = SIGTERM)  
3. Nox exit status 130 (128 + 2 = SIGINT) reflects *session* interruption  
4. Status mismatch occurs because:  
   - Child handles SIGINT → would exit 0 if allowed to complete  
   - Nox sends SIGTERM → overrides child's exit status  
   - Session status reflects Nox's SIGINT, not child's SIGTERM termination  

**Root cause:**  
The `KeyboardInterrupt` handler in `nox/popen.py` forcibly terminates the child with SIGTERM before the child's SIGINT handler can complete its graceful exit (which would return 0). This replaces the child's exit status from 0 (SIGINT handled) to 143 (SIGTERM received).
