# deja

Historical déjà vu for a git diff: say whether this change puts back deleted code, recreates a deleted path, or takes out a past bugfix.

## Install / run

Needs Python 3 and `git`. From this directory:

```bash
chmod +x deja
./deja --help
./demo.sh
```

Put `deja` on your `PATH`, or run it with `--repo /path/to/project` from anywhere.

| exit | meaning |
| --- | --- |
| 0 | clean |
| 1 | findings |
| 2 | usage / git error |

Default worktree scan is `git diff HEAD` plus untracked files whose paths history already deleted (`--untracked=resurrect`). Porcelain is one tab-separated finding per line.

## Examples

Inspect the working tree (staged + unstaged vs `HEAD`):

```bash
deja
deja --porcelain
```

Review a commit as if you were the last reviewer:

```bash
deja -c HEAD
deja -c 70ec7df --repo ~/src/sitbone
```

Pipe a patch — including the inverse of a deletion, which should come back as `RESURRECT` or `RELAPSE`:

```bash
git diff feature | deja --stdin
git diff 70ec7df 70ec7df^ -- Sources/SitboneUI/FocusRiverView.swift \
  | deja --repo ~/src/sitbone --stdin
```
