# DESTROYER — pin × invert

Adversarial pass on two Gen-2 survivors. No rewrites: the failures are conceptual, not one-line bugs.

- **pin** (durable locator token) — `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01ad1-c9bb-74f2-a42f-2d3d48dd67a5`
- **invert** (stream inverse-printf) — `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01ad1-c9bb-74f2-a42f-2d465380e59f`
- Transcript: `/tmp/destroy-pin-invert/transcript.txt`
- Fixtures: `/tmp/destroy-pin-invert/`
- Both `selftest` still exit 0 after the attacks.

Verdict: **mutate, do not kill.** The flipped assumptions are still visible. The attacks show where each primitive pretends to be more than it is.

---

## pin

Primitive restated: mint a self-contained fingerprint once; resolve it onto *any later tree* without re-supplying `path:line`.

### 1. Huge files — silent invisibility (conceptual)

`MAX_FILE_BYTES = 1_000_000`. `decode_bytes` returns `None`; the path is omitted from the snapshot. Mint then lies: “source path not in snapshot.”

```
$ ./pin mint --repo $UGLY --from $V1 src/godfile.py:1
pin mint: source path not in snapshot: src/godfile.py
# mint_rc=1
# godfile is 1_200_000 bytes, unique locus on line 1: def unique_locus_ZEBRA99()
```

Same via `--from-dir`. A 900 KB file *is* loaded (`src/almost_huge.py:10348` minted in 0.11s). The cutoff is a hard omit, not a warning. A split that lands the locus inside a generated/minified >1 MB file cannot be minted or resolved. Not a linux.git-scale problem — a single godfile.

No one-line fix: the limit is load-bearing. A real mutation is “mint from a single file, do not index the world.”

### 2. File splits — leftover stub steals the pin (conceptual, lethal to the pitch)

The demo deletes `src/calc.py` and only then claims `src/app.rs → src/app/*.rs`. Real splits leave a re-export at the old path.

v2 of the ugly repo:

```
src/calc.py          # stub: def helper_keep(): from src.calc.ops import …
src/calc/ops.py      # real body: return "stable helper"
src/legacy/calc.py   # identical helper, basename bait
```

```
$ PIN=$(./pin mint --repo $UGLY --from $V1 src/calc.py:14)
$ ./pin show "$PIN"
  minted: src/calc.py:14
  text:   def helper_keep():
  unique: helper_keep
  after:
    -     return "stable helper"

$ ./pin resolve --repo $UGLY --to $V2 --porcelain "$PIN"
shifted	-	src/calc.py:14	src/calc.py:3	1.000	same file, line number drifted
```

It landed on the stub (`def helper_keep():` + import), not `src/calc/ops.py:7` (same line text + original body) and not `src/legacy/calc.py:3` (identical clone).

Why: exact-line + (`unique_tok` or `fp.path == dst_path`) short-circuits to **1.0**. The original path still exists, so the leftover wrapper is identity. Neighbors (`return "stable helper"`) never get a vote. `add()` did the same: `src/calc.py:3 → src/calc.py:7` (the stub’s `def add`), not `src/calc/ops.py:3`.

**The file-split story only holds if the old path is gone.** That is the common case in the kizu godfile split; it is not the common case in a module extraction.

### 3. Identical helper lines — 1.000 is not uniqueness (conceptual)

Two dest copies of the exact source line, no leftover stub:

```
ident_from/src/calc.py     def helper_keep(): / return "stable helper"
ident_to/a/ops.py          identical
ident_to/z/calc.py         identical (basename bait)
```

```
$ ./pin resolve --to-dir $IDENT_TO --porcelain "$IDPIN"
moved	-	src/calc.py:1	z/calc.py:1	1.000	path or surrounding file changed
```

`helper_keep` has dest `token_df == 2`, which pin still treats as unique (`<= 2`), so **both** copies score 1.0. `resolve_fingerprint` keeps the first 1.0. Walk order / basename picked `z/calc.py`. No “ambiguous” status. A pin that claims uniqueness cannot emit 1.000 at two addresses and hide one.

### 4. Unicode paths — NFC/NFD is a different file (conceptual)

CJK `src/日本語.py` and emoji `src/🔥hot.py` mint and resolve at 1.000 (NFC == NFD for those codepoints). Combining-character names do not:

```
$ git -C $UGLY ls-files
src/café.py          # stored NFC: src/caf\xe9.py

$ ./pin mint --from $V1 $'src/caf\u00e9.py:1'     # NFC
pin1.eNqr…   # ok

$ ./pin mint --from $V1 $'src/cafe\u0301.py:1'    # NFD
pin mint: source path not in snapshot: src/café.py
```

APFS treats those as the same inode. Git + pin compare bytes. A macOS paste, `os.listdir`, or NFD-normalized locator misses a file that is sitting right there. Not a crash; a false “not in snapshot.”

### 5. Missing `--to` tree — typo looks like deletion (conceptual)

| invocation | result |
| --- | --- |
| `--repo $UGLY` no `--to` | worktree (v2). Lands on the stub. Documented default. |
| no `--repo`, cwd `/tmp` | `pin: not a git repository` exit 1. Honest. |
| `--to-dir` missing path | `pin: not a directory` exit 1. Honest. |
| `--to this-ref-does-not-exist` | `deleted  src/calc.py:14  -  0.000  no candidates` **exit 0** |
| `--to-dir` empty dir | same `deleted` / exit 0 |

`git ls-tree` on a bad ref fails; `load_git_paths` returns `[]`; the empty snapshot is a successful delete. A typo in `--to` is indistinguishable from “this function is gone.” `--strict` does not help (`deleted` is not `unresolved`).

### 6. Truncated pin tokens — porcelain success, exit 0 (conceptual)

```
$ ./pin resolve --repo $UGLY --to $V2 --porcelain 'pin1.eNptjMsKwjAURH8lzEohKIKr…'   # half token
unresolved	-	?:0	-	0.000	corrupt pin: Error -5 while decompressing data: incomplete or truncated stream
# rc=0

$ ./pin resolve --repo $UGLY --to $V2 --porcelain pin1.xxxx
unresolved	-	?:0	-	0.000	corrupt pin: Error -3 while decompressing data: incorrect header check
# rc=0

$ ./pin resolve … --strict --porcelain "$HALF"
# same line, rc=1

$ ./pin show 'pin1.eNptjMsKwjAURH8'
pin show: corrupt pin: Error -5 while decompressing data: incomplete or truncated stream
# rc=1
```

A ticket wrap / Slack clip of `pin1.…` is accepted as a pin (`is_pin_token` is `startswith("pin1.") and len>7`), resolved against the whole tree, and printed as a result row. `show` fails closed; `resolve` does not, unless `--strict`. The object is the token — a broken token should not look like a landed search.

### 7. Resolving onto an unrelated repo — the token has no origin (conceptual)

The pitch is “land it on whatever tree you have now.” That is also the footgun.

```
$ ./pin resolve --repo $UNREL --to HEAD --porcelain "$HELPER"
moved	-	src/calc.py:14	pkg/util.py:1	1.000	path or surrounding file changed
```

`$UNREL` is a different git repo whose `pkg/util.py` happens to contain `def helper_keep():` / `return "stable helper"`. Score 1.000, status `moved`. There is no repo id, no origin SHA, no “wrong tree” signal.

Controls that *survive*:

```
# unique kizu pin → voidtrace
deleted	-	src/app.rs:529	-	0.000	no candidates

# same pin → tenaoshi
deleted	-	src/app.rs:529	-	0.000	no candidates

# voidtrace `import {` → kizu
deleted	-	packages/kernel/src/evaluate.ts:1	-	0.000	no candidates

# kizu `use std::cell::{Cell, RefCell};` → voidtrace
deleted	-	src/app.rs:2	-	0.154	best candidate below threshold
```

So the unique-token case is honest across languages. The failure is the *common* case the pin exists for: a helper that is not globally unique, resolved on the wrong checkout, reported as a perfect move.

---

## invert

Primitive restated: runtime string on argv/stdin, templates on the other channel, named hole bindings, leftover prefix is a span. No walk.

### 1. Truncated log lines — miss, as designed, and that is the hole (conceptual)

CANDIDATE already lists abridged 7-hole pastes. Confirmed on the fixture Logger line:

```
$ rg -n -g '*.swift' awayRecovered fixtures | ./invert --templates - \
    'transition focused → idle reason=timeout idle=12s'
— no template for: transition focused → idle reason=timeout idle=12s
# exit 1

$ … | ./invert --templates - 'transition focused → idle'
— no template for: transition focused → idle
# exit 1

$ … | ./invert --templates - 'user 42 not'
— no template for: user 42 not

$ rg … kizu | ./invert --templates - '2026-08-19T23:50:01Z ERROR failed to spawn `git ap'
— no template for: 2026-08-19T23:50:01Z ERROR failed to spawn `git ap
```

Alignment requires the remaining static literals (`deserted=`, closing `` ` ``, `not found`). Real logs are truncated by syslog, terminal wrap, and humans. Invert inverse-printfs an *instance*, not a prefix of an instance. `--exact` is the other knob; there is no “prefix of a holed template” mode. Full 7-hole control still scores 1.12 and binds.

### 2. Concatenated strings — not a template (conceptual)

```
# concat.go
return errors.New("open " + path + ": " + err.Error())   # line 4
return fmt.Errorf("open %s: %v", path, err)              # line 8

$ ./invert --templates concat.go --extract
concat.go:4:20: lang=go holes=0 static=5 open
concat.go:8:20: lang=go holes=2 static=7 open {1}: {2}

$ ./invert --templates concat.js 'open /tmp/x: permission denied'
— no template for: open /tmp/x: permission denied
# JS file has only the + form; extract is the 5-char literal "open "
```

The Go query “succeeds” only because a sibling `fmt.Errorf` lives in the same file and `--templates` slurps it. The `+` chain is two short literals, never one template. Adjacent concatenation remains the unfmt/sluice/invert family blind spot.

### 3. rustc diagnostics — wrong grammar, confident bindings (conceptual)

invert assumes printf-shaped runtime strings. rustc is a different object (`error[E0308]`, `--> file:line`, caret lines).

```
$ rg -n -g '*.rs' -g '!target/**' 'format!|anyhow!' kizu \
    | ./invert --templates - -e 'error[E0308]: mismatched types'
— no template for: error[E0308]: mismatched types
# honest miss
```

The location line is worse:

```
$ … | ./invert --templates - -e '   --> src/git/revert.rs:46:18'
kizu/src/app.rs:5778:52: score=0.48 lang=rust holes=1 via=span from=file
  query: --> src/git/revert.rs:46:18
  tmpl:  src/{i}.rs
  {i} = git/revert
  prefix: -->
```

That template is a **test fixture** (`format!("src/{i}.rs")` around app.rs:5778). invert bound a rustc path onto it. Span leftover makes a compiler diagnostic look like a successful inverse-printf.

A rustc snippet of the source *can* recover the real spawn string (span over `anyhow!("…")`), so the failure is not “rustc never hits” — it is “rustc hits the wrong thing first, with a named binding.”

Piping the whole transcript as queries against `fixtures/src/git.rs` missed every line (including `Compiling kizu…`, which `SKIP_STDIN_RE` does *not* drop — only the exact `^Compiling\b` skip is for invert’s own template-side filter; as a query it is printed as a miss). rustc-as-templates (`--from raw`) also missed `failed to spawn …`. invert will not ingest compiler output as either channel in a useful way.

### 4. Empty template stream — survives

```
$ printf '' | ./invert 'user 42 not found'
invert: 0 templates ingested
— no template for: user 42 not found
# rc=1
```

Same for `--templates -`, newline-only stdin, and `--templates /dev/null`. Honest. Not a walk.

### 5. 10 MB stdin — lives, then drowns you

Queries (`--templates raw.txt --any`, 327_680 copies of `ERROR [worker] user 7 not found`):

```
query_bytes 10485760 lines 327680
rc 0 elapsed 3.243s stdout_bytes 102891520
```

`--any` only flips the exit code. It still formats every line. 10 MB in, **98 MB** of identical hits out.

Templates (180_788 duplicate grep lines of `user {uid} not found`): 5.25s, one deduped hit, `{uid}=7`. Ingest cap is accidental (`seen` key on `(path,line,col,display)`). Fine.

Not a hang. Not a primitive kill. `--any` is misnamed for a stream filter.

### 6. Binary stdin — crash (bug, not conceptual)

```
$ dd if=/dev/urandom bs=4096 count=8 | ./invert --templates - 'user 42 not found'
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xee in position 1
```

Same on stdin-as-queries (`sys.stdin.read()` in `main` and `load_template_spec`). File templates already refuse NUL (`binary template file: … (try -0)`). Stdin does not. Mixed random+real line also dies before the real line is seen.

A decode-with-replace (or the same NUL refuse) is a small robustness patch, not a one-line conceptual fix. Left unpatched: refuse vs replace is a design choice, and the interesting invert failures are ranking/grammar, not codec.

### 7. No-hole templates that prefix-match — outrank the holed source (conceptual)

v0.2’s pitch: reward holes, do not tax them; query-coverage ranking keeps the 7-hole above a static substring.

```
$ ./invert --templates prefix.rs -n 5 \
    '2026-08-19T23:50:01Z ERROR failed to spawn `git apply --reverse`'
prefix.rs:7:13: score=0.67 lang=rust holes=0 via=full
  tmpl:  2026-08-19T23:50:01Z ERROR failed to spawn
  note:  suffix=' `git apply --reverse`'

prefix.rs:2:13: score=0.48 lang=rust holes=1 via=span
  tmpl:  failed to spawn `{1}`
  {1} = git apply --reverse
  prefix: 2026-08-19T23:50:01Z ERROR
```

The documentation decoy (no holes, long static prefix of the paste) **beats** the real `format!("failed to spawn `{cmd}`")`. Same ranking on a raw stream of

```
failed to spawn
failed to spawn `{cmd}`
2026-08-19T23:50:01Z ERROR failed to spawn
```

A long static that is a prefix of the query has higher coverage than a holed template that only explains the inner string. Span mode was built so timestamps are leftover on the *query*; it also lets a no-hole prefix of the *whole* query win.

```
$ rg -n -g '*.ts' 'Event id|Duplicate' fixtures \
    | ./invert --templates - 'Event id must not be empty or null when enqueueing evt-99'
events.ts:3:25: score=0.52 holes=0 via=full
  tmpl:  Event id must not be empty
  suffix=' or null when enqueueing evt-99'
```

Confident hit on a static that is only a prefix of what the user pasted. `--exact` refuses these; default does not.

---

## What survived

- pin unique tokens (kizu `seen_hunk_fingerprint`) do **not** hallucinate onto voidtrace/tenaoshi.
- pin emoji / CJK NFC paths round-trip.
- pin 900 KB file mint/resolve stays ~0.1s on a tiny tree.
- invert 7-hole full paste still binds (`score=1.12`).
- invert empty stream is honest; directories still refused.
- invert 10 MB does not OOM or hang.
- Both CLIs still `--help` / `--selftest` clean.

## Kill / keep

**Keep both. Mutate both. Do not rewrite in this pass.**

| tool | do not kill because | mutate toward |
| --- | --- | --- |
| pin | The object is still the token. Unique pins refuse the wrong language/tree. kizu split still needs this verb. | Ambiguous (do not emit 1.000 twice). Neighbor body must beat a leftover stub at the old path. Bind a repo/tree hint or refuse `--to` that does not exist. NFC-normalize paths. Truncated tokens fail closed. |
| invert | Stream + named holes + span is still the unfmt×sluice harvest. 7-hole and camera cases stand. | Prefix-of-holed-template. No-hole prefix must not outrank a hole that binds. rustc/compiler grammar is a *different* tool (or a refused stream). `--any` should stop printing. Concat remains a sibling mutation, not a patch. |

A one-line invert `sys.stdin.read()` → `buffer.read().decode("utf-8", "replace")` would hide the binary crash and would not touch any of the ranking failures. Not applied.
