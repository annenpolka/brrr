# TASK

A Nox session runs a long-lived child (`python -m flask run`). The child process treats CTRL-C as a clean shutdown and exits 0 when started outside Nox.

The same CTRL-C while the process is under `nox -s app` prints `Interrupted...` / `Session ... interrupted.` and the Nox process exits 130.

The developer wants to know whether the child actually exited successfully, which signal Nox sent after the keyboard interrupt, and why the session status disagrees with the child's own exit.
