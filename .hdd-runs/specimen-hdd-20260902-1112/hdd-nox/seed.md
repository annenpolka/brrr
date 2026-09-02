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
