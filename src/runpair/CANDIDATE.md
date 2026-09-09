# runpair

Smallest host-grounded candidate from this run.

## Operation contract

Run the same command twice in one working directory. After each invocation, report regular files that were added, removed, or changed in size. Do not open or interpret those files.

```
python3 scripts/runpair.py --cwd DIR -- CMD [ARGS...]
```

JSON stdout. The process exit of `runpair` is 0 if both invocations were started; command rc lives in `first.rc` / `second.rc`.

## Nearest existing operation

`CMD; ls` or `inotifywait` plus a second `CMD`. Those do not bind first-run sidecar files to second-run exit status as one contract.

## Observable delta

On the public 32113 files, `deno run a.js` twice: first rc 0 stdout `foo` and a new `deno.lock`; second rc 1 stderr contains `Invalid package requirement '@.'`. `ls` after the fact does not record that the sidecar appeared between the two identical commands.

## Classification

USEFUL_COMPOSITION of run + directory snapshot. Not claimed as a new foundational capability.

## Isolation

Merged onto coordinator `main` from branch `hdd-20260909-runpair`.
