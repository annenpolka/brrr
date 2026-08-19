# candidate-19 — folk

## Primitive

Mine a repository's *folk protocols* — unwritten call-pair handshakes — from path-sensitive sequences, then emit the half-pairs as a Unix table.

The new object is not "a function" or "a name" or "a deleted identifier". It is **a calling convention nobody wrote down**.

## Four primitives considered

1. **assume** — usage-inferred contracts as `comm`-able tables. Discarded: conventional type inference.
2. **shadow** — unexplored argument-combination space of live functions. Discarded: combinatorial testing / pairwise, already a product category.
3. **folk** — inverse-shaped call-pair protocols + path-sensitive orphans. **Implemented.**
4. **schism** — modules whose callers form disjoint API-usage clusters. Unusual, not implemented; a later mutation.

## Why this might not exist

Developers already have RAII linters for *known* pairs (`lock`/`unlock` if you teach the tool). They do not have a command that **learns the repo's own pairs** (`beginConfiguration`/`commitConfiguration`, `set_var`/`remove_var`, `push_back`/`pop_front`) and then asks which paths broke them.

The recurring workflow this collapses: grep for `begin_`, mentally invert the name, grep for the other half, then stare at every `if` to see if both sides run.

## How to run

From the worktree root:

```
./folk --pairs fixtures/toy
./folk --orphans fixtures/toy
./folk --check fixtures/toy          # exits 1
./folk --of beginConfiguration /Users/annenpolka/ghq/github.com/annenpolka/sitbone/Sources
./demo.sh
```

## Empirical transcript

### Before the improvement (v0.1: statistical collocation + no inline)

Toy (`fixtures/toy`): 3 files, 53 functions, **14 pairs, 16 orphans**. Real leaks were found (`forgotten_commit`, `leaked_lock`, `connectLeaked`) *and* drowned in collocation:

- `lock`/`work` and `lock`/`mutate` mined as protocols, then reported as orphans across languages (Rust `lock`/`work` condemned Python `lock()`).
- `attach`/`run`, `connect`/`handshake` scored 1.000 because they always sit next to the real handshake.

Real repos:

| repo | files | pairs | orphans | what happened |
| --- | ---: | ---: | ---: | --- |
| sitbone/Sources | 23 | 6 | 4 | one true pair (`beginConfiguration`/`commitConfiguration`); false `decode`/`encode`, `fileExists`/`Data` |
| kizu/src | 69 | 66 | 714 | `Vec.push` vs `pop`, `handle_key`/`key`, Swift-style noise in Rust tests |
| tenaoshi Engine+Shell | 30 | 81 | 240 | SwiftUI `Text`/`font`/`padding` chains; `let` tokenized as a call |
| voidtrace packages+apps+tools | 79 | 89 | 915 | commander `command`/`action`, jest `toThrowError`/`objectContaining` |
| skills | 2 | 0 | 0 | only two Python scripts; no inverse pairs |
| stratal | 0 | — | — | empty checkout |

### After the improvement (v0.2)

Changes driven by those failures, not by taste:

- default to **inverse-shaped** pairs only (`--stat` opt-in)
- **language-scoped** mining (no more Rust `lock` orphaning Python `lock`)
- keywords (`let`, `return (`, `await`) are never calls
- generic inverses (`push`/`pop`, `encode`/`decode`) require a shared receiver *and* score ≥ 0.35
- one-level inline of callee *must* protocol-moves; do not inline A if the callee only sometimes does A's inverse (LRU `push_back` / overflow `pop_front`)
- skip thin wrappers (`def setup_tx(): begin_tx()`) as orphan sites
- lexical pairs use a wide gap (128) so `set_var` … 20 calls … `remove_var` still counts

Toy: **9 pairs, 8 orphans**. Every orphan is a planted leak. `wrapped_orphan` is visible only after inline (`setup_tx()` without `teardown_tx()`). `lock`/`work` is gone.

```
$ ./folk --orphans fixtures/toy
# forgotten_commit / conditional_commit / leaked_lock
# wrapped_orphan (begin_tx + setup_tx)
# connectLeaked / attachOnly / dangling_start
```

Real repos, second pass:

| repo | pairs | orphans | note |
| --- | ---: | ---: | --- |
| sitbone/Sources | **1** | **0** | `beginConfiguration`/`commitConfiguration` on `session`, both paths commit (including the device-init failure path). Handshake held. |
| kizu/src | **2** | **0** | `set_var`/`remove_var` together=7 score=1.000; `push_back`/`pop_front` together=3 same_recv=3. Both honored. |
| tenaoshi | 0 | 0 | no inverse handshake left after `Set`/`remove` (constructor) was rejected |
| voidtrace | 0 | 0 | no inverse-shaped pairs in that style |
| skills | 0 | 0 | still too small |

sitbone excerpt that made the primitive feel real:

```
# Sources/SitboneSensors/CameraFrameProvider.swift
session.beginConfiguration()
guard let device = … else {
    session.commitConfiguration()   # still paired on the failure path
    return
}
…
session.commitConfiguration()
```

`./folk --pairs --of beginConfiguration` prints one line, score 1.000, same_recv=2.

## Dogfood targets

- `/Users/annenpolka/ghq/github.com/annenpolka/sitbone` (read-only)
- `/Users/annenpolka/ghq/github.com/annenpolka/kizu/src` (read-only)
- `/Users/annenpolka/ghq/github.com/annenpolka/tenaoshi/{Engine,Shell}/Sources` (read-only)
- `/Users/annenpolka/ghq/github.com/annenpolka/voidtrace/{packages,apps,tools}` (read-only)
- `/Users/annenpolka/ghq/github.com/annenpolka/skills` (read-only)
- `/Users/annenpolka/ghq/github.com/annenpolka/stratal` (empty)
- `fixtures/toy` (planted protocols + leaks)
- `fixtures/ugly` (spaces, 日本語, broken parse, skipped `generated/`)

## Surprises

- The first *true* hit was not `lock`/`unlock`. It was AVFoundation's `beginConfiguration`/`commitConfiguration` in sitbone, which folk learned from morphology (`begin*`/`commit*` + shared remainder + same receiver) with **zero annotations**.
- kizu's tests already treat `set_var`/`remove_var` as a handshake (they even comment about not interleaving them). folk recovered that comment as a table row.
- Statistical collocation is almost always a fluent/builder chain, not a protocol. `--stat` is a research flag, not a default.
- Inlining `push_back` out of an LRU `insert` created false orphans. The rule that saved it: **do not promote A if the callee only sometimes does A's inverse.**

## Failures

1. **v0.1 cross-language leakage.** Rust `lock`/`work` condemned Python `lock()`. Fixed by scoping pairs to a language.
2. **v0.1 `let` as a call.** Swift `let (data, _) = session.data(...)` became a protocol member. Fixed: `NEVER_CALL`.
3. **v0.1 SwiftUI / commander / jest floods.** 81–89 pairs of modifier chains. Fixed: drop statistical default.
4. **`Set(` / `remove`.** PascalCase constructor `Set` stemmed to verb `set`, inverse of `remove`. Fixed: reject constructorish names.
5. **`Vec.push` vs `pop`.** Lexical inverse, almost never a handshake. Fixed: generic inverses need same receiver + score ≥ 0.35.
6. **`max_gap=8` hid real pairs.** kizu `set_var` … bootstrap … `remove_var` is 20+ calls apart. Fixed: lexical gap 128.
7. **LRU 0-iteration `while`.** `push_back` then `while over_cap { pop_front }` looks like a conditional orphan. Mitigated for generic inverses; still a CFG lie for non-generic loops.
8. **skills / voidtrace / tenaoshi / stratal produced no keepers after the filter.** Either no inverse handshakes, or they live in macros / cross-file state machines folk cannot see.
9. **TS function regex is greedy** (`ident(`), so voidtrace reports thousands of "functions". Harmless once statistical mining is off; still slow-ish.
10. **Ugly `broken.py`:** syntax error printed to stderr, file skipped. Correct, but there is no structured parse-error stream.

## Suggested mutations

- Interprocedural depth 2 + "protocol moves" as first-class events on a call graph, not just one-level splice.
- Same-receiver typed a little harder (`session.beginConfiguration` vs any `commitConfiguration`).
- `--pin protocols.tsv` / `folk check` against a committed protocol file (durable pin of a handshake).
- **schism** mode: cluster a module's callers by which protocol halves they use.
- Teach loops "B is optional cleanup" vs "B must run" via the loop condition (`len > cap` vs unbounded).
- Go `defer f.Close()` after `os.Open` as a first-class pair even when names are `Open`/`Close` on different receivers (`f` vs `os`).

## Kill / keep

**Keep.** The v0.1 flood looked like a linter. The v0.2 object is sharp: a repo-specific handshake table with almost no false pairs on sitbone and kizu, plus a planted-leak fixture that the inline pass actually needed.

Kill `--stat` as a default forever. Mutate toward pinned protocol files and deeper inlining, not toward more collocation.
