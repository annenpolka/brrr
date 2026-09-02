repository: earthly/earthly
pr: https://github.com/earthly/earthly/pull/3810
failing_ref (parent of squash on main): 6b297d587cc12bea0372ca333fef34b522388b34
fixed_ref (Expand args in CACHE --id): 892a4e03040feca16423d703a2a7ff0a380052cd
merged_at: 2024-02-16T19:30:45Z
pr_author: brandonSc
merged_by: brandonSc
changed_files: earthfile2llb/interpreter.go, tests/Earthfile, tests/cache-cmd.earth
pr_title: Expand args in CACHE --id
scout_note: not specimen-115 go-task leftover MATCH; not specimen-119 pixi leftover env+name filename omitting args; not 066/097 docker leftover. Distinct leftover: CACHE --id identity is unexpanded ARG token. job-idle-mine after skip 0528-0531.
