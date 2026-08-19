# mutation-106 — preen

## Primitive

Unfold a nested default from the **constructed expression**, not the type's init signature. Clap TACIT is an **invocation that omitted `--flag`**, not a command-shaped line.

`PinProfile(..., thresholds: Thresholds = Thresholds(driftDelay: 20))` omitted inhabits **OVERRIDE 20**. tacit reported **TACIT 15** (Thresholds's signature). Passing `Thresholds(driftDelay: 15)` is nested **SHADOW** of `SessionProfile.thresholds.driftDelay`, not only BOUND of the outer token.

## Why this might not exist

tacit's unfold walked `Foo`'s init defaults whenever the default *looked like* `Foo(...)`. The arguments inside `Thresholds(driftDelay: 20)` were ignored. Two sites can inhabit different nested worlds (`15` vs `20`) and tacit named the same future.

Clap TACIT was `kebab` on a command-shaped line (`kizu ` / `command:` / `$ `). kizu's 6 TACIT were comments, `.contains("kizu hook-post-tool")`, and a truncated doc-comment. Production always writes `--agent {agent_arg}`. There were no real clap riders.

Discarded: leftover-name search, lockset clone, rewriting tacit into a review platform.

## How to run

```bash
chmod +x ./preen ./demo.sh
./preen --selftest
./demo.sh 0
./preen -C /Users/annenpolka/ghq/github.com/annenpolka/sitbone --summary presentThreshold
./preen -C /Users/annenpolka/ghq/github.com/annenpolka/sitbone --all SessionProfile driftDelay
./preen -C /Users/annenpolka/ghq/github.com/annenpolka/kizu --all --summary agent
./preen -C ./fixtures --all PinProfile driftDelay
```

Python 3.10+, stdlib, `git` for `--git`. Exit 0 ok, 1 `--check` found TACIT/BLAST, 2 error.

## Empirical transcript

### v0.1 — constructed unfold + invocation clap

`--selftest` 44/44. `./demo.sh 0` passed=35 failed=0 (before the clap needle/shebang fix).

Constructed ≠ signature (fixtures):

```
SessionProfile(name: "coding")                         TACIT  thresholds.driftDelay 15
SessionProfile(..., thresholds: Thresholds())          TACIT  thresholds.driftDelay 15
SessionProfile(..., thresholds: Thresholds(driftDelay: 15))  SHADOW 15
SessionProfile(..., thresholds: Thresholds(driftDelay: 20))  OVERRIDE 20
PinProfile(name: "p")   default Thresholds(driftDelay: 20)    OVERRIDE 20
DotInit(name: "d")      default .init()                      TACIT 15
```

tacit on the same PinProfile site: TACIT 15. preen stops when constructed-default ≠ signature-default.

sitbone (nested default is `Thresholds()`, so constructed == signature 15 — still honest):

| query | tacit | preen v0.1 |
| --- | --- | --- |
| `presentThreshold` | **27 TACIT, 0 SHADOW** | **27 TACIT, 0 SHADOW** |
| `e9b0f75` PresenceArbiter | BLAST 54, `--check` rc=1 | BLAST 54, `--check` rc=1 |
| `SessionProfile colorHue` | SHADOW makeDefault 0.45 | SHADOW makeDefault 0.45 |
| `SessionProfile driftDelay` | 10 TACIT 15 (omitted `Thresholds()`) | 10 TACIT 15 |

kizu `--all --summary agent`:

| | TACIT | SHADOW | OVERRIDE | BOUND |
| --- | --- | --- | --- | --- |
| tacit HookPostTool | 6 (comments / contains / doc) | 14 | 4 | 1 |
| preen v0.1 HookPostTool | 6 (different 6) | 14 | 3 | 1 |
| tacit HookStop | 0 | 4 | 3 | 1 |
| preen v0.1 HookStop | 1 | 4 | 3 | 1 |

Old gold-lie lines gone: `settings_json.rs:15` doc-comment, `:152` comment, `tests.rs:97/198/308` comments. New false TACIT: `matches!(token, "hook-post-tool")`, `.contains("hook-post-tool")` (opening quote hid the needle), assertion prose `pre-existing hook-post-tool must remain` (kebab was argv[1]). Lost a real OVERRIDE: `#!/bin/sh\n{} hook-post-tool --agent cline` (kebab was argv[2] after shebang + `{}`).

### v0.2 — one improvement, from that run

v0.1 clap TACIT moved rather than vanished. The remaining 6 were `matches!(token, "hook-post-tool")`, `.contains("kizu hook-post-tool")` (needle regex died on the opening quote), and assertion prose `pre-existing hook-post-tool must remain` (kebab was argv[1]). The lost OVERRIDE was `#!/bin/sh\n{} hook-post-tool --agent cline` (kebab at argv[2]).

Fix: an invocation is **kebab followed by `--flag`/`{`/`$` anywhere**, or **bare kebab last with at most one predecessor**. Needles are `contains(` / `matches!(` in the 80 chars before the string, quote-tolerant.

`--selftest` 45/45. `./demo.sh 0` passed=40 failed=0.

kizu `--all --summary agent` after:

```
HookPostTool  agent  "claude-code"  TACIT=0 SHADOW=14 OVERRIDE=4 BOUND=1
HookStop      agent  "claude-code"  TACIT=0 SHADOW=4  OVERRIDE=3 BOUND=1
```

The 6 mention-TACIT are gone. `install.rs:345` shebang cline is OVERRIDE again (4, matching tacit's real OVERRIDE count). sitbone **27 TACIT presentThreshold**, e9b0f75 **BLAST 54**, makeDefault SHADOW hue unchanged.

Constructed-default ≠ signature-default still holds on PinProfile (OVERRIDE 20 vs TACIT 15).

## Dogfood targets

- `./preen --selftest` (45): Swift constructed unfold, `.init()`, clap omit / continuation / quotes / `long=` / `--timeout` / shebang OVERRIDE / prose-not-TACIT, Python, TS, diff BLAST/FOSSIL.
- `./demo.sh 0` (40): fixtures + synthetic git rename + sitbone/kizu/tenaoshi.
- `/Users/annenpolka/ghq/github.com/annenpolka/{sitbone,kizu,tenaoshi}`.

## Surprises

- sitbone never constructs `Thresholds(driftDelay: 20)` as a default. Every nested default is `Thresholds()`. Constructed-default ≠ signature-default is a fixture object (PinProfile); sitbone still pays rent as 27 TACIT `presentThreshold` and 10 TACIT `thresholds.driftDelay=15`.
- kizu's 6 TACIT moved rather than vanished in v0.1. Masking comments was necessary and not sufficient. `kebab at argv[0] or argv[1]` treats English `pre-existing hook-post-tool …` as a subcommand and misses `#!/bin/sh {} hook-post-tool --flags`.
- `.contains("kizu hook-post-tool")` on the same line still fired in v0.1 because the needle regex ended before the opening quote. v0.2 searches `contains(` / `matches!(` in the prefix.

## Failures

- tenaoshi `PanelSession.swift:623` wrapper `func reopenUnit(id: String)` is still TACIT of `returningToFinal`. Signature-skip is only the defaulted sig, not every `func reopenUnit(`.
- Swift unlabeled first (`paint("red")`) still drops the call. Trailing closures unbound. `*args` still steal positionals. Block comments can still drop a labeled call. Pairing is still index. Parked: those are other holes; this mutation is constructed unfold + clap invocations.
- TypeScript `name = value` is still treated as a keyword. Not this primitive.

## Suggested mutations

- **wrap**: signature-skip is every `func reopenUnit(`, not only the defaulted paren. tenaoshi `:623` is not a call.
- **splat**: `*args` / `**kwargs` do not occupy positional slots. TS does not have `name =` keywords.
- **paint**: unlabeled first argument is still a call; defaulted labeled slots after it are TACIT.
- **pair**: pairing is identity of a defaulted slot, not index. Insert-before-rename must keep FOSSIL.

## Kill / keep

**Keep.** The object is still omission. The mutation is load-bearing: constructed-default ≠ signature-default is now a different verdict (PinProfile OVERRIDE 20 vs SessionProfile TACIT 15), and kizu clap TACIT=6 mentions became TACIT=0. sitbone 27/54 and makeDefault SHADOW hold. Do not grow a review platform.
