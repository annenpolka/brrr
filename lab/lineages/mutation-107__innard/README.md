# innard

Earliest pipeline stage that already contains this needle — **including inner `$()` stages**. Mid-command `2>&1` is a stderr merge **at that stage**, not a trailing-token peel.

Beck names the outer wrap. `echo $(printf kizu | tr k K)` is not one mint. The inner `tr` assembled `Kizu`. `{ }` as “one outer stage” without a walk was a lie; innard walks `$()` / `bash -c` / `<( )` (and a brace group only so it is not three bash syntax errors). Not leftover-name. Not a wait-source (`knot`).

```
echo $(printf kizu | tr k K) | cat
                 ▲
                 stdout WRAP  tr k K    nest $()
                 tee on the outer pipe: echo
```

```
git -C /tmp 2>&1 status | cat
        ▲
        stderr MINT  git   (fd at the redirect, not stdout-because-bash-merged)
```

```
git -C /tmp status | cat
        ▲
        stderr MINT  git   piped_bytes=0
        tee on the pipe: miss
```

`tee | grep` of the outer pipe is the skeptic. It cannot see unpiped stderr, and an exact grep of those dumps names the wrap, not the inner first-producer.

## Install / run

Python 3.10+, stdlib, `bash`. No pip packages. `jq` / `rg` / `git` only for examples.

```bash
chmod +x ./innard ./demo.sh
./innard --selftest
./demo.sh
./innard --help
```

Exit 0 found, 1 miss, 2 usage.

## Examples

### 1. Inner `$()` is not the outer wrap

```bash
./innard --quiet --needle 'Kizu' --sh 'echo $(printf kizu | tr k K) | cat'
```

Beck names `echo $(…)`. innard: `WRAP  stage 0.1  stdout  tr k K` with `nest $()`. Tee on the outer pipe still names echo.

### 2. Mid-command `2>&1` keeps the origin fd

```bash
./innard --quiet --needle 'fatal: not a git repository' --sh 'git -C /tmp 2>&1 status | cat'
```

The redirect is not trailing. innard peels it as a merge **at that stage** and reports **stderr** (where git wrote). Tee sees the pipe; the fd column is not “stdout because bash merged before we looked.”

### 3. Gold: git fatal never enters the pipe

```bash
./innard --quiet --needle 'fatal: not a git repository' --sh 'git -C /tmp status | cat'
```

`git` writes the line on **stderr**. Nothing entered `|`. `tee | grep` of the dumps is empty. innard: `MINT  stage 0  stderr`. Same gold as beck.

```bash
./innard --cwd ~/ghq/github.com/annenpolka/kizu \
  --needle 'release: v0.7.0' --sh 'git log --oneline | rg release | head'
./innard --needle STR --sh 'cmd | cmd'
./innard --json --quiet --needle STR --sh 'echo $(printf a | tr a b)'
./innard --save run.json --sh 'cmd | cmd'
./innard --needle STR --trace run.json
```
