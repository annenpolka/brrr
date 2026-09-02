# OBSERVED

Owned fixture: files/pkg_util.py and files/pkg_parse.py plus files/test_parse_identity.py.

`from pkg_util import parse` vs `from pkg_parse import parse` bind different functions with the same name. A stale test import still hits the leftover helper.
util ('legacy', '  z  ')
parse ('moved', 'z')
same_function False
stale_test_would_see legacy
