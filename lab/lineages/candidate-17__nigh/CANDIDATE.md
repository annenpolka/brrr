# candidate-17 — nigh

## Primitive

Compare a repository's constructed literals against its branch cuts and report the distance field: CLOSED (never constructed), NIGH (grazes: typo/case/inflection/affix), BRINK (numeric on the cut).

## Why this might not exist

Dead-code tools ask "is this reachable in the CFG?". Coverage asks "did a process execute this?". Mutation testing asks "would a test fail?". Linters ask "is this comparison silly?". None of them ask the cheaper, static question: *given the values this tree already writes down, which predicates never fire and which ones almost do?*

That join — predicates ⋈ vocabulary, with a metric — is a missing Unix column. `rg "beam"` finds mentions. `nigh` classifies a mention as a *cut* or a *constructor* and measures the gap.

Not leftover-name hunting (the name is alive in the predicate). Not inverse-dead-code (the function is called). Not format-string inversion (no runtime string → template). Not ghosts of deleted identifiers.

Four primitives considered; two discarded as conventional (unnamed call-protocol mining; assertion-tether / mutation-lite). The other remaining idea was representation-boundary field drift (`seam`). `nigh` is the stranger object.

## How to run

```bash
python3 bin/nigh fixtures
python3 bin/nigh --probe success fixtures
python3 bin/nigh --format tsv --nigh fixtures | cut -f2,3,6,9
python3 bin/nigh --closed /Users/annenpolka/ghq/github.com/annenpolka/sitbone/Sources
./demo.sh
```

Exit: `0` clean, `1` CLOSED or NIGH, `2` usage. `--report-only` always `0`.

## Empirical transcript

### Before (v0.1, commit `b02180f`)

Fixtures already worked:

```
NIGH       nigh_typo.py:2  status == 'success'   (Success / sucess)
NIGH       nigh_inflect.ts:2  flag === 'has_more' (hasMore)
CLOSED     closed.py:4  kind == 'phoenix'
CLOSED     family.ts:2  action.kind === 'action.never-built'
           family action.resolved-beam, action.resolved-radial, ...
BRINK      brink.go:4  n > 3   (HIT 8, BRINK 3)
```

Dogfood on real trees (default report included ONE-SIDED / BRINK):

| repo | files | gates | NIGH | CLOSED | notes |
| --- | --- | --- | --- | --- | --- |
| sitbone Sources+Tests | 50 | 67 | 2 | 3 | `--auto-start` already found; drowned in ONE-SIDED test asserts |
| kizu `src/` | 69 | 148 | 28 | 31 | Rust lifetimes parsed as strings (`impl < 'a> SelectState<'`); `\x1b` became `x1b` |
| tenaoshi Engine+Shell | 49 | 90 | 6 | 12 | `claude-haiku-4-5` CLOSED because it lived only inside a Swift `#"..."#` blob |
| voidtrace pkgs/apps/data/tools/specs | 221 | 100 | 6 | 3 | JS template `${...}` desynced the lexer; `forced-slash` assignment invisible; `ENOENT` NIGH-matched `event` at d=2 |
| skills | 3 | 3 | 0 | 2 | `__name__ == "__main__"` |
| stratal | 0 | 0 | 0 | 0 | empty tree |

Real hit already present: sitbone `CommandLine.arguments.contains("--auto-start")` — the flag is tested for and never constructed as a literal anywhere under `Sources/`.

### After (v0.2)

Lexer and scoring changes driven by the failures above:

- Rust `'a` / `'static` / `'_` are lifetimes, not strings
- JS/TS template interpolations no longer swallow the rest of the file
- `\xNN` / `\u{…}` / `\uNNNN` unescaped
- Swift `#"..."#` raw strings + vocab harvested from long JSON blobs
- no-whitespace vocab (oracle sentences dropped)
- `__main__`, regex-shaped rhs, `contains()` UI snippets dropped
- typo matching requires first letter; d=2 only with a shared prefix; `ENOENT` ↛ `event`
- numeric "nearby" only with the same field (`401` NIGH `400` on `statusCode` stays)
- default report is CLOSED+NIGH only

`./demo.sh` still exits 0. New fixture guards: `template.ts` assignment satisfies `forced-slash`; `long_json.swift` produces `claude-haiku-4-5`; `rust_lifetime.rs` does not emit lifetime gates; `enoent.ts` is CLOSED, not a typo of `event`.

Recount:

| repo | v1 gates / NIGH / CLOSED | v2 (same roots, default) |
| --- | --- | --- |
| sitbone | 67 / 2 / 3 | 65 gates; default CLOSED=5 (`--auto-start`, `www.`, layout numbers) |
| kizu | 148 / 28 / 31 | **44 / 4 / 8** — lifetime garbage gone |
| tenaoshi | 90 / 6 / 12 | **80 / 1 / 6** — model names now produced from raw JSON |
| voidtrace | 100 / 6 / 3 | **849 gates, CLOSED=5, NIGH=0** — templates now visible; the old `forced-slash` NIGH was a false miss |

### Findings that survived scrutiny

**voidtrace** — `case "critical-tier.resolve-binary-roll"` in `packages/kernel/src/trace-replay.ts:1388` is the *only* occurrence of that token in the whole repo. Sibling family values (`critical-tier.resolve-tier-roll`, `critical-tier.resolve-expected-branches`) are constructed. The arm is a fall-through onto the next case. In-repo vocabulary can never take that label.

**sitbone** — `contains("--auto-start")` in `SitboneApp.swift:61`. Production code looks for a flag nobody writes down. `startswith("www.")` similarly: hostnames in the tree are `zenn.dev` / `youtube.com`, never a `www.`-prefixed producer.

**tenaoshi** — `http.statusCode == 401` NIGH against a `400` produced on the same field. `line.hasPrefix("data:")` CLOSED: SSE prefix never constructed in-repo (it arrives from the wire).

**kizu** — `diff.contains("API_TOKEN")` CLOSED relative to short vocab: the constructor is the long blob `"API_TOKEN=deadbeef\n..."`. Useful as a reminder that buried tokens are still a hole.

## Dogfood targets

- `/Users/annenpolka/ghq/github.com/annenpolka/{sitbone,kizu,tenaoshi,voidtrace,skills,stratal}` (read-only)
- `fixtures/` — closed, typo, inflection, brink, family+JSON, membership, comments-only, oracle prose, typeof, rust lifetimes, JS templates, Swift raw JSON, ENOENT vs event

## Surprises

- A switch arm that exists only as a `case` label (`resolve-binary-roll`) is a sharper object than "unused function".
- Template-literal desync hid most of voidtrace's actual gates; fixing the lexer *increased* gates 8× and *decreased* false NIGH to zero.
- Inflection (`has_more` / `hasMore`) is a *distance*, not identity tracking — same surface as name-alias tools, different question (does the cut ever get built?).
- `node_modules` as a CLOSED `entry.name ===` is almost a joke: the scanner skips that directory, so the name is never a producer. Still true.

## Failures (remaining)

- Tokens buried in unquoted long strings (`API_TOKEN=deadbeef`) are not harvested.
- `contains("lib.py:3")` still NIGHs `lib.py` (path:line without a slash).
- Numeric equality CLOSED on test layout constants (`820`, `11.5`) is correct and also boring.
- Swift/Rust enum cases (`.flow`, `FocusPhase.drift`) are not string gates.
- Git protocol prefixes (`---`, `data:`, `` ``` ``) look CLOSED because they are assembled or arrive from a pipe.
- Pkl / generated files still contribute some regex-shaped leftovers if they sneak past the filter.
- Membership gates are all-or-nothing (`punch-through | ricochet | chain` is BALANCED if any member is produced).

## Suggested mutations

- Harvest `KEY=` / dotted tokens from long assignment strings.
- `PARTIAL` status for membership lists.
- `--diff`: gates whose HIT set changed between two refs.
- Enum-case extraction (`.foo` as both gate and producer).
- `--probe` against stdin values as a `comm`-style filter in a test runner.

## Kill / keep

**Keep.** The object is small (two columns + a metric), Unix-shaped (`--probe` inverts it, TSV pipes it), and on the second dogfood it pointed at a real unconstructed discriminant in voidtrace plus a real unconstructed CLI flag in sitbone. The first hour's noise was lexer/oracle leakage, not an empty idea.
