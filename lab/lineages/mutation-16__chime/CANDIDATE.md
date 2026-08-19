# mutation-16 — chime

## Primitive

Name a locus; emit other loci whose path-condition is the **same stack**, or a **superset** (deeper nest, seed stack is an ordered prefix). Control-flow rhyme as a Unix verb: `chime file:line`, also spelled `chime --same-as file:line`.

## Why this might not exist

`when` answers "when does this line run?" `under` answers "what runs under this predicate snippet?" Reviewers actually point at a line and ask the third question: *what else is in this arm?* `when --group` clusters a diff by stack but you cannot address a cluster by a locus. `under --same-as` AND-matches snippets from the stack, so it is fuzzy containment, not identity, and it cannot say "exact arm" vs "deeper". Nothing is `comm(1)` for path-conditions.

Ancestor `when`'s own suggested mutation: invert to `when --same-as file:line` — the rhyme of *when*, not of tokens. Reverse lineage `under` left "lines that share *exactly* this stack" open.

Not leftover-name hunting, not inverse-dead-code, not format-string inversion, not snippet grep of `if`.

## How to run

```bash
./chime fixtures/nested.py:13 --exact --explain
./chime fixtures/nested.py:8 --group
./chime --same-as fixtures/nested.py:10 --exact
./chime fixtures/guards.rs:11 --explain
printf '13:return\n6:missing\n' | ./chime fixtures/nested.py:8 --tsv
./demo.sh
```

Python 3.10+, stdlib only. `./chime` is the CLI.

## Empirical transcript

### Before the improvement

See the next commit. v0.1: exact / prefix-superset rhyme, span collapse, `--same-as`.

## Dogfood targets

| target | what we asked |
| --- | --- |
| `kizu/src/git/parse.rs` | `chime parse.rs:60` — unquoted-form survivors vs quoted branch |
| `fixtures/nested.py`, `guards.rs`, `sample.swift` | exact arm, None-guard superset, try≠except, guard≠guard-else |

## Surprises

(filled after dogfood)

## Failures

(filled after dogfood)

## Suggested mutations

- Overlay an unapplied patch so `--diff` is the post-image.
- Cross-file rhyme of an identical condition stack (the same four givens in another parser).
- A TUI that paints a file by same / deeper / other relative to a pinned locus.

## Kill / keep

**Keep** if dogfood shows exact-arm vs deeper is a question `under --same-as` cannot ask. Kill if it collapses to "grep the stack dump."
