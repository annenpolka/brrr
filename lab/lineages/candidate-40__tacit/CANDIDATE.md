# candidate-40 — tacit

## Primitive

A slot with a default is not a value. Classify each call-site as **TACIT** (omitted; rides a future default change), **SHADOW** (passed a literal equal to the default; will not follow), **OVERRIDE**, or **BOUND**. A default-moving diff is a **BLAST** of tacit riders plus **FOSSIL** restatements of the old literal.

## Why this might not exist

`rg foo(` plus counting commas is the skeptic pipeline. It loses keyword arguments, multiline calls, Swift labels, clap flags, nested `Thresholds = Thresholds()`, and the only distinction that matters: two sites can inhabit the same world (`0.45`) with opposite futures.

sow/hatch emit the *values* production inhabits. cinch locks hunks. zanei finds leftover *claims*. erst finds natal *keys*. None of them name **omission**. The compiler does not warn when you change a default. Coverage still says the tests ran. The hysteresis tests never pass `presentThreshold` and still "cover" it.

The missing Unix verb is: *who rides this default, and who restated it?*

Discarded: leftover-name search, inverse-printf, occupancy eras, path-conditions, env-ABI, wait-for graphs, lockset clones, `existing tool + LLM`.

## How to run

From the worktree root:

```bash
chmod +x ./tacit ./demo.sh
./tacit --selftest
./demo.sh
./tacit -C /Users/annenpolka/ghq/github.com/annenpolka/sitbone --summary PresenceArbiter
./tacit -C /Users/annenpolka/ghq/github.com/annenpolka/sitbone --git e9b0f75^ e9b0f75 --check
./tacit -C /Users/annenpolka/ghq/github.com/annenpolka/kizu --all --summary agent
./tacit -C /Users/annenpolka/ghq/github.com/annenpolka/tenaoshi --all reopenUnit
```

Python 3.10+, stdlib, `git` for `--git`. Exit 0 ok, 1 `--check` found TACIT/BLAST, 2 error.

## Empirical transcript

### v0.1 — classify + unfold + rename pairing

`--selftest` green on fixtures: TACIT/SHADOW/OVERRIDE/BOUND, comment residue ignored, `SessionProfile` unfolds `thresholds.driftDelay`, `--git` BLAST/FOSSIL, `threshold → presentThreshold` at the same index.

First dogfood (before honesty):

| tree | query | v0.1 |
| --- | --- | --- |
| sitbone | `presentThreshold` | **27 TACIT, 0 SHADOW**. Hysteresis tests ride 0.45. Production `SitboneCore.swift:68` rides it. Money shot. |
| sitbone | `--git e9b0f75^ e9b0f75` | **BLAST 54**: rename `threshold=0.4 → presentThreshold=0.45` plus born `absentThreshold=0.35`. Every caller tacit. |
| sitbone | `--summary PresenceArbiter` | **false callees**: `SensorReading`, `PresenceReading` because the filter matched the *path* `PresenceArbiter.swift`. |
| sitbone | `--summary SessionProfile` | `createProfile` / `test(` leaked via `SessionProfileTests.swift` in the path. |
| sitbone | `colorHue` | **SHADOW** `makeDefault()` passes `0.45` — real, kept. |
| kizu | `agent` | only **HookStop** (clap_flags keyed by field name, HookPostTool overwritten). `{agent_arg` classified OVERRIDE. |
| tenaoshi | `reopenUnit` | signature `returningToFinal: Bool = true` classified as a **BOUND call**. Lie. |
| voidtrace | `--summary` | TS firehose: every `ident(` with a `>` in the type looked like a default. |

### v0.2 — one improvement, from that run

Honesty of *sites*, not more verdicts:

1. **Filters match callee/param**, not path (unless the needle looks like a path).
2. **A signature paren is not a call.** `reopenUnit(` the definition is skipped; `reopenUnit(id:, returningToFinal: true)` stays SHADOW.
3. **Clap `--agent` binds to the subcommand on the line.** HookPostTool and HookStop are two slots. `{agent_arg` / format interpolations are BOUND. Trailing `\n` in `"--agent cline\n"` peels so **cline is OVERRIDE**.
4. TS signatures require `function` / `const f = (` / `constructor` / a visibility-prefixed method. Cuts the `changedScenario` dump; remaining generics are a known miss.

After v0.2: `./demo.sh` **32 passed, 0 failed**.

sitbone `--summary PresenceArbiter` is four rows, all PresenceArbiter. `makeDefault` SHADOW intact. e9b0f75 still BLAST 54.

kizu:

```
HookPostTool  agent  "claude-code"  TACIT=6 SHADOW=14 OVERRIDE=4 BOUND=1
HookStop      agent  "claude-code"  TACIT=0 SHADOW=4  OVERRIDE=3 BOUND=1
```

Tests restate `--agent claude-code` (SHADOW: a default change will not update installed hook strings). `install.rs` interpolates `{agent_arg}` (BOUND). Cline installer hardcodes `"cline"` (OVERRIDE).

tenaoshi `reopenUnit`: signature gone. `reopenFocusedFinalUnit` SHADOW `true`. PanelSession/PanelView TACIT — production rides `returningToFinal=true`.

voidtrace: `createWorldState(entities=[])` 14 BOUND constructions; `readCommandVersion(args=["--version"])` 3 TACIT.

## Dogfood targets

- `./tacit --selftest` (33): Swift/Python/dataclass/clap/TS, unfold, diff, rename, signature-skip, filter, interpolation.
- `./demo.sh` fixtures + synthetic git rename + sitbone/kizu/tenaoshi/voidtrace.
- `/Users/annenpolka/ghq/github.com/annenpolka/{sitbone,kizu,tenaoshi,voidtrace}`.

## Surprises

- Hysteresis tests **override `emaAlpha: 1.0`** (they need an identity EMA) and **omit the thresholds they are about**. The tests document 0.45 in comments and in the 0.40 middle-band stimulus. The call does not lock the default. Changing `presentThreshold` to 0.50 would keep the tests green until the middle band moved, then silently retarget.
- `SessionProfile.makeDefault()` is the dual: it **looks** like it uses the default mint hue and does not. It is SHADOW.
- Nested `thresholds: Thresholds = Thresholds()` means `SessionProfile(name: "coding")` rides `driftDelay=15` without mentioning Thresholds. Unfold is the only way that row exists. SessionProfileTests then `XCTAssertEqual(..., 15)` — a SHADOW assertion, not a SHADOW call. Different object (zanei/echo); not harvested.
- Clap `default_value` lives in a string. Masking strings for comment-safety *deleted the default*. Structure from the mask, value from the original.
- Darwin/`e9b0f75` is a rename plus a numeric move plus a born slot. Name-only join would report death of `threshold` and birth of `presentThreshold` with no BLAST. Position pairing is load-bearing.

## Failures

- TypeScript generics and `T = Default` still leak (`change> void` as a default on voidtrace helpers). Method harvest is visibility-gated; a bare `foo(x = 1)` method is silent.
- Clap TACIT needs a command-shaped line (`kizu ` / `command:`). Prose `kizu hook-post-tool` in README is a miss unless it contains those markers.
- Swift unlabeled first arguments are ignored (honesty: they were comment residue). A real `_ sensors:` unlabeled init would be silent.
- Rust `impl Default` / serde `#[serde(default)]` / TOML omission is the same object (config-key TACIT) and is not harvested.
- Default expressions that are not `Foo()` do not unfold (`Double.random(in: 0...1)`).
- `--git` walks both trees via `git show`; large monorepos will be slow. No file-ignore beyond directory skip.

## Suggested mutations

- **echo**: a TACIT call whose enclosing function body restates the default literal (hysteresis comments/`XCTAssertEqual(..., 15)`). The test *thinks* it locked 0.45.
- **config-key TACIT**: `impl Default` fields vs omitted keys in TOML/JSON (kizu `debounce_worktree_ms = 300` in README is SHADOW of TimingConfig::default).
- **`--patch -`**: harvest default changes from a unified diff without two full tree walks.
- **`--emit`**: rewrite TACIT sites to SHADOW (pin the current default) or rewrite SHADOW to TACIT (delete restated literals). The patch is the witness.
- Inverse: given a call, print the world it inhabits *and* which slots are tacit, as a fixture (sow with a binding column).

## Kill / keep

**Keep.** The object is omission. sow cannot name TACIT vs SHADOW of the same world. A skeptic who will `rg presentThreshold` still cannot see the 27 riders that never mention it. sitbone e9b0f75 and kizu `--agent claude-code` already paid rent.

Park: treating this as leftover-claims (zanei) or argument-worlds (sow). Those are the values. This is whether the value was said.
