# COMMANDS

Not executed in this packet. Commands as reported / as they would be in Django's cache tests.

```bash
git clone https://github.com/django/django.git
cd django
git checkout cd7554e5517992d5ca2594ffc936cb193daab26c
```

Relevant files:

- `django/middleware/cache.py`
- `tests/cache/tests.py` (`test_cached_control_private_not_cached`, `test_cache_page_timeout`)
- ticket reproducer view with `Cache-Control: no-store`

Focused test module (full Django test run is large):

```bash
python tests/runtests.py cache --verbosity=2
```

Ticket reproducer: run the view twice under the two-part cache middleware and compare bodies.
