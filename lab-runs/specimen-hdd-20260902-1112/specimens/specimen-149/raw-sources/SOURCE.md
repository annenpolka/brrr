repository: compose-spec/compose-go
issue: https://github.com/docker/compose/issues/11962
pr: https://github.com/compose-spec/compose-go/pull/654
compose_pr: https://github.com/docker/compose/pull/11965
failing_ref (parent of squash on main): 65600cee45d45771a1faa6ddaf87b23ca4d2400c
fixed_ref (keepEmpty on environment resolve): 6adefd584b8088e0c6817bf54f5715595dd41301
merged_at: 2024-07-08T10:13:40Z
pr_author: ndeloof
merged_by: ndeloof
changed_files: loader/normalize.go, loader/normalize_test.go
pr_title: keep empty environment variables as those must be UNSET in container
scout_note: not 010 local env-empty / not 031 pip empty-override. leftover image ENV default after listed-without-equals dropped. unique vs 001-148.
