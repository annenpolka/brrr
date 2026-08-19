# candidate-04 — reverb

## Primitive

Treat the preimage of a diff as a search query: given what you just changed or deleted, find remaining copies of the old code (exact, indent-drifted, identifier-renamed, or same string literal in a different line shape).

## Why this might not exist

The recurring workflow is: fix a bug in one place, then `rg` for a string you hope is distinctive, then miss the copy whose identifiers differ or whose indent drifted. `git grep` searches what you type. Clone detectors search the whole tree without knowing *which* snippet you just decided was wrong. `reverb` makes the diff itself the query.

Four primitives considered; discarded the two most conventional:

1. ~~hunk-bisect of uncommitted changes~~ (delta-debug + `git bisect` mashup)
2. ~~rename-residue via `rg` of old identifiers~~ (typed-query leftover hunt)
3. `after` — what do callers do with this return value? (kept as a mutation)
4. **reverb** — the change is the search query (implemented)

## How to run

```bash
chmod +x reverb demo.sh
./demo.sh
./reverb -C /path/to/repo
git diff HEAD | ./reverb --stdin --json
./reverb --grep | cut -d: -f1 | sort -u
```

Exit: 0 none, 1 lingering preimages, 2 error.

## Empirical transcript

### Before the improvement (commit 88c5a6c)

Synthetic fixture: fix one of several duplicated nil-checks.

```
changed src/auth.py:2-4
  -     if user is None:
  -         return 0
  -     user.activate()
  exact  src/billing.py:2-4
  indent src/nested dir/legacy.py:2-4
  exact  src/nested dir/バグ copy (1).py:2-4
reverb: 3 lingering preimages from 1 query
note: missed identifier-renamed clone src/accounts.py (token matching gap)
note: missed nested-git copy vendor_copy/nested-git/shadow.py (ls-files gap)
```

tenaoshi adapters (real): change Content-Type charset on Anthropic only.

```
tree/CodexResponsesClient.swift:118:        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
tree/OpenAICompatibleClient.swift:91:        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
```

kizu `src/git` (real): change `unwrap_or(file_path)` in `diff.rs`. Sister line in `repo.rs` is `unwrap_or(path)`.

```
kizu exit=0
note: kizu missed repo.rs clone (different identifier names)
```

Live kizu tree with `--stdin` (change not applied): empty — origin site skipped, no exact leftovers.

sitbone Logging.swift: change one `Logger(subsystem:category:)` call. Zero hits.

voidtrace `packages/kernel/src` only: change `"catalog-load-failed"` union member. Zero hits in that narrow copy (leftovers live in other packages). Broader copy later found the *same-shaped* union member in experiments, still missed `case "catalog-load-failed":`.

### After the improvement (token clones, string literals, nested git)

Same synthetic fixture:

```
changed src/auth.py:2-4
  -     if user is None:
  -         return 0
  -     user.activate()
  token  src/accounts.py:2-4
             if account is None:
                 return 0
             account.activate()
  exact  src/billing.py:2-4
  indent src/nested dir/legacy.py:2-4
  exact  src/nested dir/バグ copy (1).py:2-4
  exact  vendor_copy/nested-git/shadow.py:2-4
reverb: 5 lingering preimages from 1 query
```

kizu copy of `src/git`, same `unwrap_or` edit:

```
kizu exit=1
tree/repo.rs:144:    let rel = path.strip_prefix(root).unwrap_or(path);
```

Live kizu `--stdin` (read-only original repo):

```
$ git-diff-shaped patch | ./reverb --stdin -C /Users/annenpolka/ghq/github.com/annenpolka/kizu --grep
src/git/repo.rs:144:    let rel = path.strip_prefix(root).unwrap_or(path);
```

sitbone: six other `Logger(...)` declarations of the same shape.

```
sitbone matches 6
  token tree/SitboneCore/Logging.swift:11
  token tree/SitboneCore/Logging.swift:14
  token tree/SitboneCore/Logging.swift:18
  token tree/SitboneData/Logging.swift:8
  token tree/SitboneSensors/Logging.swift:11
  token tree/SitboneUI/Logging.swift:8
```

voidtrace `packages/*/src`: string-literal query finds differently shaped leftovers.

```
packages/experiments/src/index.ts:39:  | "catalog-load-failed"
packages/experiments/src/index.ts:417:    return failure("catalog-load-failed", ...
packages/experiments/src/index.ts:424:      "catalog-load-failed",
packages/kernel/src/evaluate.ts:3285:      "catalog-load-failed",
packages/runtime-node/src/application.ts:194:    case "catalog-load-failed":
packages/runtime-node/src/application.ts:215:    case "catalog-load-failed":
```

Naive token matching first also flagged every `setValue("...", forHTTPHeaderField: "...")` in tenaoshi. Tightened: single-line token clones require a keyword (`let`/`if`/`unwrap_or`/…) so the Content-Type leftover stays exact-only:

```
tree/CodexResponsesClient.swift:118:        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
tree/OpenAICompatibleClient.swift:91:        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
```

`./demo.sh` exits 0 (10 checks).

## Dogfood targets

- Synthetic fixture: spaces in paths, Unicode filename `バグ copy (1).py`, extra indent, identifier rename, nested git
- `/Users/annenpolka/ghq/github.com/annenpolka/tenaoshi` — Engine adapters (copied, not mutated in place)
- `/Users/annenpolka/ghq/github.com/annenpolka/kizu` — `src/git` copy + live `--stdin` against the real repo
- `/Users/annenpolka/ghq/github.com/annenpolka/sitbone` — `Sources/*/Logging.swift`
- `/Users/annenpolka/ghq/github.com/annenpolka/voidtrace` — `packages/*/src`
- `/Users/annenpolka/ghq/github.com/annenpolka/skills` — surveyed; almost no cross-file duplicated long lines, so not a useful target

## Surprises

- Git emits a one-line `- return 0` hunk for a nil-check fix; searching only `-` lines yields nothing useful. Reconstructing the old hunk (context + deletion) is the actual preimage.
- `--all-files` already walked nested repos; default `git ls-files` did not. Nested-git discovery is the default now.
- Token-normalizing *strings* as well as identifiers made `obj.method("a", label: "b")` match every other labelled string call. Keywords on single-line token queries were the fix.
- A renamed error code's leftovers are often `case "old"` / `failure("old")`, not the union member you edited. Literal extraction, not block clone, finds those.

## Failures

- V1 missed identifier-renamed clones (kizu `file_path` vs `path`, synthetic `user` vs `account`).
- V1 missed nested git copies under `git ls-files`.
- V1 missed same-string different-shape lines (voidtrace `case "..."`).
- V1 sitbone: logger lines too unique under exact/indent.
- First token implementation: tenaoshi false positives on unrelated `setValue` headers (fixed before the improvement commit).
- skills: almost no duplicated long lines; `reverb` has nothing to say when the preimage is unique.

## Suggested mutations

- Addition-side queries: sibling functions that never gained the new check.
- Rename mapping: identifiers that changed in the hunk stay literal, others normalize — tighter than full ID substitution.
- `--tests-only` / `--no-tests` path filters.
- `after`: for a function, show what callers do with the return value (the discarded sibling primitive).
- Search blobs at `--at <rev>` without checkout, so `reverb A..B --at B` audits a historical fix.

## Kill / keep

Keep. The tenaoshi hit is the "why doesn't this exist" moment: one header-line fix, two adapters still wrong, no query typed by hand. kizu/voidtrace after the improvement show the primitive is not just copy-paste detection — it is "the intent of this diff, elsewhere."
