```
# not executed on this lab host
# failing_ref 843a683fef61e9b3f9607ab637b72b0774241513
# src/cargo/sources/git/utils.rs absolute_submodule_url / update_submodule
# tests/testsuite/git.rs dep_with_scp_like_submodule_url

# public shape:
# .gitmodules: url = git@github.com:foo/bar.git
# cargo fetch
# failing: [UPDATING] git submodule `ssh://git@github.com/foo/bar.git`
```

Source-backed only. Do not execute untrusted checkouts on the host.
