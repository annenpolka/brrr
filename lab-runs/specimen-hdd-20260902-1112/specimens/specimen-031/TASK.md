# TASK

A pip checkout sits at 545eda389c41478e2f99d23212254d757d8c2cef (around pip 25.3).

Two configuration layers both set `global.proxy`:

- system/global pip.conf: `proxy = http://non_existing_proxy_server.tld`
- user pip.conf: `proxy =` (key present, value empty)

The operator cannot edit the global file. They want the empty user value to disable the global proxy so install uses the ordinary network (or HTTP(S)_PROXY from the process environment), as it did on pip 25.0.1.

Outcome sought: explain the contrast between “key absent”, “key present and empty”, and “key present and non-empty” across config layers, and why an empty user setting no longer voids the global proxy.
