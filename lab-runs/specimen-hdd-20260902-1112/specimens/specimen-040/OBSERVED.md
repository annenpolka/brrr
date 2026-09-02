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
