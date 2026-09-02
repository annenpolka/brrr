# Reality assessment

classification: USEFUL_COMPOSITION

Core operation: isolated file load of one import (unique
`spec_from_file_location` name) plus static `also` names leftover vs moved
same-name helpers.

Nearest: `from pkg_util import parse` + `inspect.getsource` and `grep def parse`.
Delta: one query pairs the body that import binds with the other def, without
executing sibling leftovers and without reporting stdlib `ast.parse` for a
leftover `ast.py`.
