```
# not executed on this lab host
# failing_ref cad2c455ec1acff29a81421c58adbe0ffc191f65
# src/libsystemd/sd-path/path-lookup.c get_paths_from_environ

# public shape:
# leftover cwd search path after SYSTEMD_UNIT_PATH=/foo::/bar
# unset is default path; "" is empty path; trailing : appends defaults
# new process / EINVAL after repair does not keep leftover cwd
```

Source-backed only. Do not execute untrusted checkouts on the host.
