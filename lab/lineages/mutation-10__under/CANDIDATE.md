# mutation-10 — under

## Primitive

Name a predicate snippet; emit every locus whose current path-condition contains it. Reverse of `when` (candidate-20): `when` names a line and prints the stack, `under` names a condition and prints the lines.

The object is still a **condition stack**. The query is inverted.

## Why this might not exist

`rg` answers "where is this text." `when` answers "when does this line run." Reviewers and agents actually ask the other half: *what else runs under `isEnabled`? under `starts_with(b"a/")`? under the None-guard that no longer appears on the line?* Debuggers answer it dynamically for one pause. Nothing answers it statically as a Unix pipe.

The ancestor's own suggested mutation was this invert (`when --same-as`, address-by-path). This lineage kills "user names a line" as the primary verb.

Not leftover-name hunting, not inverse-dead-code, not format-string inversion.

## How to run

```bash
./under 'user.locked' fixtures/nested.py --explain
./under 'user.locked | can_delete' fixtures/nested.py
./under 'starts_with(a/)' fixtures/guards.rs --kind given
./under 'isEnabled' fixtures/sample.swift
printf '13:return\n34:drained\n' | ./under 'user.locked' fixtures/nested.py --tsv
./under 'can_delete' --diff fixtures/sample.diff --group
./demo.sh
```

Python 3.10+, stdlib only. `./under` is the CLI.

## Empirical transcript

### Before the improvement (commit `90006f8`)

Fixtures already inverted `when` correctly: `user.locked` hit `return "denied"` and not `return "drained"`; `isEnabled` skipped the Swift guard-else; `exists` as `--kind given` on `validate_execplan.py` listed the whole function after the file-exists early return.

Real repos lied about *which* predicate.

`./under 'Decision:' validate_execplan.py` matched the parent `if decision_section and len(...)` because token match treated `decision` as a prefix of `decision_section`. The actual `'Decision:' not in decision_section` warning was buried under two extra stacks.

`./under 'unknownID' EditPlanComposer.swift` hit `case .duplicateID` and `case .unknownSelectionUnitID` (`id` ⊂ `unknownID` ⊂ `unknownSelectionUnitID`) plus the real `if let unknownID`. `./under 'invalidRange'` hit `guard !range.isEmpty` (`range` ⊂ `invalidRange`).

`./under 'actual.has' compare.ts` listed both polarities: the `if (!actual.has(path)) continue` *and* the `given actual.has(path)` fallthrough. Same for `if !bytes.starts_with(b"a/")` under `starts_with(a/)`. A naive substring of the stack dump is the opposite of the question.

`kizu/src/git/parse.rs:59-60` (`let b_side = …`) under `--kind given 'a/'` was already the valuable invert of `when parse.rs:60`.

### After the improvement (this commit)

Matching requires an identifier boundary and treats leading `!` / `¬(P)` / `guard-else` as inverted frames.

```
$ ./under 'Decision:' skills/…/validate_execplan.py --explain
validate_execplan.py:102-103
  match  if 'Decision:' not in decision_section
  given  file_path.exists()
  if     decision_section and len(...) > 0
  if     decision_section.strip() != '[実装中に記入予定]' and ...
  if     'Decision:' not in decision_section
  here   errors.append(ValidationError("warning",
```

One locus. The Japanese-placeholder parent is still on the stack (it is in force); it is no longer the *match*.

```
$ ./under 'unknownID' EditPlanComposer.swift
  match  if unknownID = selections.keys.filter(...)   (L102)
$ ./under 'invalidRange' EditPlanComposer.swift
  match  case .invalidRange(let unitID, let start, let end, ...)
  here   return "invalid original range for unit …
```

`duplicateID`, `unknownSelectionUnitID`, and `range.isEmpty` are gone.

```
$ ./under 'actual.has' voidtrace/…/compare.ts
  match  given actual.has(path)
  given  expected.has(path)
  if     (!actualBytes || !expectedBytes || !actualBytes.equals(...))
```

The `if (!actual.has) continue` arm is no longer "under actual.has". `./under '!actual.has'` gets that arm.

```
$ ./under 'starts_with(a/)' --kind given kizu/src/git/parse.rs
parse.rs:59-60
  given  ¬(len<5+ 2)
  given  inner.is_multiple_of(2)
  given  bytes.starts_with(b"a/")
  given  bytes.get(b_prefix_start..)== Some(b" b/")
  here   let b_side = &bytes[b_prefix_start + 3..];
```

Same stack `when parse.rs:60` printed, reached by naming the condition instead of the line.

`sitbone/…/PresenceArbiter.swift` `under isEnabled` is still the body after `guard isEnabled else { return }`, not the else.

`./demo.sh` exits 0.

## Dogfood targets

| target | what we asked |
| --- | --- |
| `skills/execplan-manager/scripts/validate_execplan.py` | `--kind given exists`; `Decision:` |
| `skills/codebase-investigator/scripts/dep_graph.py` | `for` — inventory of loop stacks |
| `kizu/src/git/parse.rs`, `kizu/src/git/diff.rs` | `starts_with` / `a/` givens / `success` / `is_empty` |
| `sitbone/Sources/SitboneCore/PresenceArbiter.swift` | `isEnabled` vs `guard-else` |
| `tenaoshi/Engine/Sources/TenaoshiEngine/EditPlanComposer.swift` | `unknownID` / `invalidRange` |
| `voidtrace/tools/spec-check/src/compare.ts` | `actual.has` polarity |
| `fixtures/nested.py`, `guards.rs`, `sample.swift` | adversarial nesting |

Read-only on the real repos. Ugly fixtures live in `fixtures/`.

## Surprises

- Polarity is the whole game. A stack dump is not a path-condition: `guard-else isEnabled` and `given ¬(len<7)` *mention* the snippet and mean the opposite. The invert of `when` is unusable until those frames are treated as inverted.
- The valuable "under" on real Rust is the **survivors of an early-return**, not the `if` body. `under --kind given 'a/'` is the question `git diff -W` cannot ask.
- Token containment (`id` ⊂ `unknownID` ⊂ `unknownSelectionUnitID`) is how a reverse-`when` quietly becomes a worse `rg`. Identifier-boundary fold plus camel/snake split was the empirical fix, not a nicety.
- `under 'exists'` on a Python file-guard prints the rest of the function. That looks noisy and is the correct object: every later line runs *given the file exists*.

## Failures

1. **Inherited engine holes.** Nested-but-total early returns (quoted-path miss in `parse.rs`), `if let` dropping `let`, `len<5+ 2` spacing, empty Rust match-arm preds — same as `when`.
2. **Brace-only lines.** Spans still surface a closing `}` as a representative `here`.
3. **`--diff` of an unapplied patch** maps `+` onto the working tree (sample.diff `audit.block` becomes `return "denied"`). Same hole as `when`.
4. **`under 'for'`** matches every loop. A kind-name as a snippet is legal and usually the wrong question.
5. **`if not P` vs `!P`.** Python `if not user.can_delete` stays a *written* predicate (`can_delete` still hits it). Rust/JS `!P` is treated as inverted. The split is intentional and easy to miss.
6. **`unknownID` body.** The `if let unknownID` span is the header line; the throw sits on the same two-line span. Fine here, luck of the engine.

## Suggested mutations

- Overlay an unapplied patch so `--diff` is the post-image.
- Infer `given ¬(P)` for fully-exiting nested ifs (quoted-form miss).
- Default `--payload`: hide `}`, `else:`, and eval-only headers.
- A TUI that paints every line of a file by whether it is under the named predicate.
- `under --same-as` as the only input (drop the snippet) is already implemented; a "lines that share *exactly* this stack" mode is still open.

## Kill / keep

**Keep.** The invert is a real verb: `when parse.rs:60` and `under --kind given 'a/'` are the same object approached from opposite ends, and the second is the one you type when you do not yet know the line. Kill only if a later generation reduces it to "grep the `if` condition and print the body."
