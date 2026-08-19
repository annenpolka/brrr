# candidate-41 — beck

## Primitive

Earliest pipeline stage whose output already contains this needle — naming the fd, mint/carry/wrap, and the earlier pieces when a later stage assembled the exact bytes.

## Why this might not exist

The workaround is to rewrite the pipeline with `tee` files and `grep -n`. That answers a different question:

1. **Unpiped stderr.** `git status | cat` prints `fatal: not a git repository` on git's stderr. Nothing entered the pipe. `tee | grep` of the dumps is empty. The user still saw the line.
2. **Wrap / construct.** `jq -r '.name + "@" + .version'` mints `kizu@0.7.0`. Exact grep of tee dumps names **jq**. The name and the version already lived in cargo's JSON. The object is the first producer of the *substance*, not the first exact match of the final spelling.
3. **Honest cuts.** Quoted `|`, `|&`, trailing `2>&1`, `$()` inner pipes. Naive `split('|')` lies.
4. **Recorded traces.** A tee'd run should be queryable later without re-running cargo.

Not `whence` (path-condition of a source line). Not `knot` (wait-source of a process tree). Not `git blame`. Not a third under-stream, a fourth cinch, leftover-name search, or inverse-printf.

The missing verb: **which stage first produced this byte?**

## How to run

From the worktree root:

```bash
chmod +x ./beck ./demo.sh
./beck --selftest
./demo.sh
./beck --quiet --needle 'fatal: not a git repository' --sh 'git -C /tmp status | cat'
./beck --quiet --line 1 --sh 'printf "%s\n" "{\"name\":\"kizu\",\"version\":\"0.7.0\"}" | jq -r ".name + \"@\" + .version"'
./beck --cwd /Users/annenpolka/ghq/github.com/annenpolka/kizu --needle 'release: v0.7.0' --sh 'git log --oneline | rg release | head'
./beck --cwd /Users/annenpolka/ghq/github.com/annenpolka/sitbone --needle 'dual-threshold hysteresis' --sh 'git log --oneline | rg hysteresis'
```

Python 3.10+, stdlib, `bash`. Exit 0 found, 1 not found, 2 usage.

## Empirical transcript

### v0.1 — exact first producer + fd + suffix payload

`--selftest` green on cuts (`'a|b'`, `||` vs `|`, `2>&1`, `$()`, `+`) and runs (mint stdout, unpiped stderr vs tee, wrap suffix, merged 2>&1, stdin carry, `--line`/`--span`).

First dogfood:

| pipeline | needle | v0.1 |
| --- | --- | --- |
| `git -C /tmp status \| cat \| cat` | `fatal: not a git repository` | **MINT stage 0 stderr**. tee sim: **MISS**. Naive `git \| tee s0 \| cat` piped **0 bytes**. Money shot. |
| `printf 'not a git repository' \| sed 's/^/fatal: /' \| cat` | `fatal: not a git repository` | **WRAP stage 1 sed**, payload suffix `'not a git repository'` from printf. tee names sed. |
| kizu `git log --oneline \| rg release \| head` | `release: v0.7.0` | **MINT git log** byte 8 line 1. rg/head CARRY. tee agrees (passthrough). |
| sitbone `git log --oneline \| rg hysteresis` | `dual-threshold hysteresis` | **MINT git log** line 4. e9b0f75. rg CARRY. |
| kizu `cargo metadata --offline \| jq -r '… \| .version'` | `0.7.0` | **MINT cargo** byte 367077 (one giant JSON line). jq CARRY — the field already existed. |
| kizu `cargo metadata \| jq -r '… \| "kizu@" + .version'` | `kizu@0.7.0` | **WRAP jq**. Payload **only** `'@0.7.0'` (longest suffix in cargo JSON). Missed that `kizu` was also cargo's. |
| `git -C /tmp status 2>&1 \| rg fatal` | same fatal | **MINT stage 0 stderr** still. tee sees the merge at stage 0. Honest fd after peel. |
| `--line 1` on `git log \| rg ^9349dc5` | (final line) | needle becomes `9349dc5 release: v0.7.0`, mint git. |

`tee | grep -n` is already the wrong object on the first two rows. The kizu construct row showed the remaining hole: **one suffix is not the substance**.

### v0.2 — greedy piece cover, from that run

Replace suffix/prefix payload with a left-to-right cover: at each offset take the longest fragment already present in an earlier stream; unmatched bytes are glue.

After v0.2:

Tiny JSON (the clean witness):

```
printf '{"name":"kizu","version":"0.7.0"}' | jq -r '.name + "@" + .version'
BECK  WRAP  stage 1  jq
      pieces  from printf 'kizu'  +  glue '@'  +  from printf '0.7.0'
      tee     stage 1 jq  (first exact; substance earlier)
```

kizu cargo (real graph):

```
pieces  from cargo 'kizu' (byte 367060)
        from cargo '@0.7.0' (byte 448982)
```

`@0.7.0` is *also* a substring of cargo metadata — `notify-debouncer-full@0.7.0` in the crate graph (8 hits). Greedy longest match at needle byte 4 absorbs the `@` that jq minted. Honest as bytes; the tiny-JSON fixture is the semantic `@` glue.

`./demo.sh 0` **33 passed, 0 failed**, including a live `tee | grep` that misses git stderr (0 piped bytes) and a live tee dump whose first exact hit is sed.

`--quiet` holds child stderr (still recorded) so JSON stays composable. `--save` / `--trace` round-trip the unpiped-stderr case.

## Dogfood targets

- `./beck --selftest` (14): cuts, mint, stderr vs tee, wrap pieces, 2>&1, stdin carry, jq concat, trace replay.
- `./demo.sh` 33: naive tee comparison, fixtures, kizu git/cargo, sitbone git.
- `/Users/annenpolka/ghq/github.com/annenpolka/kizu` — `git log \| rg`, `cargo metadata --offline \| jq`.
- `/Users/annenpolka/ghq/github.com/annenpolka/sitbone` — `git log \| rg hysteresis`.
- `git -C /tmp status` — the canonical unpiped-stderr needle.

## Surprises

- Cargo metadata is one line (~1.3MB). `0.7.0` first-producer is cargo, **col 367077**. jq extracting the field is CARRY, not wrap. Constructing `kizu@0.7.0` is wrap. Same jq, different object.
- The crates.io identity `name@version` already lives in `cargo metadata` JSON. Greedy cover of `kizu@0.7.0` therefore picks `'@0.7.0'` from `notify-debouncer-full@0.7.0`, not glue `@` plus kizu's own version. Byte-cover is not field-cover.
- `2>&1` peel lets beck keep **stderr** as the origin after the merge. tee agrees on stage and loses the fd.
- `--line 1` is the better everyday interface: you do not copy the needle; the final line *is* the needle, then the same walk.
- stdin into `cat | cat` is CARRY from `<stdin>`. Instrumenting only inside the pipeline with tee would have called first `cat` the producer.

## Failures

- Nested pipelines in `$()` / `{ foo | bar; }` are one outer stage. Inner first-producer is not walked.
- Greedy fragments are first-occurrence substrings, not aligned fields. `0.7.0` in cargo JSON is whichever crate version appears first at that spelling, not necessarily kizu's.
- `rg` with no match: needle not found (exit 1). Correct, but easy to misread as a beck bug.
- Process-substitution and `>file` redirections are left to bash inside a stage; stdout then never reaches the next pipe.
- ANSI / colorized git: matching is raw bytes. `git -c color.ui=always` would miss a plain needle.
- Binary needles work as bytes; human report UTF-8-replaces them.
- macOS `git` fatal text is stable here; translations would change the needle.

## Suggested mutations

- **field-cover**: JSON/key-aware pieces so `kizu@0.7.0` pairs with `.name` and `.version` of the same object, not `notify-debouncer-full@0.7.0`.
- **byte lineage of `--span`**: map a final byte range through wraps onto the earlier span(s), not just substring search.
- **inner stages**: descend into `$()` / script wrappers the way knot descends wait-source.
- **`--follow` a running trace**: JSONL of (stage, fd, offset) as bytes arrive; query without waiting for EOF.
- Inverse: `beck --mint-only --sh '…'` list lines each stage invented (the wrap's glue).

## Kill / keep

**Keep.** The object is first-producer of a byte in a pipeline, and it is empirically not `tee | grep -n`: git's fatal never enters the pipe (0 bytes), and `jq '"kizu@" + .version'` is first-exact at jq while `kizu` / `0.7.0` already lived in cargo. knot names wait-source. whence names path-conditions. Neither answers this.

Park: treating this as "insert tee and grep". That is the skeptic pipeline. It cannot name fd or pieces.
