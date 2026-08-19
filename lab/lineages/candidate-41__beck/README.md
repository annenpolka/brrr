# beck

Which pipeline stage first produced this byte (or line)?

Not `git blame`. Not file history (`whence`). Not a wait-source (`knot`). Given a pipeline — or a recorded per-stage trace — and a needle, emit the **earliest stage whose output already contains it**. Name the fd, whether that stage **minted / carried / wrapped**, and when a later stage assembled the exact bytes, the **earlier pieces**.

```
git status | cat | cat
          ▲
          stderr MINT  "fatal: not a git repository"
          tee on the pipe: miss
```

```
printf '{"name":"kizu","version":"0.7.0"}' | jq -r '.name + "@" + .version'
                                            ▲
                                            stdout WRAP  "kizu@0.7.0"
                                            pieces:  kizu  +  glue @  +  0.7.0
                                            tee | grep: names jq, not printf
```

`tee | grep -n` of the pipe dumps is the skeptic. It cannot see unpiped stderr, and an exact grep of those dumps names the wrap, not the substance.

## Install / run

Python 3.10+, stdlib, `bash`. No pip packages. `jq` / `rg` / `git` only for examples.

```bash
chmod +x ./beck ./demo.sh
./beck --selftest
./demo.sh
./beck --help
```

## Examples

### 1. Unpiped stderr — tee never sees it

```bash
./beck --quiet --needle 'fatal: not a git repository' --sh 'git -C /tmp status | cat'
```

`git` writes the line on **stderr**. Nothing entered the pipe. A `tee` between stages greps empty files. beck: `MINT  stage 0  stderr`.

### 2. Wrap — exact needle is assembled; pieces lived earlier

```bash
./beck --quiet --line 1 --sh \
  'printf "%s\n" "{\"name\":\"kizu\",\"version\":\"0.7.0\"}" | jq -r ".name + \"@\" + .version"'
```

Final line is `kizu@0.7.0`. Exact grep of tee dumps first hits **jq**. beck: `WRAP  stage 1  jq` with pieces `kizu` and `0.7.0` from printf, glue `@`.

### 3. Real pipeline: who minted the release line?

```bash
./beck --cwd ~/ghq/github.com/annenpolka/kizu \
  --needle 'release: v0.7.0' --sh 'git log --oneline | rg release | head'
```

`rg` and `head` only carry. First producer is `git log`. `--line 1` uses the first final line as the needle so you do not have to copy it.

```bash
./beck --needle STR --sh 'cmd | cmd'
./beck --needle STR --run -- printf hi + cat + cat
./beck --needle STR --trace run.json
./beck --save run.json --sh 'cmd | cmd'          # record, then query
./beck --json --quiet --needle STR --sh '...'
```

`--` ends options. A lone `+` is an explicit stage cut. `|` / `|&` / trailing `2>&1` are parsed with quote and `$()` honesty. Report is mint/carry/wrap; `--json` / `--tsv` compose.
