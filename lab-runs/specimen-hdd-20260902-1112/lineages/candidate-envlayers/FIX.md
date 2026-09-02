# FIX envlayers

Date: 2026-09-02

Destroyer: `DESTROYER_envlayers.md` (missing `--file` raw Errno 2; duplicate-key spec hole).

Worktree: `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-envlayers-envlayers/envlayers/`

Branch: `specimen-hdd/candidate-envlayers-envlayers`

Commit: `29ccacf87ee3a8ddd6e01250efe5cedb6263c2ab`

Archive: `lab-runs/specimen-hdd-20260902-1112/lineages/candidate-envlayers/`

## Missing `--file`

`--file` of a path that does not exist printed:

```
envlayers: [Errno 2] No such file or directory: '…'
```

rc=1. That is a wrapped `OSError`, not a labeled miss.

Now:

```
envlayers: file not found: PATH
```

rc=1. No traceback, no `Errno`. A directory is `envlayers: is a directory: PATH`. Invalid UTF-8 is `envlayers: not utf-8: PATH`. Omitted `--file` is still rc=0 with `file	None`; that is not a missing path.

## Duplicate keys

Specified, not invented:

- `file` / `assign`: last assignment, including empty.
- `skip_empty`: last non-empty assignment. Empty does not unset an earlier file value and does not fall back to inherited while a non-empty file assignment exists.

`KEY=fromfile` then `KEY=`, inherited `/x`:

```
inherited	'/x'
file	''
skip_empty	'fromfile'
assign	''
```

`skip_empty` is `'fromfile'` (file), not inherited `'/x'`. Last-wins-then-skip (collapse the file to a map, then skip empty → inherited) is rejected.

## Tests

`python3 tests/test_envlayers.py` — missing file, directory, invalid UTF-8, omitted `--file` vs missing path, duplicate-key last-assignment vs last-non-empty.

## Demo

`./demo.sh` twice. Specimen-010 unchanged: `file ''`, `skip_empty '/x'`, `assign ''`.
