```
# not executed on this lab host
# failing_ref a2214422293d2c26ad389050f25460b3f2f00825
# src/cmd/go/internal/workcmd/sync.go runSync
# src/cmd/go/testdata/script/work_sync_replace.txt (on CL 762602, not failing_ref)

# public shape:
# go.work use ./a ./b
# a replace syncreplace v1.1.0 => v1.0.0
# b no replace
# go work sync
# failing: EditBuildList error continue; b/go.mod leftover workspace quote v1.0.0
```

Source-backed only. Do not execute untrusted checkouts on the host.
