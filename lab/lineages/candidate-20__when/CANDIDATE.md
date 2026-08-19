# candidate-20 — when

## Primitive

Path-condition at a source locus: given `file:line` (or a diff, or grep output), emit the nested predicates still in force — *when this line runs* — including fallthrough `given` frames from early-return guard clauses.

The object is a **condition stack**, not a function name and not a hunk window. The verb is the missing question-word next to `whatis` / `which` / `whereis`.

## Why this might not exist

Reviewers reconstruct enclosing `if` / `try` / `match` / `guard` by scrolling. `git diff -W` and `diff -p` only name the function. Unified hunks are line-windows; the `if` that makes a change legal is often 40 lines above the `@@` header. Debuggers answer "when" dynamically. Nothing answers it statically as a Unix pipe.

Private list of four primitives; discarded the two most conventional:

1. **hitch** — hidden coupling via shared literals + co-change. Discarded: shotgun-surgery / CodeScene.
2. **rumor** — caller beliefs vs callee testimony. Discarded: type/error analysis.
3. **rhyme** — control-flow skeleton groups (not chosen).
4. **when** — path-condition at a locus (implemented).

Not leftover-name hunting, not inverse-dead-code, not format-string inversion, not ghosts of deleted identifiers.

## How to run

```bash
./when fixtures/nested.py:13 --explain
./when --diff fixtures/sample.diff --group
printf '13:return\n' | ./when fixtures/nested.py --tsv
rg -n 'return None;' /path/to/file.rs | ./when /path/to/file.rs --tsv
./when --git --group
./demo.sh
```

Python 3.10+, stdlib only. `./when` is the CLI.

## Empirical transcript

### Before the improvement (commit `a511246`)

Python on `skills/execplan-manager/scripts/validate_execplan.py:102` already worked:

```
in     validate_execplan(file_path)
if     decision_section and len(...) > 0
if     decision_section.strip() != '[実装中に記入予定]' and ...
if     'Decision:' not in decision_section
here   errors.append(ValidationError("warning",
```

Real Rust did not. `kizu/src/git/parse.rs:60` (`let b_side = ...`) — a line that is only legal after four early-return checks:

```
in     parse_diff_git_header(rest:&str)-> Option<PathBuf>
here   let b_side = &bytes[b_prefix_start + 3..];
engine braces  depth=1
```

`kizu/src/git/diff.rs:51` missed the two guards above it (`success`, `raw.is_empty()`). Predicates lost string literals (`bytes.starts_with(b)` instead of `b"a/"`).

`rg -n 'return None;' parse.rs | ./when --tsv` printed **nothing**: single-file rg emits `LINE:text`, and the parser demanded `FILE:LINE:text`.

`tenaoshi/.../EditPlanComposer.swift:70` attributed a return to the **first** `case .blankUnitID` instead of `.invalidRange` (new `case` ignored once a case was on the stack). `:103` invented a fake `try` frame that swallowed half the function (`try` in Swift is not a block).

`stratal` is an empty git repo (no source). Logged and skipped.

### After the improvement (this commit)

Same Python locus now also reports the file-exists guard as a fallthrough given:

```
in     validate_execplan(file_path)
given  file_path.exists()                          (L54)
if     decision_section and len(...) > 0
if     decision_section.strip() != '[実装中に記入予定]' and ...
if     'Decision:' not in decision_section
here   errors.append(...)
```

`kizu/src/git/parse.rs:60`:

```
in     parse_diff_git_header(rest:&str)-> Option<PathBuf>
given  ¬(len<5+ 2)
given  inner.is_multiple_of(2)
given  bytes.starts_with(b"a/")
given  bytes.get(b_prefix_start..b_prefix_start+ 3)== Some(b" b/")
here   let b_side = &bytes[b_prefix_start + 3..];
depth=5
```

`kizu/src/git/diff.rs:51`:

```
given  output.status.success()
given  raw.is_empty()
if     is_untracked_and_visible(root,rel)?
```

`rg -n 'return None;' parse.rs | ./when parse.rs --tsv` now emits one row per return, each with its own condition stack (quoted-branch vs length-guard vs `b/` separator vs quoted-token loop).

`tenaoshi` `:70` is `case .invalidRange(let unitID, let start, let end, ...)`. `:103` is `if unknownID = selections.keys.filter(...).first` — no phantom `try`.

`sitbone/.../PresenceArbiter.swift:81` (after `guard isEnabled else { return }`):

```
in     detect() async -> PresenceReading
guard  isEnabled
here   let active = readings.filter { ... }
```

`voidtrace/tools/spec-check/src/compare.ts:84`:

```
for    (const path of allPaths)
given  actual.has(path)
given  expected.has(path)
if     (!actualBytes || !expectedBytes || !actualBytes.equals(expectedBytes))
```

`./demo.sh` exits 0.

## Dogfood targets

| target | what we asked |
| --- | --- |
| `skills/execplan-manager/scripts/validate_execplan.py` | nested if + Japanese string + exists-guard |
| `skills/codebase-investigator/scripts/dep_graph.py` | triple-for + if |
| `kizu/src/git/parse.rs`, `kizu/src/git/diff.rs` | Rust early-return parser |
| `sitbone/Sources/SitboneCore/PresenceArbiter.swift` | Swift `guard` + `switch` |
| `tenaoshi/Engine/Sources/TenaoshiEngine/EditPlanComposer.swift` | `if let` + associated-value `switch` |
| `voidtrace/tools/spec-check/src/compare.ts` | TS try/for + empty-check guards |
| `stratal` | empty repo — no source |
| `fixtures/nested.py`, `guards.rs`, `sample.swift`, `sample.rs`, `contradict.py` | adversarial nesting |

Read-only on the real repos. Ugly fixtures live in `fixtures/`.

## Surprises

- The valuable "when" on real Rust is **not** the nested `if`. It is the **negation of the last four early returns**. Guard-clause style makes `git diff -W` almost useless: the function name is known, the surviving predicates are not.
- Swift `guard` is the explicit spelling of the same object. Once `given` existed, `guard` became the same frame with a keyword.
- `rg FILE` omitting the filename is a real pipeline footgun. The fix (`LINE:text` + a FILE operand) is part of the interaction model, not a nicety.
- Unapplied patches (`--diff fixtures/sample.diff`) look up *working-tree* line numbers. Lucky when the insert is in the same arm; lying otherwise.

## Failures

1. **Nested-but-total early returns.** `parse.rs` quoted-path `if bytes.starts_with(b"\"a/") { ... several ifs ... return Some }` is *not* turned into `given ¬(quoted form)` at line 60, because the simple-exit heuristic refuses nested `if`. Conservative miss.
2. **Token spacing.** `len<5+ 2` instead of `len < 5 + 2`.
3. **`if let` pred drops `let`.** `if unknownID = ...` not `if let unknownID = ...`.
4. **Match arm predicates** in Rust are often empty (`arm` with no pattern text).
5. **`--diff` of an unapplied patch** maps `+` lines onto the current file, not the post-image.
6. **`stratal`** has no tracked source.
7. **Brace `try`/`do` without `{`** is now ignored (correct for Swift `try foo()`), so Python-style is the only precise `try`.

## Suggested mutations

- Overlay an unapplied patch in memory so `--diff` is the post-image.
- Infer `given ¬(P)` for fully-exiting *nested* ifs (the quoted-form miss).
- Address a locus as a condition path (`when 'fn parse_header | given starts_with(a/)'`) and jump back to today's line numbers — durable-pin adjacent, but the object is the path-condition.
- Invert: `when --same-as file:line` lists other lines that share the stack (the rhyme of *when*, not of tokens).
- Feed `when --group` into a review TUI (kizu hunks tagged by condition).

## Kill / keep

**Keep.** The object (path-condition + fallthrough `given`) is small, pipeable, and changed what we could say about real kizu/sitbone/tenaoshi lines. Kill only if a later generation reduces it to "print the enclosing function."
