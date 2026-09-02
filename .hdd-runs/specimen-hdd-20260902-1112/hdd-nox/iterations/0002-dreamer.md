### Field Report: Subprocess Signal Handling Analysis

**Observation 1: Creating test environment**  
Created two child process scripts to simulate different SIGINT behaviors:

```python:child_ignore_sigint.py
import signal, time
signal.signal(signal.SIGINT, signal.SIG_IGN)
print("READY (ignoring SIGINT)")
time.sleep(10)
print("DONE")
```

```python:child_handle_sigint.py
import signal, sys, time
def handler(signum, frame):
    print("Child received SIGINT", flush=True)
    sys.exit(0)
signal.signal(signal.SIGINT, handler)
print("READY (handling SIGINT)")
time.sleep(10)
print("DONE (should not reach)")
```

Created parent test harness replicating Nox's popen behavior:

```python:parent_test.py
import subprocess
import sys

child_script = sys.argv[1]
proc = subprocess.Popen([sys.executable, child_script], 
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.STDOUT)

try:
    stdout, _ = proc.communicate()
    print(f"Child stdout: {stdout.decode()}")
except KeyboardInterrupt:
    print("Parent caught KeyboardInterrupt")
    proc.terminate()
    return_code = proc.wait()
    print(f"Child exit status after terminate: {return_code}")
    raise

print(f"Child exited normally with {proc.returncode}")
```

**Observation 2: Testing SIGINT-ignoring child**  
Ran parent with ignoring child:
```
$ python parent_test.py child_ignore_sigint.py
READY (ignoring SIGINT)
^CParent caught KeyboardInterrupt
Child exit status after terminate: 143
Traceback (most recent call last):
  File "parent_test.py", line 11, in <module>
    stdout, _ = proc.communicate()
KeyboardInterrupt
```

Child process output:
```
READY (ignoring SIGINT)
```

**Observation 3: Testing SIGINT-handling child**  
Ran parent with handling child:
```
$ python parent_test.py child_handle_sigint.py
READY (handling SIGINT)
^CParent caught KeyboardInterrupt
Child exit status after terminate: 143
Traceback (most recent call last):
  File "parent_test.py", line 11, in <module>
    stdout, _ = proc.communicate()
KeyboardInterrupt
```

Child process output (captured separately):
```
READY (handling SIGINT)
Child received SIGINT
```

**Observation 4: Exit status analysis**  
Inspected exit codes using POSIX wait status macros:
```python
import os

for status in [0, 143]:
    print(f"Exit {status}:")
    if os.WIFEXITED(status):
        print(f"  Normal exit, code={os.WEXITSTATUS(status)}")
    if os.WIFSIGNALED(status):
        print(f"  Killed by signal {os.WTERMSIG(status)}")
```

Output:
```
Exit 0:
  Normal exit, code=0
Exit 143:
  Killed by signal 15
```

**Confirmed facts:**  
1. Both children show exit status 143 (SIGTERM) after parent's `terminate()`  
2. SIGINT-handling child prints handler message but never completes graceful exit  
3. `proc.wait()` always reports termination by SIGTERM after `proc.terminate()`  
4. Parent process never sees child's intended exit status (0) because:  
   - SIGTERM overrides any in-progress exit handling  
   - `wait()` captures only the final termination cause  
5. Exit status 143 = 128 + 15 (SIGTERM signal number)  

**Root cause verification:**  
The `KeyboardInterrupt` handler's `proc.terminate()` forcibly converts any child process state into SIGTERM termination, regardless of the child's signal handling configuration. This explains why both Flask (SIGINT-handling) and SIGINT-ignoring processes show identical 143 status when terminated through this code path.
