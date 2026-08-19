# hybrid-01 — moor

## Primitive

A log line is an *instance*: re-bind it, in one pass, to a current `path:line` and to the format-string holes that produced it, letting the stale locator and the interpolated text corroborate.

## Why this might not exist

Yesterday's CI log is full of two lies at once. `src/app.rs:529` no longer exists (the file split). `git diff single file failed: fatal: not a git repository` is not a grep-able literal (a `{}` ate the tail). Developers already have two tools for the two lies: relocate the address (`slip`), invert the string (`unfmt` / `sluice`). Piping one into the other is the conventional hybrid and it is the wrong object.

The object is the **instance**. The locator is a hint for which template; the filled-in text is a hint for which line. A test file that asserts the exact runtime string will beat the production template on raw inverse-printf. A rustc diagnostic has no project template at all, but it *names* the identifier sitting on the slipped line. Neither parent sees that agreement. The missing Unix verb is: **moor the instance to its current berth and unpack its cargo.**

Discarded as concatenation: `slip | unfmt`, or unfmt-on-HEAD then slip the hit. That is two scores, never a joint.

## How to run

From the worktree root:

```bash
chmod +x ./moor
./moor --selftest
./demo.sh
./moor --repo /path --from <old-sha> --to HEAD < ci.log
./moor --from-dir old/ --to-dir new/ --porcelain 'src/auth.py:5: user 42 not found'
```

## Empirical transcript

### v0.1 working prototype

Synthetic ugly repo (format strings + file split + exact test-literal decoy + unicode/colon/spaces + nested git) plus real kizu / sitbone / tenaoshi.

```
$ ./moor --selftest
selftest: ok

$ ./moor --repo $UGLY --from $V1 --to $V2 --porcelain \
    'src/auth.py:5: user 42 not found'
bound  src/auth.py:5  src/users/lookup.py:5:24  user {uid} not found  uid=42  via=joint
```

The decoy `tests/test_auth.py` holds the exact literal `user 42 not found` (raw score 1.0). Production is `user {uid} not found` (raw ~0.83). unfmt-alone would keep the test. Moor's locator proximity after the split (`src/auth.py` → `src/users/lookup.py`) flips the bind.

```
$ cat log.txt
ERROR src/auth.py:5 user 42 not found
thread 'git::diff' panicked at src/git.rs:2:12:
git diff single file failed: boom
  File "src/auth.py", line 5, in find_user
KeyError: user 42 not found

$ cat log.txt | ./moor --repo $UGLY --from $V1 --to $V2
ERROR src/users/lookup.py:5 user 42 not found  ⟦… user {uid} not found  uid=42⟧
thread 'git::diff' panicked at src/git.rs:2:12:
git diff single file failed: boom  ⟦… git diff single file failed: {}  0=boom⟧
  File "src/users/lookup.py", line 5, in find_user
KeyError: user 42 not found  ⟦… user {uid} not found  uid=42⟧
```

kizu mixed CI log, one pass (file-split locators **and** the anyhow hole):

```
$ cat kizu-log.txt | ./moor --repo kizu --from b4e6a5d --to HEAD
error[E0599]: no method named seen_hunk_fingerprint
  --> /home/runner/work/kizu/kizu/src/app/layout.rs:17:5
  File "src/app/navigation.rs", line 22, in nearest_landing_forward
thread 'git::diff' panicked at src/git/diff.rs:34:28:
git diff single file failed: fatal: not a git repository …  ⟦src/git/diff.rs:34:28  git diff single file failed: {}  0=fatal: …⟧
```

sitbone / tenaoshi (no locator, template-only berth):

```
$ ./moor --repo sitbone --porcelain 'session started profile=DeepWork'
matched  -  SitboneCore.swift:423:33  session started profile={self.activeProfile.name}  self.activeProfile.name=DeepWork

$ ./moor --repo sitbone --porcelain \
    'cumulative save failed path=/tmp/c.json error=disk full'
matched  -  JSONSessionStore.swift:45:36  cumulative save failed path={…} error={…}

$ ./moor --repo tenaoshi --porcelain \
    'has_more cannot be true when units is empty'
matched  -  EditPlan.swift:260:43  has_more cannot be true when units is empty
```

tenaoshi's engine source is untracked; dest worktree includes untracked by default (the unfmt v0.2 lesson, kept).

### Failures that drove v0.2

A mixed log already using **today's** path, pointed at `--from b4e6a5d` (the SHA that does not contain `layout.rs`):

```
$ printf 'error src/app/layout.rs:17: no method named seen_hunk_fingerprint\n' \
    | ./moor --repo kizu --from b4e6a5d --to HEAD     # v0.1
error src/app/layout.rs:17: no method named seen_hunk_fingerprint
```

Nothing moored. Locators were bound only against the *from* snapshot, so a dest-only path was invisible. The rustc record `error[E0599]: no method named seen_hunk_fingerprint` + `--> src/app.rs:529:5` *did* relocate (`layout.rs:17`) but left the method name unbound: rustc diagnostics are not project format strings, so the unfmt kernel had nothing to invert.

### After the improvement (v0.2)

Parse locators against the union of both snapshots. A dest-only path is already current (`same`). When no format template matches, a compiler-diagnostic name that also lives on the dest line is a hole.

```
$ ./moor --repo kizu --from b4e6a5d --to HEAD --porcelain <<'EOF'
error[E0599]: no method named seen_hunk_fingerprint
  --> src/app.rs:529:5
EOF
bound  src/app.rs:529  src/app/layout.rs:17:5  no method named {}  0=seen_hunk_fingerprint  via=ident

$ printf 'error src/app/layout.rs:17: no method named seen_hunk_fingerprint\n' \
    | ./moor --repo kizu --from b4e6a5d --to HEAD --rewrite --annotate
error src/app/layout.rs:17: no method named seen_hunk_fingerprint  ⟦src/app/layout.rs:17  no method named {}  0=seen_hunk_fingerprint⟧
```

`./demo.sh` → `passed=25 failed=0` (includes dest-only fixture path, kizu ident bind, sitbone 2-hole flatten, tenaoshi untracked).

## Dogfood targets

| Target | What we threw at it |
| --- | --- |
| synthetic `ugly` (demo.sh) | split+rename, test-literal decoy, panic record, traceback record, rustc `-->`, from-dir/to-dir, unicode/colon/spaces, nested git |
| `/Users/annenpolka/ghq/github.com/annenpolka/kizu` | `b4e6a5d` `app.rs` split 529→`layout.rs:17` / 543→`navigation.rs:22`; anyhow `git diff single file failed: {}`; dest-only `layout.rs`; rustc ident hole |
| `/Users/annenpolka/ghq/github.com/annenpolka/sitbone` | Swift `\(` + `privacy:`; multiline `"""` `cumulative save failed`; 3-hole `session saved key=` |
| `/Users/annenpolka/ghq/github.com/annenpolka/tenaoshi` | untracked `EditPlan.swift` `has_more cannot be true when units is empty` |
| `/Users/annenpolka/ghq/github.com/annenpolka/voidtrace` | `Duplicate event ID: {snapshot.id}` → `evt-abc` (ad-hoc, not in demo.sh) |

## Surprises

- The test-literal decoy is the proof that this is not `unfmt | slip`. Raw inverse-printf *correctly* prefers the exact string. The instance is only recovered when the stale locator is allowed to vote.
- `--records auto` is load-bearing. slip rewrites the `-->` line; unfmt matches the next line; neither notices they are one observation.
- rustc diagnostics looked like a miss for the unfmt kernel and a win for slip. They are actually the cleanest ident-hole: the diagnostic *is* a template (`no method named {}`) whose value must live on the dest line or the bind is a lie.
- dest-only paths against an old `--from` are the mixed-SHA log nobody writes a test for and everyone pastes.
- sitbone's hole *names* (`self.cumulativeURL.path`, `error.localizedDescription`) survive flattening and are more useful than `{}` `{}`.

## Failures

- Adjacent concatenation (`"open " + path + ": " + err`) is still not a template.
- Interpolated tail only (`fatal: not a git repository…`) still does not find `git diff single file failed: {}` without the static prefix.
- Shared-ident fallback can tag a traceback `in nearest_landing_forward` as `⟦{}  0=nearest_landing_forward⟧`. Correct, a bit loud.
- rustc diagnostics that do not name a token on the dest line stay `relocated` (no hole).
- Whole-tree index of kizu (e2e fixtures included) is acceptable but not free; no incremental cache.
- No stitching of anyhow *chains* (`context` + inner) into one instance.

## Suggested mutations

- `moor mint`: store `(template, hole values, line fingerprint)` instead of `file:line@sha` so a ticket survives the next split.
- Reconstruct an error as an ordered chain of moored instances.
- Prefer templates whose span covers the grepped / slipped line when a file has many strings (kizu `format!` vs `anyhow!` on neighboring lines).
- Coverage / SARIF rewrite: moor every `file:line` *and* keep the bound test name.
- `--watch` a pinfile of instances across HEAD movement.

## Kill / keep

**Keep.** The object changed. The demo has a case (exact test literal vs production template) that neither parent gets right, and a kizu CI log that is simultaneously a file-split problem and an inverse-printf problem and is now one filter. v0.2 came from a real mixed-SHA miss, not from a feature list. Kill only if a later generation proves that pins-as-objects (`moor mint`) is the actual primitive and this stream is just the renderer.
