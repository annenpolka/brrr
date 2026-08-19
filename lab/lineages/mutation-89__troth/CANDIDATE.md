# mutation-89 — troth

## Primitive

`--apply` from **host role** without breaking OPEN expected: the legal set is `OPEN expected ∪ ACTUAL-BOUND-if-this-host`. A portable golden that failed on Alice still applies here; if this host produced the fail, the actual-side skip/fixture is legal. Comments are not oaths.

## Why this might not exist

vow (mutation-68) inferred two oaths from a failing assertion and named this host (`ACTUAL` when dump actual is `$HOME`). `--apply` still applied the *expected* side (oracle polarity). A portable expected must not skip just because you are NEITHER / ACTUAL. The naive flip — apply the side that matches host role, else skip — *does* skip OPEN expected on NEITHER. The other trap is `--side both`: AND the actual MISS into OPEN expected and skip a `/tmp` golden.

The daily loop is two skip/apply permissions, not one polarity: "the golden is portable" and "this run was me". Nobody emits their OR as an object. `--side actual` is a flag, not a host-role apply.

Discarded: lees `--par` clone. Discarded: visa-of-the-whole-file. Discarded: stain/admit. Discarded: leftover-name. Discarded: treating `# ran on alice` as an oath. Discarded: making host role a third exit code that overrides OPEN.

## How to run

From this worktree root:

```bash
./demo.sh
./troth --help
./troth --self-test
python3 -m unittest discover -s tests -q
./troth fixtures/comment_only.py
./troth fixtures/title.swift
./troth --from-fail --apply < fixtures/xctest_fail.txt
./troth --from-fail --apply --side both < fixtures/xctest_fail.txt   # vow trap: skip OPEN
printf 'E   - /tmp/x\nE   + %s/proj\n' "$HOME" | ./troth --from-fail --apply
printf 'E   - /Users/alice/proj\nE   + %s/proj\n' "$HOME" | ./troth --from-fail --apply
printf 'E   - /tmp/x\nE   + %s/proj\n' "$HOME" | ./troth --from-fail --fixture
./troth --from-fail --apply < fixtures/pytest_fail.txt
./troth --scan -C /path/to/repo --porcelain
```

## Empirical transcript

### v0.1 — legal apply set is the object

`./troth --self-test` 75/75. Unittest 39/39. `./demo.sh` passed=70 failed=0.

```
$ ./troth --from-fail --apply < fixtures/xctest_fail.txt
troth  pair  xctest  EXPECTED-OPEN vs ACTUAL-BOUND
  expected /tmp/x
  actual   /Users/alice/Library
  host     NEITHER  this host is neither recorded machine
  legal    OPEN
  apply    APPLY  this host may apply
           OPEN expected still applies (portable golden)
# exit 0

$ ./troth --from-fail --apply --side both < fixtures/xctest_fail.txt
# same report (legal OPEN) but exit 1 — AND actual MISS into OPEN expected
```

That `--side both` exit 1 *is* vow's hole: host is named, apply still poisons a portable golden.

```
$ printf 'E   - /tmp/x\nE   + %s/proj\n' "$HOME" | ./troth --from-fail --apply
troth  pair  pytest  EXPECTED-OPEN vs ACTUAL-BOUND
  host     ACTUAL  this host produced the fail
  legal    OPEN ACTUAL
  apply    APPLY
           OPEN expected still applies (portable golden)
           ACTUAL-BOUND skip/fixture is legal  [ "$(uname -s)" = Darwin ] && [ "${HOME}" = /Users/annenpolka ]
# exit 0; --emit shell still true (OPEN)

$ printf 'E   - /Users/alice/proj\nE   + %s/proj\n' "$HOME" | ./troth --from-fail --apply
  host     ACTUAL
  legal    ACTUAL
  apply    APPLY
# exit 0 — vow --side expected exits 1 (Alice MISS)

$ ./troth --from-fail --apply < fixtures/pytest_fail.txt
  host     NEITHER
  legal    (none)
  apply    SKIP
# exit 1 — neither recorded machine, expected is not portable
```

Unary gold (oath window, unchanged):

```
# ran on alice          → OPEN, silent comment USER=alice
assert os.environ['USER'] == 'alice'  → BOUND require USER=alice
title.swift             → FIXTURE USER=annenpolka, require empty
payload.rs              → SPEC (John Doe /home/user quoting)
```

Dogfood `--scan` (this host, 2026-08-20):

| repo    | BOUND | OPEN | SPEC | UNSAT | FIXTURE | note |
| ------- | ----- | ---- | ---- | ----- | ------- | ---- |
| sitbone | **0** | 21   | 0    | 0     | 4       | title fixture, not TAINTED |
| kizu    | 0     | 13   | 2    | 0     | 0       | comments silent; quoting SPEC |

sitbone `WindowTitleParserTests` USER empty, status FIXTURE. kizu `init/tests.rs` HOME empty, status SPEC.

### v0.2 — `--fixture` iff ACTUAL-BOUND; `--side both` names the AND trap

v0.1 named `legal OPEN ACTUAL` but `--emit shell` still printed `true` (OPEN). `--side actual --emit` printed Alice's skip even when this host was NEITHER. `--side both` printed `apply APPLY` (host-role) while exiting 1 (AND).

After: `--fixture` emits the actual-side skip **only if this host is ACTUAL-BOUND**. OPEN expected `--apply` is unchanged. `--side both` keeps `apply APPLY` / `legal OPEN` and names `side both SKIP  AND actual MISS into OPEN expected`.

```
$ printf 'E   - /tmp/x\nE   + %s/proj\n' "$HOME" | ./troth --from-fail --fixture
[ "$(uname -s)" = Darwin ] && [ "${HOME}" = /Users/annenpolka ]
# exit 0

$ ./troth --from-fail --fixture < fixtures/xctest_fail.txt
false
# exit 1 — NEITHER; Alice's skip is not legal here

$ ./troth --from-fail --apply --side both < fixtures/xctest_fail.txt
  legal    OPEN
  apply    APPLY  OPEN expected still applies
  side     both  SKIP  AND actual MISS into OPEN expected
# exit 1
```

`./demo.sh` → passed=80 failed=0. Unittest 43/43. Self-test 79/79.

## Dogfood targets

- `fixtures/` — comment vs env-assert, alice/CI snaps, sitbone-shaped title, kizu quoting payload, pytest/cargo/jest/go/junit/xctest dumps, pytest `-vv` tmp-vs-alice, junit XML, `# ran on` inside a fail dump
- This host's live `$HOME`/`$USER` written into `demo-tmp/live.snap` (MATCH) and live fail dumps (`legal OPEN ACTUAL`, `legal ACTUAL`)
- `/Users/annenpolka/ghq/github.com/annenpolka/{sitbone,kizu}` `--scan` (read-only)

## Surprises

- The object is an **OR of permissions**, not a chosen polarity. AND (`--side both`) is exactly how OPEN expected breaks. OR (`--side host`) is how ACTUAL-BOUND becomes legal without skipping `/tmp`.
- `--emit shell` on `legal OPEN ACTUAL` still prints `true` (the golden's predicate). `--fixture` is the gated actual-side skip; `--side actual --emit` is ungated. Three verbs, not one.
- sitbone needed no new fixture rule. The assertion window already keeps `annenpolka` as identity-as-data. troth's new object lives only on `--from-fail --apply`.

## Failures

- `--emit shell` under `--side host` still prefers OPEN `true` when both OPEN and ACTUAL are legal. That is now the point of `--fixture` (gated) vs `--emit` (golden predicate).
- HOST (hostname) is still soft and not part of `--apply`.
- Assertion strings that wrap across a third-argument message are parsed as call-args; Swift `#expect` with `<>` generic noise is not.
- `skills` / voidtrace / tenaoshi were not scanned this generation (sitbone/kizu were the gold).

## Suggested mutations

- `--held`-style: when did an assertion newly acquire an actual-bound machine.
- Join with alibi: splice tests onto old production, then troth the failure (LOCKED-and-EXPECTED-BOUND vs LOCKED-and-ACTUAL-BOUND).
- Resolve `expected = home; assert got == expected` by following the name.

## Kill / keep

**Keep.** The object is new: `--apply` is a legal set from host role ∪ OPEN expected, not expected-only polarity and not an AND of both sides. A dump whose actual is this `$HOME` applies the actual-side skip/fixture (vow `--side expected` skips); `--fixture` emits that skip only when it is legal. A dump whose expected is `/tmp/x` still applies here when host is NEITHER (naive host-role skip, and vow `--side both`, do not). sitbone stays FIXTURE (not TAINTED). kizu comments about John Doe stay silent; quoting asserts are SPEC. `# ran on` does not bind. Not lees `--par`, not visa's whole file, not stain/admit, not leftover-name.
