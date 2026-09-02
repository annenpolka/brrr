```
# not executed on this lab host
# failing_ref 6b297d587cc12bea0372ca333fef34b522388b34
# earthfile2llb/interpreter.go handleCache
# earthfile2llb/converter.go Cache

# public shape:
# ARG something
# CACHE --id $something /id-test
# leftover cache mount identity is the unexpanded token
# later ARG something=bar reuses leftover foo mount
```

Source-backed only. Do not execute untrusted checkouts on the host.
