# CANDIDATE: mutation-02 — owes-strict

```yaml
origin:
  method: hdd
  trial: hdd-agent
  parent: candidate-03__owes
  mutation: owes-strict
```

## Primitive

Given a working-tree change (unified diff, or before/after snapshots) and
the remaining tree, list obligations written elsewhere that the change
appears to break:

- identifiers removed on minus lines that remaining files still mention
- required companion files named by remaining docs with `MUST exist: PATH`
  or `required file: PATH` that do not exist

Incidental backtick paths in markdown are not companions. First Selection
Skeptic found the parent scanner to be a landmine on real markdown.

Classification: USEFUL_COMPOSITION (ordinary mutation of candidate-03).
Nearest existing operation is `git diff` plus `rg` through docs/tests.
The mutation's observable delta versus parent: companion harvest is a
closed phrase set, not any filename-like backtick after "must".

## Why it might not exist

Diff tools stop at the hunk list. Repo linters encode one project's rules.
`owes` is the small composition: parse what the change removed, then ask
the remaining tree whether it still owes that name or that file. The
parent also treated `must \`path\`` as a required file, which fires on
ordinary prose (`see \`README.md\``). Strict companions keep the file-miss
half without scanning every backtick.

## How to run

```bash
./owes fixtures/deleted-fn
./owes fixtures/missing-companion
./owes fixtures/clean
./owes fixtures/prose-backticks
./owes --tree fixtures/deleted-fn/tree --diff fixtures/deleted-fn/change.diff
./owes --json fixtures/deleted-fn
./demo.sh
python3 tests/test_owes.py -v
```

Python 3 stdlib. Tests invoke the shipped `./owes` process.

## Reality assessment

Copied from the pre-implementation harvest (hdd-agent), still in force:

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

Parent leak this mutation closes: filename-like backtick after "must".

## Empirical transcript

First working mutation commit, 2026-09-02, worktree
`/Users/annenpolka/.grok/worktrees/annenpolka-brrr/mutation-02-owes-strict`.

```text
$ python3 tests/test_owes.py -v
test_clean_change_has_no_unkept_obligations ... ok
test_deleted_function_still_mentioned ... ok
test_json_missing_companion ... ok
test_json_shape ... ok
test_missing_companion_from_remaining_docs ... ok
test_plus_line_changelog_mention_is_ignored ... ok
test_tree_diff_flags ... ok
test_usage_error_missing_dir ... ok
test_usage_error_tree_without_diff ... ok
test_usage_error_without_args ... ok
Ran 10 tests in 0.310s
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
exit: 2
ok

=== 3 clean change with no leftover mentions (expect exit 0) ===
no unkept obligations
exit: 0
ok

demo: all three fixtures behaved as expected
```

Fixture 2 no longer names `docs/adr.md` (parent did, from `must read \`docs/adr.md\``).

Second commit, same worktree (prose-backticks fixture):

```text
$ python3 tests/test_owes.py -v
Ran 12 tests in 0.366s
OK

$ ./demo.sh
=== 4 prose markdown with incidental README.md backticks (expect exit 0) ===
no unkept obligations
exit: 0
ok
demo: all fixtures behaved as expected

$ python3 owes fixtures/prose-backticks
no unkept obligations
exit: 0

$ python3 owes --json fixtures/prose-backticks
{
  "unkept_references": [],
  "missing_companions": []
}

# parent candidate-03 on the same fixture:
$ python3 lab-hdd/lineages/candidate-03__owes/owes fixtures/prose-backticks
missing companions:
  README.md
    named in docs/guide.md:4: must see `README.md`
exit: 2
```



## Dogfood

Parent `candidate-03__owes` harvested backtick-after-must as a companion.
Skeptic ran the tool on `lab-hdd` and got false required files from
ordinary markdown, including `docs/adr.md` from `must read \`docs/adr.md\``.

First commit drops that matcher. Fixture 2 still names
`SECURITY.decision.md` and `docs/threat-model.md`; it no longer names
`docs/adr.md`.

Second commit adds `fixtures/prose-backticks`: remaining `docs/guide.md`
says reviewers must see `README.md`, and names `CONTRIBUTING.md` /
`LICENSE.md` in passing. There is no `README.md` in that tree. Parent
`owes` reports a missing companion and exits 2; this mutation prints
`no unkept obligations` and exits 0.

## Surprises

- The parent already had a filename-like filter after the first demo
  (`make test` dropped). Real markdown still tripped it via `README.md`
  and `docs/adr.md`. The leak was the matcher, not the filter.
- Replaying parent `owes` on `fixtures/prose-backticks` flags exactly
  `must see \`README.md\`` and ignores the other incidental backticks
  (`CONTRIBUTING.md`, `LICENSE.md`) because they are not after "must".
- `MUST exist: PATH` in the tool's own README remains a self-hit if you
  scan the worktree. This mutation does not invent a quoting convention
  for documenting the phrase.

## Failures

- No understanding of "should" vs "must", conditionals, or "except in tests".
- A moved function (deleted in one file, defined in another) is still
  reported wherever it is mentioned, including its new definition.
- Comment-only leftovers (`# formerly validate_input`) still count as
  unkept references.
- Companion scan still walks remaining `*.md` and does not consult the
  diff. Missing companions are true of the remaining tree, not caused by
  this hunk.
- Documenting `MUST exist: PATH` in README still names `PATH`.

## Suggested mutations

- Skip identifiers that still have a definition in the remaining tree.
- Bind missing companions to the files the diff actually touched.
- Optionally ignore comments-only mentions (too easy to hide a real stale
  call site).
- Search tests (`*.py`, `test_*`) for MUST-like phrases, not only `*.md`.
