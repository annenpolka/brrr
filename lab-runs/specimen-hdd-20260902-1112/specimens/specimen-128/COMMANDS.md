```
# not executed on this lab host
# failing_ref 425174668513d0696a637e62c683ec5885999914
# lib/src/entrypoint.dart isLockFileUpToDate / isPackagePathsMappingUpToDateWithLockfile

# public shape:
# leftover .dart_tool/package_config.json after workspace: [sub, pkg_b]
# missing pkg_b omitted from up-to-date check
# dart run pkg_b:tool treated leftover mapping as current
```

Source-backed only. Do not execute untrusted checkouts on the host.
