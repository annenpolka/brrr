```
# not executed on this lab host
# failing_ref bc6f7be35057d15f8384c91ed500a610ab7e2a87
# source/git/source.go shaToCacheKey / CacheKey
# source/git/source_test.go TestMultipleTagAccessKeepGitDir (on the PR, not failing_ref)

# public shape (keepGitDir, two tags, one commit):
# GitIdentifier{Remote, KeepGitDir: true, Ref: "a/v1.2.3"}
# GitIdentifier{Remote, KeepGitDir: true, Ref: "a/v1.2.3-same"}
# failing: CacheKey equal (sha+".git"); Snapshot 2 can reuse Snapshot 1 .git
# intended: pin equal, key unequal when keepGitDir
```

Source-backed only. Do not execute untrusted checkouts on the host.
