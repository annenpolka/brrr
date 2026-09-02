```
# not executed on this lab host
# failing_ref 23e865c5601534f14cfe5fbc097c2eb1cf4f342e
# packages/cli/src/Generate.ts watch loop reuses leftover schemaContext

# public shape:
# leftover generated client after schema.prisma appends model B
# watch generate identity is first-load schemaContext
# generated/models stays ['A.ts'] until non-watch prisma generate
```

Source-backed only. Do not execute untrusted checkouts on the host.
