# once

If two paths ever held the **same git blob**, they are kin. That blob is the merge-base git never recorded. Port later drift with `git merge-file`.

No similarity. No basename heuristics. No `git diff -C`. A 56% copy is not kin. A file edited before `git add` is not kin. Exact object identity only.

## Install / run

```sh
chmod +x ./once ./demo.sh
./once -C /path/to/repo --pretty
./demo.sh
```

Requires Python 3 and `git`. No other dependencies.

Default output is TSV. `--pretty` for humans, `--json` for machines.

Exit codes: `0` success; `1` with `--check` when drifted kin exist, or `--port` with conflicts; `2` usage/git error / not kin.

## Examples

List drifted twins (currently-identical copies are hidden unless `--identical`):

```sh
./once -C ~/ghq/github.com/annenpolka/skills --pretty
```

Inspect a known pair and port unique changes from `FROM` onto `TO`. The base is the last shared blob, not a guessed similar file:

```sh
./once -C ~/ghq/github.com/annenpolka/skills \
  emergent-engine/SKILL.md emergent-engine/SKILL_claude.md
./once -C ~/ghq/github.com/annenpolka/skills \
  --port emergent-engine/SKILL.md emergent-engine/SKILL_claude.md
```

Update every forgotten snapshot of a live file. Safe only because the other path still *is* the merge-base blob (`cp` would be wrong if we had guessed similarity):

```sh
./once -C ~/ghq/github.com/annenpolka/skills --sync emergent-engine/SKILL.md
./once -C ~/src/repo --check
./once -C ~/src/repo --frozen --pretty
```
