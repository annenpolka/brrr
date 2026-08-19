# mutation-107 — innard

## Primitive

Earliest pipeline stage that already contains this needle, **including inner `$()` stages**; mid-command `2>&1` is a stderr merge at that stage, not a trailing peel.

## Why this might not exist

Beck’s first-producer is real for unpiped git stderr and for `sed`/`jq` wraps. DESTROYER_BECK kept the object and named the remaining lie:

1. **`$()` is one outer stage.** `echo $(printf kizu | tr k K) | cat` mints at `echo $(…)`. The inner `tr` already assembled `Kizu`. `bash -c 'printf a | sed s/a/b/'` and `cat <(printf a | tr a b)` are the same wrap. Nested first-producer was parked, never walked.
2. **Mid-command `2>&1` is stdout.** Only a trailing `2>&1` is peeled. `git -C /tmp 2>&1 status | cat` lands on the stage’s stdout because bash merged before capture. The fd column is a parser of the stage string, not where git wrote.
3. **`{ }` was a docstring.** CANDIDATE listed brace groups next to `$()` as “one outer stage.” Empirical: three broken stages and a miss.

`tee | grep` still cannot see unpiped stderr. Exact grep of those dumps still names the wrap. Facet is same-object JSON fields. Knot is wait-source of a process tree. Leftover-name is a different object. None of those descend a command substitution.

The missing verb: **which stage first produced this byte, counting the inside of `$()`?**

## How to run

```bash
chmod +x ./innard ./demo.sh
./innard --selftest
./demo.sh
./demo.sh 0
./innard --help
./innard --quiet --needle 'Kizu' --sh 'echo $(printf kizu | tr k K) | cat'
./innard --quiet --needle 'fatal: not a git repository' --sh 'git -C /tmp 2>&1 status | cat'
./innard --quiet --needle 'fatal: not a git repository' --sh 'git -C /tmp status | cat'
./innard --cwd /Users/annenpolka/ghq/github.com/annenpolka/kizu \
  --needle 'release: v0.7.0' --sh 'git log --oneline | rg release | head'
```

Python 3.10+, stdlib, `bash`. Exit 0 found, 1 miss, 2 usage.

## Empirical transcript

### v0.1 — inner `$()` + mid-command `2>&1`

`--selftest` 25/25. `./demo.sh 0` **35 passed, 0 failed**.

Gold unpiped git stderr still holds. Naive `git -C /tmp status | tee s0 | cat` pipes **0 bytes**. innard:

```
INNARD  MINT  stage 0  stderr  git -C /tmp status
        tee     MISS
        note    tee on the pipe never sees unpiped stderr
# piped_bytes=0  disagrees_with_tee=true
```

The lie beck admitted, now walked:

```
$ ./innard --quiet --needle 'Kizu' --sh 'echo $(printf kizu | tr k K) | cat'
INNARD  WRAP  stage 0.1  stdout  tr k K
        nest    $() of  echo $(printf kizu | tr k K)
        pieces  glue 'K'  +  from printf 'izu'
        tee     stage 0  echo $(…)   (first exact on the outer pipe)
        later   stage 0 echo carry   stage 1 cat carry

$ ./innard --quiet --needle 'kizu' --sh 'echo $(printf kizu | tr k K) | cat'
INNARD  MINT  stage 0.0  stdout  printf kizu
        nest    $() of  echo $(printf kizu | tr k K)
        tee     MISS   # the user's pipe only ever saw Kizu
```

Inner stage ≠ outer wrap. `bash -c 'printf a | sed s/a/b/'` mints at inner `sed`. `cat <(printf a | tr a b)` mints at inner `tr`. Nested `echo $(echo $(printf kizu | tr k K))` still names `tr`.

Mid-command `2>&1` is a merge at that stage. Same git, same needle, origin fd **stderr**:

```
$ ./innard --quiet --needle 'fatal: not a git repository' --sh 'git -C /tmp 2>&1 status | cat'
INNARD  MINT  stage 0  stderr  git -C /tmp status
        tee     stage 0  piped  (same stage)
# merge_stderr=true  argv has no leftover 2>&1
```

Trailing `2>&1` / `|&` unchanged. `{ printf kizu | tr k K; } | cat` is one outer stage and a walked inner `tr` — parser honesty, not the product.

Dogfood:

| pipeline | needle | innard | tee |
| --- | --- | --- | --- |
| kizu `git log --oneline \| rg release \| head -5` | `release: v0.7.0` | **MINT git** byte 8 line 1. rg/head CARRY | same stage |
| kizu `echo "$(git log --oneline \| rg release \| head -1)"` | `release: v0.7.0` | **MINT git** nest `$()` path 0.0. echo is later carry | names echo |
| sitbone `git log --oneline \| rg hysteresis \| cat` | `dual-threshold hysteresis` | **MINT git** byte 192 line 4 | same stage |
| `git -C /tmp status \| cat` | fatal | **MINT stderr** piped_bytes=0 | miss |
| `echo $(git -C /tmp status) \| cat` | fatal | **MINT git** nest `$()` stderr. tee miss | miss |
| `echo $(git -C /tmp 2>&1 status) \| cat` | fatal | **MINT git** nest `$()` stderr, merge | names echo |

### v0.2 — `$()` stderr leak is not remint (from that run)

`echo $(git -C /tmp status) | cat` already minted at inner git. The later column lied:

```
later   stage 0  remint  stderr  echo $(git -C /tmp status)
```

`$()` captures stdout only. Inner git’s stderr **is** the wrap’s stderr (fd inheritance). The wrap did not remint the fatal. After:

```
INNARD  MINT  stage 0.0  stderr  git -C /tmp status
        nest    $() of  echo $(git -C /tmp status)
        tee     MISS
        note    $() captures stdout only; inner stderr never entered the substitution
        later   stage 0  leak  stderr  echo $(git -C /tmp status)
```

`--selftest` 27/27. `./demo.sh 0` **38 passed, 0 failed**. `printf hi | echo hi` occupancy-carry is untouched (that is a different object).

## Dogfood targets

- `./innard --selftest` (v0.1 25; v0.2 27, leak + occupancy).
- `./demo.sh`: gold tee-miss, `$()` ≠ wrap, mid `2>&1`, bash -c, `<()`, sed/jq wraps, kizu git log, kizu `$()`, sitbone, `$()` git fatal leak, stdin carry.
- `/Users/annenpolka/ghq/github.com/annenpolka/kizu` — `git log | rg | head` and the same pipeline inside `echo "$(…)"`.
- `/Users/annenpolka/ghq/github.com/annenpolka/sitbone` — `git log | rg hysteresis`.
- `git -C /tmp status` — unpiped and mid-command `2>&1`, bare and inside `$()`.

## Surprises

- Command substitution does not capture stderr, but the wrap **still has** those bytes on its own stderr (same fd). First-producer search order (inners before wrap) is load-bearing. The later column is where the wrap lie came back as `remint`.
- Greedy cover of `Kizu` against `printf kizu` is glue `K` + `izu`, not “tr case-folded kizu.” Byte-cover, same as beck. The product is the inner stage, not a better piece algebra.
- Tee on the outer pipe for needle `kizu` against `echo $(printf kizu | tr k K)` is a **miss**. The user’s pipe only ever saw `Kizu`. That is honest.
- Empty `--sh ''` hits `split_pipeline` (`empty pipeline`, rc=2), not beck’s usage banner. Accidental; kept.

## Failures

- Inner pipelines are re-executed (once instrumented, once inside the wrap). Side-effecting `$()` would be recorded twice. Not a process-tree walk.
- `{ }` descent exists so the parser is not three syntax errors. It is not the primitive and is not sold as `$()`.
- `printf hi | echo hi` is still occupancy-carry. DESTROYER asked for a data-flow edge; not this mutation.
- Greedy JSON coincidence `kizu@0.7.0` vs `notify-debouncer-full@0.7.0` is still beck’s hole. Facet owns it.
- `--run +` still `" ".join`s. `--sh` is the honest door.
- Single-byte needles (`b` from `sed s/a/b/`) cannot wrap (cover requires len≥2). Inner `sed` is still named. Mint, not wrap.

## Suggested mutations

- Data-flow carry: `printf hi | echo hi` is remint (echo did not read). Occupancy of `prev.piped` stays the skeptic.
- Field-cover handoff to facet when the wrap is `jq` and the earlier dump is JSON.
- `--span` lineage through a `$()` wrap onto the inner byte range.
- Refuse to re-exec: rewrite the wrap with the recorded inner stdout (deterministic `$()` only).

## Kill / keep

**Keep.** The object is still first-producer of a byte. Git fatal still never enters the pipe (`piped_bytes=0`, tee miss). The new gold is inner ≠ wrap: `echo $(printf kizu | tr k K)` names `tr`, kizu `echo "$(git log | rg | head)"` names `git log`, `git 2>&1 status` names **stderr**. Knot names wait-source. Facet names same-object fields. Leftover-name is a different verb. Do not kill because `{ }` also walks, because greedy `K`+`izu` is ugly, or because inners are re-run.
