# CANDIDATE: owes

```yaml
origin:
  method: hdd
  trial: hdd-agent
```

## Primitive

Given a working-tree change (unified diff, or before/after snapshots) and
the remaining tree, list obligations written elsewhere that the change
appears to break:

- identifiers removed on minus lines that remaining files still mention
- required companion files named by remaining docs that do not exist

Classification: USEFUL_COMPOSITION. Nearest existing operation is `git diff`
plus `rg` through docs/tests. The observable delta is that a missing
companion artifact named by remaining docs is a first-class miss tied to
the change, not only a hunk list.

## Why it might not exist

Diff tools stop at the hunk list. Repo linters encode one project's rules.
`owes` is the small composition: parse what the change removed, then ask
the remaining tree whether it still owes that name or that file. It does
not invent CVEs, tickets, or rationale.

## How to run

```bash
./owes fixtures/deleted-fn
./owes fixtures/missing-companion
./owes fixtures/clean
./owes --tree fixtures/deleted-fn/tree --diff fixtures/deleted-fn/change.diff
./owes --json fixtures/deleted-fn
./demo.sh
python3 tests/test_owes.py -v
```

Python 3 stdlib. Tests invoke the shipped `./owes` process.

## Reality assessment

Copied from the pre-implementation harvest (hdd-agent):

> Take a diff or two snapshots. Extract identifiers and simple MUST/required-file
> phrases from remaining docs/tests. Report removed symbols still mentioned;
> required files named by remaining docs that do not exist.
>
> Will not understand policy language beyond simple patterns. Will not know
> true author intent.
>
> Removed magic: CVE/ticket oracles, hidden chat logs, auto-rationale.

Harvest mapping, preserved:

- Change as a set of added/removed lines
- Obligation as text already in the tree (docs, tests, comments)
- Absence of a named companion file
- Will not understand policy language beyond simple patterns
- Will not know true author intent

## Empirical transcript

First working run, 2026-09-01, worktree
`/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-03-owes`.

```text
$ python3 tests/test_owes.py -v
test_clean_change_has_no_unkept_obligations ... ok
test_deleted_function_still_mentioned ... ok
test_json_missing_companion ... ok
test_json_shape ... ok
test_missing_companion_from_remaining_docs ... ok
test_tree_diff_flags ... ok
test_usage_error_missing_dir ... ok
test_usage_error_tree_without_diff ... ok
test_usage_error_without_args ... ok
Ran 9 tests in 0.281s
OK

$ ./demo.sh

=== 1 deleted function still mentioned in README.md (expect exit 2) ===
unkept references:
  validate_input
    README.md:3: Call `validate_input` before saving user data.
exit: 2
ok

=== 2 remaining doc names absent SECURITY.decision.md (expect exit 2) ===
missing companions:
  SECURITY.decision.md
    named in docs/CONTRIBUTING.md:5: MUST exist: SECURITY.decision.md
  docs/threat-model.md
    named in docs/CONTRIBUTING.md:7: required file: docs/threat-model.md
  make test
    named in docs/CONTRIBUTING.md:3: must run `make test`
exit: 2
ok

=== 3 clean change with no leftover mentions (expect exit 0) ===
no unkept obligations
exit: 0
ok

demo: all three fixtures behaved as expected
```

`--json` on fixture 1:

```json
{
  "unkept_references": [
    {
      "identifier": "validate_input",
      "path": "README.md",
      "line": 3,
      "text": "Call `validate_input` before saving user data."
    }
  ],
  "missing_companions": []
}
```

## Dogfood

Observed on the first real `./demo.sh` run, fixture 2:

```text
  make test
    named in docs/CONTRIBUTING.md:3: must run `make test`
```

That is a command, not a companion file. A second constructed run showed
another real miss: a changelog plus line "Removed validate_input" was
reported as an unkept reference even though the change itself wrote that
sentence.

Second commit:

- backtick-after-must keeps only filename-like tokens (`/` or `.`, no
  spaces), so `make test` is dropped and `docs/adr.md` still counts
- remaining mentions whose stripped line text appears as a plus line of
  the same change are skipped

After the fix, fixture 2 no longer names `make test`; `./owes fixtures/plus-line-changelog` still flags the leftover README mention and omits `CHANGELOG.md`.

```text
$ python3 tests/test_owes.py -v
Ran 10 tests in 0.322s
OK

$ ./demo.sh
=== 2 remaining doc names absent SECURITY.decision.md (expect exit 2) ===
missing companions:
  SECURITY.decision.md
    named in docs/CONTRIBUTING.md:5: MUST exist: SECURITY.decision.md
  docs/adr.md
    named in docs/CONTRIBUTING.md:9: must read `docs/adr.md`
  docs/threat-model.md
    named in docs/CONTRIBUTING.md:7: required file: docs/threat-model.md
exit: 2
ok
demo: all three fixtures behaved as expected

$ python3 owes fixtures/plus-line-changelog
unkept references:
  validate_input
    README.md:3: Call `validate_input` before saving user data.
exit: 2
```

## Surprises

- before/after snapshot diffing with stdlib `difflib` was enough; no git
  subprocess was required for the DIR layout.
- `required file: docs/threat-model.md` fell out of the same scan as
  `MUST exist:` without extra fixture-specific code.
- The noisy backtick matcher fired on the very first demo, before any
  extra adversarial fixture was written.

## Failures

- No understanding of "should" vs "must", conditionals, or "except in tests".
- A moved function (deleted in one file, defined in another) is still
  reported wherever it is mentioned, including its new definition.
- Comment-only leftovers (`# formerly validate_input`) still count as
  unkept references.
- `must ship \`LICENSE\`` (no dot, no slash) is ignored after the
  filename-like filter.
- Plus-line skip matches on stripped line text, so an identical
  pre-existing line in another file with the same basename could be
  dropped.

## Suggested mutations

- Skip identifiers that still have a definition in the remaining tree.
- Optionally ignore comments-only mentions (too easy to hide a real stale
  call site).
- Search tests (`*.py`, `test_*`) for MUST-like phrases, not only `*.md`.
- Bind missing companions to the files the diff actually touched.
