```
# not executed on this lab host
# failing_ref e03454a3cffaafbbe5235078b6f2c5bf13ea32bc
# src/vcpkg/base/system.cpp get_environment_variable

# public shape:
# leftover unset after FOO= empty on Windows
# GetEnvironmentVariableW sz==0 JOINs empty and unset
# FOO=bar is a present string; POSIX getenv already splits
```

Source-backed only. Do not execute untrusted checkouts on the host.
