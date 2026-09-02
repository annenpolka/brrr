```
# not executed on this lab host
# failing_ref cc17967ace76ff2fdf455106a6eb26da50685260
# src/pdm/cli/utils.py format_lockfile FileRequirement branch
# src/pdm/models/setup.py extras_require vs install_requires

# public shape:
# pdm lock
#   path = "../lib"
#   "lib @ file:///${PROJECT_ROOT}/../lib"
# pdm lock --update-reuse
#   path = "../lib"
#   failing: "lib @ file:///mnt/c/pdm-minimal/lib"
```

Source-backed only. Do not execute untrusted checkouts on the host.
