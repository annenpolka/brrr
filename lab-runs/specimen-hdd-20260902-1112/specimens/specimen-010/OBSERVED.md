# OBSERVED

Owned fixture files/loader.py:

Inherited KEY=/x plus file `KEY=` (empty assignment).

Naive loader that skips falsey values leaves inherited `/x`.
A loader that always assigns stores empty string.

See COMMANDS for captured prints.
skip_empty '/x' '2'
assign '' '2'
unset_vs_empty False None
