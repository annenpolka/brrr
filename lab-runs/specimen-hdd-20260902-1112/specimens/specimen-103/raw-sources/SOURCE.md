repository: golang/go
issue: https://github.com/golang/go/issues/65363
pr: https://go-review.googlesource.com/c/go/+/762602
failing_ref (CL parent): a2214422293d2c26ad389050f25460b3f2f00825
fixed_ref (submitted CL): 8191cd88683192e9aa3f3a1c11e841f8f40a9a9d
merged_at: 2026-04-29T18:17:32Z
pr_author: matloob
changed_files: src/cmd/go/internal/workcmd/sync.go, src/cmd/go/testdata/script/work_sync_replace.txt, testdata/mod example.com_syncreplace v1.0.0/v1.1.0
pr_title: cmd/go: loosen go work sync version requirements
scout_note: not specimen-084 sumdb leftover. not cargo#14230 unfixed. Distinct leftover: go work sync mustSelect from workspace replaces then EnterModule uses module replaces; EditBuildList continue leaves leftover go.mod identity.
