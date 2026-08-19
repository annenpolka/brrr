# candidate-43 — badge

## Primitive

Never-red is a fold over observations keyed by **(suite, class, method)**
across rename and alias, and `<flakyFailure>` is a red — not `rg PASS` on
the newest junit, and not maiden's string id.

## Why this might not exist

maiden (candidate-42) named the never-red set. DESTROYER_MAIDEN showed the
object was still **parser × string id**: Surefire `<flakyFailure>` maidened a
test the file said had failed, and `pkg.T::compute_diff` →
`pkg.T::compute_operation_diff` was a new maiden column. TDD's "this test has
never been red" is not a spelling. Coverage, alibi, cinch, and maiden-as-
string-id all miss that.

Discarded: alibi, cinch, leftover-name, inverse-printf, third ambit, fourth
cinch, `rg PASS`.

## How to run

```bash
chmod +x ./badge ./demo.sh
./badge --selftest
./demo.sh
./badge --no-ledger --header fixtures/junit/run-2019-fail.xml fixtures/junit/run-2024-green.xml
./badge --no-ledger --header fixtures/junit/flaky-then-green.xml
./badge --no-ledger --header fixtures/junit/rename-fail.xml fixtures/junit/rename-pass.xml
./badge --no-unify --no-ledger --counts fixtures/junit/rename-fail.xml fixtures/junit/rename-pass.xml
./badge --no-ledger --roster --counts fixtures/roster/sitbone-list.txt
```

Python 3.10+, stdlib. Exit 0 ok, 1 `--check` fired, 2 usage.

## Empirical transcript

### v0.1 — triple + flakyFailure is red

`--selftest` 43/43. Gold junit 2019-fail + 2024-green still:

| id | history | `--latest` | skeptic |
| --- | --- | --- | --- |
| pkg.T::alpha | SCARRED (fail 2019, pass 2024) | MAIDEN | yes |
| pkg.T::beta | MAIDEN (2 pass) | MAIDEN | no |
| pkg.T::gamma | SKIPPED | SKIPPED | no |
| pkg.T::delta | MAIDEN (born 2024) | MAIDEN | no |

JSON now carries `suite` / `class` / `method`. `--latest --skeptic` exits 2.
`ingest --run ci-2024 FILE` works (maiden argparse order was rc=2).

Destroyer fixtures:

| file | maiden 0.2 | badge 0.1 |
| --- | --- | --- |
| `flaky-then-green.xml` | MAIDEN `pkg.T::alpha` | **SCARRED** |
| `rerun-failure.xml` | MAIDEN | **SCARRED** |
| `status-attr-failed.xml` | MAIDEN | **SCARRED** |
| `rename-fail` + `rename-pass` | SCARRED `compute_diff`, MAIDEN `compute_operation_diff` | **same split** |
| `skip-only.xml` | SKIPPED, `--check MAIDEN` 0 | SKIPPED |
| sitbone list | UNKNOWN 213 | UNKNOWN 213 |

The rename pair was the remaining hole: identity was structured but not yet
joined across a method rename.

### v0.2 — rename is one identity (from that dogfood)

`--no-unify` on the destroyer pair is the v0.1 split (SCARRED 1 MAIDEN 1,
SKEPTIC 0). Unify folds token-subset method rename and package-prefix class
move, blocked by co-occurrence in the same src/run:

| pair | v0.1 | v0.2 |
| --- | --- | --- |
| `compute_diff` + `compute_operation_diff` | 2 ids, SKEPTIC 0 | **1 id SCARRED** n_fail=1 n_pass=1, **SKEPTIC 1**, aka=old spelling |
| `pkg.Old::alpha` + `pkg.New::alpha` | 2 ids | **1 id SCARRED** |
| gold 2019+2024 | 4 ids | **4 ids** (alpha/beta do not join) |
| sitbone roster | UNKNOWN 213 | **UNKNOWN 213** |

`why pkg.T::compute_diff` names the canonical badge
`pkg.T::compute_operation_diff`. `--selftest` 46/46. `./demo.sh` 32 passed, 0 failed.

## Dogfood targets

- fixtures/junit (maiden gold + destroyer flaky/rename/status/skip)
- fixtures/roster/sitbone-list.txt (213 specifiers from live `swift test list`)
- fixtures/gha, cargo, swift, tree (maiden identity fixtures)
- live sitbone `swift test list` (UNKNOWN 213, MAIDEN 0)

## Surprises

1. Surefire's green suite (`failures="0"`) still contains `<flakyFailure>`.
   never-red on junit is not `rg '<failure>|<error>'`.
2. `status="failed"` with no child is a real Android/Gradle dialect; empty
   body is still pass.
3. sitbone's 213 list lines already *are* `(module, type-path, func)` — the
   roster is a badge column with no outcomes, not a maiden column. Unify
   must not touch them: they all co-occur in one `--list`.
4. The destroyer rename pair becomes `--skeptic` once it is one identity.
   String-id never-red could not see the scar beside the new spelling.

## Failures

- Class+method both changing (`pkg.Old::compute_diff` →
  `pkg.New::compute_operation_diff`) still splits (no transitive bridge).
- Token-subset needs ≥2 tokens; `alpha` → `alpha_v2` does not join (class
  move of exact `alpha` does).
- bun / go / nextest logs still parse to empty (maiden hole, not this cut).
- xcresult missing bundle still empty.

## Suggested mutations

- Bridge simultaneous class+method rename via the leaf + occupancy, not
  extra fuzzy tokens.
- Refuse non-empty unparsed logs (go/bun/nextest) instead of a silent fold.
- Persist `gh run view --log` before 410 (maiden CANDIDATE).

## Kill / keep

**Keep.** Gold alpha is still SCARRED / `--skeptic`; SKIP-only is not maiden;
sitbone 213 is UNKNOWN; `<flakyFailure>` is a red; rename is one identity.
Kill only if a later tool shows never-red is alibi on HEAD — it is not. Do
not grow a test-intel platform. The object is the dialect-honest fold keyed
by a badge, not a prettier TSV.
