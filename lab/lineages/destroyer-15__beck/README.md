# destroyer-15 — beck

Adversarial pass on **beck**: which pipeline stage first produced this byte?

Not a rewrite of the victim. Not knot. Not whence. Gold is unpiped git stderr (tee sees 0 bytes). The peel is facet's JSON field-cover hole: greedy `kizu@0.7.0` still pairs with `notify-debouncer-full@0.7.0`.

Verdict: **mutate, do not kill.** Full writeup: `DESTROYER_BECK.md`.

## How to run

Victim (do not edit):

```bash
BECK=/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01bad-eb91-7d80-9aa0-1108ac34ccbe/beck
chmod +x "$BECK" ./demo.sh ./attack.py
"$BECK" --selftest
./demo.sh
python3 ./attack.py          # writes /tmp/destroy-beck/
```

Python 3.10+, stdlib, `bash`, `jq`, `rg`, `git`, `cargo` for dogfood. `facet` optional (same cargo dump).

## Examples

### 1. Git fatal never enters the pipe

```bash
git -C /tmp status | tee /tmp/t0 | cat   # 0 piped bytes; grep miss
"$BECK" --quiet --needle 'fatal: not a git repository' --sh 'git -C /tmp status | cat'
# BECK  MINT  stage 0  stderr  git -C /tmp status
#       tee     MISS
```

### 2. Facet hole still in beck (byte-cover ≠ field-cover)

```bash
CARGO=/tmp/destroy-beck/fixtures/kizu-cargo.json
"$BECK" --quiet --needle 'kizu@0.7.0' --sh \
  "cat $CARGO | jq -r '.packages[] | select(.name==\"kizu\") | .name + \"@\" + .version'"
# WRAP jq; pieces  kizu@367060  +  @0.7.0@448982 (notify-debouncer-full .id)
# facet on the same dump: siblings kizu .name + glue @ + .version@367077
```

### 3. `{ }` is not `$()` — CANDIDATE claimed one outer stage

```bash
"$BECK" --quiet --needle Kizu --sh '{ printf kizu | tr k K; } | cat'
# BECK NONE  rc=1  — split into `{ printf kizu` | `tr k K; }` | `cat`
# echo $(printf kizu | tr k K) | cat  → MINT echo (inner not walked, but it runs)
```
