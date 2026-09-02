```
# not executed on this lab host
# failing_ref 8ed846c73b5033087eee119ae00511e019f91729
# src/compiler/builder.ts computeSignature / d.ts emit signature
# leftover: .tsbuildinfo file signature = hash(d.ts text) only

# public shape:
# incremental true; public -> protected (error) -> public
# leftover: TS2445 still reported on importer
# incremental false: clean
```

Source-backed only. Do not execute untrusted checkouts on the host.
