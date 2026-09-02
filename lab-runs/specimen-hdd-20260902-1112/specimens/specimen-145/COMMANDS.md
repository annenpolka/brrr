```
# not executed on this lab host
# failing_ref 17004093f058bfe45c59ab6e34fe3c46da86dbf8
# cli/download_source.go encodeSourceName / CopyFolderContents / cleanupDownloadDir

# public shape:
# leftover .terragrunt-cache path after ?ref= change
# encodeSourceName omits query; leftover stale.tf; leftover dest without .git
# rm -rf .terragrunt-cache yields the new source
```

Source-backed only. Do not execute untrusted checkouts on the host.
