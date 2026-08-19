# hybrid-07 — dowel

## Primitive

A **dowel** is a contract token: template fingerprint + the hole names that bound + the locus they sat in. Mint once. Resolve later: current `path:line` **and** whether those same holes still bind.

## Why this might not exist

pin (mutation-22) mints a durable locus and refuses to take `path:line` on resolve. invert/stump bind a paste against templates in a stream and name the holes. Developers who have both still have two reports.

`pin | invert` is the conventional hybrid and the wrong object. pin relocates a source line and is silent on hole names. invert binds whatever names live in dest *now* and does not remember that the hole used to be `{uid}`. A leftover wrapper plus a basename clone that kept `{uid}` makes pin land on the clone at 1.000. invert, handed the dest file, prints `{user_id}=42`. Neither says: *the extracted body is the seat, and the contract renamed.*

The object changed. Seating uses the template's static parts plus locus (path, neighbors, stem-split). Hole names are assayed **after** the seat is chosen — a clone that kept the old names cannot hide a rename at the extracted body.

Discarded as concatenation: store a pin next to an invert query; invert the dest file pin found.

## How to run

From the worktree root:

```bash
chmod +x ./dowel
./dowel --selftest
./demo.sh
./dowel mint --repo /path --from <old-sha> path:line 'runtime instance'
./dowel resolve --repo /path --to HEAD dowel1.…
./dowel show dowel1.…
```

Python 3.10+, git. Exit 0 on success. `resolve` exits 2 if you hand it a `path:line`. Missing `--from`/`--to` refs exit 2 (`unknown ref`). Corrupt / truncated tokens exit 1 with no result row. Origin mismatch exits 1 unless `--any-repo`. `--strict` also fails on `unbound` / `gone` / `ambiguous`.

## Empirical transcript

### v0.1 working prototype

`./dowel --selftest` → `selftest: ok`

`./demo.sh` → all checks passed.

The money shot is not "we found the line." pin on the same fixture:

```
pin:    moved   src/user.py:4  →  src/legacy/user.py:2   1.000
dowel:  renamed src/user.py:4  →  src/user/messages.py:4  0.834  {uid}→{user_id}; skipped basename bait
invert: {user_id} = 42
```

pin sat on the clone that kept the old identifier. invert bound dest names and forgot `{uid}`. dowel seated the extracted body (stem-split) and assayed the contract.

Other fixture rows:

```
shifted  src/user.py:10 → src/user/messages.py:10  {cmd} still binds
unbound  src/user.py:7  → src/user/messages.py:7   dropped {port}; drifted {host}
seated   identity at v2, unicode café.py, spaced filename, js two-hole
```

Dropped `{port}` is not invert's silent `{host}=db.internal:5432`. rustc `--> src/git/revert.rs:46:18` refused at mint. Clipped token fail-closed. Missing `--to` is `unknown ref`, not `gone`. Foreign repo refused.

Real trees, v0.1 (HEAD identity):

```
kizu     src/git/parse.rs:171     seated  {rest}=a/foo b/foo
kizu     src/git/diff.rs:34       seated  {1}=fatal: not a git repository
sitbone  SitboneCore.swift:554    seated  7 holes (oldPhase…awayRecovered)
sitbone  SitboneCore.swift:361    seated  {self.isCameraEnabled}=enabled
voidtrace event-queue.ts:65       seated  {this.#processedTimeMs}, {snapshot.timeMs}
```

### Dogfood that v0.1 left on the table

Historical kizu split (`3b3e0a9^` `src/git.rs:609` → HEAD `src/git/parse.rs:171`) already **shifted** with `{rest}` still bound — that is the joint working.

Truncated sitbone paste (`idle=12s` without `deserted=…`) minted the four bound holes, then printed:

```
truncated:  deserted= driftRecovered={counters.driftRecovered.value} awayRecovered=…
```

The next hole `{counters.deserted.value}` was swallowed because a prefix match on `s deserted=` counted as "that literal bound," so the following hole was treated as already consumed. A remainder that lies is the same class of bug stump killed in invert.

Leftover `src/user.py` (no template) never entered the exact-copy list, so the rename row named the basename bait and stayed mute on the stub. kizu's split left `src/git.rs` standing without `{rest}` — same mute.

`--instance 'user 99'` first reported `unbound` (value-matched the rename against the stored `42`). Fixed in-tree before demo 0 by matching rename **in position**, not by stored values.

### After the improvement (v0.2)

Remainder starts at the unmatched literal tail **and** names the next unbound hole. Old path with no holed template is recorded as `leftover stub` even when it was never a seating candidate.

```
$ ./dowel mint --repo sitbone --from HEAD SitboneCore.swift:554 \
    'transition focused → idle reason=timeout idle=12s'
  bound:  {oldPhase.rawValue}, {newPhase.rawValue}, {reason.name}, {idle}
  truncated:  deserted={counters.deserted.value} driftRecovered=… awayRecovered=…
$ ./dowel resolve --to HEAD   # seated; contract is those four names

$ ./dowel mint --repo kizu --from 3b3e0a9^ src/git.rs:609 \
    'unparseable `diff --git` header: a/foo b/foo'
$ ./dowel resolve --repo kizu --to HEAD
shifted  src/git.rs:609  →  src/git/parse.rs:171  {rest}  leftover stub src/git.rs

$ ./dowel mint --repo tenaoshi --from HEAD AnthropicMessagesClient.swift:86 \
    'Anthropic APIがHTTP 429を返した: rate limited'
seated  {http.statusCode}=429  {detail}=rate limited
```

`./demo.sh` still 0, now including cases 25–27.

## Dogfood targets

- Synthetic ugly git repo: leftover stub + `src/user/messages.py` rename + `src/legacy/user.py` bait; dropped `{port}`; spawn move; unicode; spaces
- Destroyer-shaped: missing `--to`, truncated token, rustc locator, foreign repo
- `/Users/annenpolka/ghq/github.com/annenpolka/kizu` — HEAD `{rest}` / `{1}`, and `git.rs:609@3b3e0a9^` → `parse.rs:171`
- `/Users/annenpolka/ghq/github.com/annenpolka/sitbone` — 7-hole Logger, camera nested quotes, truncated 7-hole mint
- `/Users/annenpolka/ghq/github.com/annenpolka/voidtrace` — two-hole enqueue
- `/Users/annenpolka/ghq/github.com/annenpolka/tenaoshi` — `Anthropic APIがHTTP {http.statusCode}を返した: {detail}`

## Surprises

- Seating must not use hole names. The clone that kept `{uid}` wins any score that mixes names into identity. Stem-split before neighbors is load-bearing: a rename at the body (`def report(user_id)`) *lowers* neighbor score against the minted `def report(uid)`.
- pin v0.3's leftover-stub rule is not enough here. The leftover has **no** template, so it is not a candidate. The thief is the basename clone that still *is* the old template. That is why this is not pin.
- invert on the dest file is not enough either: it cannot say `uid→user_id`. The token is the memory.
- Truncated mint is a smaller contract (4 of 7 names). Resolve against the full dest template is still **seated** — extra dest holes are not a break of a contract that never claimed them.

## Failures

- v0.1 remainder after a truncated 7-hole omitted the next hole. Fixed: prefix-of-literal is not a bound hole.
- Whole-tree dest scan on resolve. kizu/sitbone/voidtrace are cheap; linux.git is not.
- `--any-repo` still lands a common `user {uid}` helper on a stranger.
- Adjacent concatenation (`"open " + path`) is still not one template.
- Dynamic format strings remain invisible.
- v1 tokens only. No pinfile registry.

## Suggested mutations

- `dowel watch`: rewrite a dowelfile onto HEAD as the tree moves.
- Reconstruct a *chain* of templates from `truncated:` remainder (stump's suggested mutation, now with a stored contract).
- Mint from a grep stream (`rg | dowel mint`) without a locator, recording each hit as its own token.

## Kill / keep

**Keep.** The object changed. Demo case 1 is a tree on which pin wheat is `legacy/user.py` at 1.000, invert wheat is `{user_id}=42`, and dowel wheat is `messages.py` + `{uid}→{user_id}`. Historical kizu `git.rs` → `parse.rs` keeps `{rest}`. Kill only if a later generation proves that "pin the line, then invert the dest file, then diff hole names by hand" recovers the contract — it does not, because pin does not sit on the extracted body when a same-static clone exists.

## What the flipped assumption bought and lost

**Bought**

- A stored binding schema, not a stored line and not a stored search.
- Rename is a first-class verdict.
- Dropped holes are unbound, not a quieter invert hit.
- Stem-split seating survives a neighbor-identifier rename.

**Lost**

- No-hole templates cannot mint (use pin).
- Compiler diagnostics as instances are refused.
- You must have an instance at mint time. A locus without a binding is a pin, not a dowel.
