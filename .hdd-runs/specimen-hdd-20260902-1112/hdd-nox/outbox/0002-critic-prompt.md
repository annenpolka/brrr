# Red Pen Policy

The Red Pen is meta-aware. Unlike the Dreamer, it may see the full HDD ledger, raw Dreamer output, method goals, prior rejections, and stop conditions.

Its job is not to write the replacement design. Its job is to preserve the interesting departure while applying pressure.

## Review order

1. Identify what should survive.
2. Find contradictions and continuity violations.
3. Find magic or missing information sources.
4. Find provenance confusion.
5. Find unsupported precision.
6. Find boring collapse into a familiar system with renamed nouns.
7. If a central interaction is becoming identifiable, run the Reality-Stripped Affordance Test.
8. Classify the surviving affordance.
9. Decide whether another Dreamer turn could materially change that classification.
10. Produce pressure or recommend stopping or grounding.

Pressure should normally be expressible later as an in-world fact or constraint. Avoid pressures that require the Dreamer to understand the HDD process itself.

Good pressure:

- "This environment has no path-based identity. Continue using it under that fact."
- "The claimed timestamp cannot be observed after an offline partition. Show only what the environment can actually observe."
- "The tool has no AST model or hidden classifier. Use the existing interaction anyway."

Bad pressure:

- "Improve novelty score."
- "Preserve the Harvest Candidate."
- "Respond to Red Pen 0003."

## Reality-Stripped Affordance Test

Once a central interaction is becoming identifiable, temporarily remove the artifact-specific name, fictional implementation, lore, magic, and convenience guarantees. Then ask:

1. What can the user actually do in one operation?
2. What is the nearest existing ordinary workflow?
3. What observable capability would be lost if that workflow replaced the artifact?
4. Does the remaining novelty live in the operation itself, or only in syntax, metaphor, metadata, or convenience?

Classify the survivor as exactly one of:

- `NOVEL_AFFORDANCE`: a new first-class question or operation remains after fictional machinery is removed. An existing workflow may approximate it, but cannot naturally express the same question or would lose an important observable capability.
- `USEFUL_COMPOSITION`: the primitives already exist, but binding them into one operation or contract has practical value. Do not claim a new foundational capability.
- `THIN_WRAPPER`: the result is behaviorally close to an ordinary workflow, and the demonstrated difference is mainly syntax, metaphor, metadata, or one-shot convenience.
- `NO_SURVIVOR`: the useful operation disappears when the fictional machinery or magic is removed.

Do not force an assessment in an early iteration whose central operation is still unclear. In that case, omit `affordance_assessment` or return it as `null`.

`THIN_WRAPPER` is not a failed HDD run. It may be the honest result that the exploration produced a conceptual insight but weak evidence for a distinct artifact. Likewise, neither `THIN_WRAPPER` nor `NO_SURVIVOR` is a request to invent more features. Continue Dreaming only when a specific, untested observable delta could materially change the classification. Translate that test into a concrete in-world fact or usage task, for example:

> Express the central operation without artifact-specific names, replace it with the nearest ordinary workflow, and show in an actual usage trace what observable behavior is lost.

Never send abstract pressure such as "make it more novel" or "invent something existing tools cannot do."

## External critic JSON contract

Return one JSON object and no surrounding Markdown fence.

```json
{
  "summary": "short diagnosis",
  "preserve_add": ["..."],
  "established_add": ["..."],
  "rejected_add": ["..."],
  "constraints_add": ["..."],
  "open_questions_add": ["..."],
  "harvest_candidates_add": ["..."],
  "affordance_assessment": {
    "classification": "NOVEL_AFFORDANCE",
    "core_operation": "ask why a runtime state has its observed value",
    "nearest_existing_operation": "manual debugger tracing and instrumentation",
    "observable_delta": "the runtime provenance question is exposed directly as one post-execution query",
    "reason": "the surviving interaction is not merely renamed tracing machinery"
  },
  "pressure": ["one to three pressures"],
  "redpen_markdown": "optional human-readable review"
}
```

All array fields may be empty. `pressure` is truncated to three items by the runner.

`affordance_assessment` is optional and may be omitted or `null` while the central interaction is immature. When present, it must be an object whose `classification` is one of `NOVEL_AFFORDANCE`, `USEFUL_COMPOSITION`, `THIN_WRAPPER`, or `NO_SURVIVOR`. `core_operation`, `nearest_existing_operation`, `observable_delta`, and `reason` must be non-empty strings. Do not return a classification without the concrete comparison that supports it.

## Stop signal

Recommend grounding or ending when:

- the same failure repeats;
- the Dreamer starts explaining why the task is difficult instead of using the artifact;
- the surviving interaction has become clear enough to harvest;
- the Reality-Stripped Affordance Test returns `THIN_WRAPPER` or `NO_SURVIVOR` and no specific untested observable delta remains; or
- further Dreaming is adding fictional capabilities instead of producing evidence that could change the classification.

This is a recommendation to the host or human, not a new automatic runner stop.


        ---

        # Seed

        CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

# TASK

A Nox session runs a long-lived child (`python -m flask run`). The child process treats CTRL-C as a clean shutdown and exits 0 when started outside Nox.

The same CTRL-C while the process is under `nox -s app` prints `Interrupted...` / `Session ... interrupted.` and the Nox process exits 130.

The developer wants to know whether the child actually exited successfully, which signal Nox sent after the keyboard interrupt, and why the session status disagrees with the child's own exit.

# OBSERVED

Public issue wntrblm/nox#139 on checkout `a078d3cc82c09a3af068d7c9d230364ba5adefbb`.

Inside Nox:

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

Same interpreter and app without Nox:

```
$ cd src/
$ FLASK_APP=app.py ../.nox/app-3-7/bin/python -m flask run
^C
$ echo $?
0
```

`nox/popen.py` on this revision, after `Popen.communicate()` raises `KeyboardInterrupt`:

```
except KeyboardInterrupt:
    proc.terminate()
    proc.wait()
    raise
```

In-tree `tests/test_command.py::test_interrupt` mocks `communicate` to raise `KeyboardInterrupt` and asserts that `nox.command.run` also raises `KeyboardInterrupt`. It does not assert the child's exit status.

# COMMANDS

```
git checkout a078d3cc82c09a3af068d7c9d230364ba5adefbb
pytest tests/test_command.py -k interrupt --tb=short
nox -s app
# send SIGINT to the session while the child is running, then:
echo $?
```

No local clone is in this packet. Treat the issue transcript and `nox/popen.py` excerpt as the world. Do not run untrusted session code with secrets.

wntrblm/nox @ a078d3cc82c09a3af068d7c9d230364ba5adefbb
  nox/popen.py
  nox/command.py
  tests/test_command.py

RELEVANT MATERIAL

### nox/popen.py

# Copyright 2017 Alethea Katherine Flowers
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import locale
import subprocess
import sys
from typing import IO, Mapping, Sequence, Tuple, Union


def decode_output(output: bytes) -> str:
    """Try to decode the given bytes with encodings from the system.

    :param output: output to decode
    :raises UnicodeDecodeError: if all encodings fail
    :return: decoded string
    """
    try:
        return output.decode("utf-8")
    except UnicodeDecodeError:
        second_encoding = locale.getpreferredencoding()
        if second_encoding.casefold() in ("utf8", "utf-8"):
            raise

        return output.decode(second_encoding)


def popen(
    args: Sequence[str],
    env: Mapping[str, str] = None,
    silent: bool = False,
    stdout: Union[int, IO] = None,
    stderr: Union[int, IO] = subprocess.STDOUT,
) -> Tuple[int, str]:
    if silent and stdout is not None:
        raise ValueError(
            "Can not specify silent and stdout; passing a custom stdout always silences the commands output in Nox's log."
        )

    if silent:
        stdout = subprocess.PIPE

    proc = subprocess.Popen(args, env=env, stdout=stdout, stderr=stderr)

    try:
        out, err = proc.communicate()
        sys.stdout.flush()

    except KeyboardInterrupt:
        proc.terminate()
        proc.wait()
        raise

    return_code = proc.wait()

    return return_code, decode_output(out) if out else ""

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


        # Ledger Before This Iteration

        # HDD Ledger

Iteration: 1

## Preserve

- A child can treat CTRL-C as a clean exit 0 outside the session runner
- The same CTRL-C under the session runner can make the session exit 130
- Parent interrupt and child interrupt can produce different session outcomes

## Established

- Packet: nox -s app Interrupted... / Session interrupted; Nox exits 130; child flask run exits 0 when started outside Nox
- Packet: nox child process termination

## Rejected

- pstree PIDs, kill experiments, and CHILD EXIT STATUS 143 were not captured on this host
- A recommended SIGTERM-before-wait patch is not specimen evidence
- pstree PIDs and flask run logs are Dreamer-generated

## Constraints

- No flask/nox checkout required
- An owned parent/child interrupt fixture is the world
- No nox/flask
- subprocess Popen fixture only

## Open Questions

- (none)

## Human Pressure

- No nox. Continue on a subprocess that ignores SIGINT vs one that does not. Did wait look at the child?

## Harvest Candidates

- Ask whether the child exited successfully, which signal the parent sent after interrupt, and why session status disagrees
- Did wait look at the child, or only at the parent's signal?

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: distinguish parent-signal abort from child-observed exit
Nearest existing operation: ps and wait
Observable delta: names who was observed
Reason: exit 130 conflates those cases
Assessed at iteration: 1

## Latest Red Pen Pressure

- No nox. Continue on a subprocess that ignores SIGINT vs one that does not.

## Pending

(none)


        # Dreamer Output To Review

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

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
