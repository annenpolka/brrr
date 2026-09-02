```
# not executed on this lab host
# failing_ref b4ee407a256ac2e4f4f3a5419387b43815cf6be7
# src/install/PackageManager/PackageJSONEditor.rs edit_update_no_args
# test/cli/install/catalogs.test.ts describe("update") (on the PR, not failing_ref)

# public shape:
# root catalog: { "no-deps": "^1.0.0" }
# packages/app: { "no-deps": "catalog:" }
# bun update --latest   # from packages/app
# failing: member "no-deps" is a caret range; root catalog still ^1.0.0
```

Source-backed only. Do not execute untrusted checkouts on the host.
