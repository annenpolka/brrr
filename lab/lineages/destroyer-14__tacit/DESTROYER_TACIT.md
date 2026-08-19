# DESTROYER — tacit

Adversarial pass on **TACIT / SHADOW / OVERRIDE / BOUND** of a defaulted slot, and on **BLAST / FOSSIL** of a default-moving diff. No rewrites. Failures are conceptual except where a regex binds the wrong token. Attacked omission, not leftover-claims.

- **tacit** (candidate-40, v0.2) — `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01b83-5900-7902-9188-72c70d715bf7`
- Transcript: `/tmp/destroy-tacit/transcript.txt`
- Follow-up: `/tmp/destroy-tacit/followup.txt`
- Fixtures: `/tmp/destroy-tacit/fixtures/`
- Git repos: `/tmp/destroy-tacit/repos/`
- Attack driver: `/tmp/destroy-tacit/attack.py`
- TSV dumps: `/tmp/destroy-tacit/logs/`
- `./tacit --selftest` → **33 ok** after the attacks. `./demo.sh` → **passed=32 failed=0**. tacit 0.2.

Attacks: keyword vs positional (`*args`, TS `name = value`, Swift unlabeled), multiline (labeled Swift vs comment-split Python vs clap continuation), Swift labels / trailing closures, clap flags (quotes, `long =`, field-name `--agent`, comment TACIT), nested `Thresholds()`, default-moving diffs, FOSSIL of old vs new, comments that look like args, sitbone `e9b0f75` pairing gold.

Verdict: **mutate, do not kill.** sitbone `presentThreshold` is still **27 TACIT, 0 SHADOW**. `e9b0f75` is still **BLAST 54**. `makeDefault` is still SHADOW `colorHue 0.45`. Same-name `0.45 → 0.50` still emits BLAST / FOSSIL / PRE / LOCK / BOUND as advertised. Nothing in this battery turned omission into leftover-name search or into `rg foo(` plus comma counting. The holes are where a call is not a paren, where unfold reads the *signature* of `Foo` not the constructed `Foo(driftDelay: 20)`, and where clap TACIT is a command-shaped line.

---

## Primitive restated

A slot with a default is not a value. Two sites can inhabit `0.45` with opposite futures:

| verdict | claimed meaning |
| --- | --- |
| **TACIT** | omitted; rides a future default change |
| **SHADOW** | passed a literal equal to the default; will not follow |
| **OVERRIDE** | passed a different literal |
| **BOUND** | passed a name / expression / collection |

A default-moving (or born) slot in `--git OLD NEW` is tagged:

| why | claimed meaning |
| --- | --- |
| **BLAST** | TACIT on a slot whose default moved or was born |
| **FOSSIL** | still passes the old literal |
| **PRE** | already restates the new default |
| **LOCK** | some other literal |

`--check` exits 1 on TACIT (tree) or BLAST (diff). FOSSIL is visible and does not fail `--check`.

---

## 1. Keyword vs positional — `*args` and TS `=` invert the slot (conceptual, load-bearing)

Python mixed keywords survive:

```
f()            a,b,c TACIT
f(1)           a SHADOW, b TACIT, c TACIT
f(1, 2)        a SHADOW, b SHADOW, c TACIT
f(b=2)         a TACIT, b SHADOW
f(1, c=3)      a SHADOW, b TACIT, c SHADOW
f(c=3, a=9)    a OVERRIDE 9, b TACIT, c SHADOW
greet("x", "yo")           greeting OVERRIDE "yo"
greet("x", times=2)        greeting TACIT, times OVERRIDE
greet("x", greeting="hi")  greeting SHADOW
```

`parse_call_args` walks positionals against the harvested names, then keywords. That is the advertised object. It dies the moment a skipped `*args` sits in front of a default:

```python
def splat(*args, timeout=30): ...
splat()         # TACIT timeout=30     honest
splat(1)        # OVERRIDE timeout=1   lie
splat(1, 2, 3)  # OVERRIDE timeout=1   lie
```

`*args` is dropped in `parse_py_param`. `positional_names` is `[timeout]`. The first positional binds `timeout`. Reality: `1` is `*args` and `timeout` is omitted (TACIT). The tool reports the opposite future.

`kwargs(**{"timeout": 30})` is BOUND of the unpack, not SHADOW of `30`. Honest as “not a literal”; it will follow if the dict is built from the default. The `*args` inversion is the kill of *this* call, not of the primitive.

TypeScript has no keyword arguments. `name = value` is an assignment expression and a *positional*:

```
retry(() => 1, delay = 200)
# tool:   attempts TACIT, delay OVERRIDE 200
# JS:     attempts OVERRIDE 200, delay TACIT 100
```

Verdicts inverted. The Python `=` matcher is applied to TS.

**Swift unlabeled-only calls vanish.** `paint(_ color: String, opacity: Double = 1.0, blend: String = "normal")`:

```
paint("red")                                   # no rows
paint("red", opacity: 0.5)                     # opacity OVERRIDE, blend TACIT
paint("red", 0.5)                              # no rows (illegal Swift; unlabeled second)
paint("red", opacity: 1.0, blend: "normal")    # both SHADOW
```

CANDIDATE already said unlabeled first arguments are ignored (comment residue). The cost is the common legal form `paint("red")`: both defaulted slots are invisible. A site that rides `opacity=1.0` is not TACIT. It is absent.

`labeled(0.50)` (illegal without the label) is also absent. `labeled(presentThreshold: 0.50)` is OVERRIDE. Labeled Swift is the dialect the tool actually implements.

---

## 2. Multiline calls — labeled Swift works; clap continuation and Python `#` do not (conceptual)

Sitbone production is already multiline (`SitboneCore.swift:68`) and is one of the 27 TACIT `presentThreshold` rows. Fixture:

```
PresenceArbiter(
    sensors: ["camera"],
    presentThreshold: 0.45
)                                          # SHADOW 0.45

PresenceArbiter(
    sensors: ["camera"],
    presentThreshold: // the documented default
        0.45
)                                          # SHADOW 0.45   split_top strips //

PresenceArbiter(
    sensors: ["camera"]
    // presentThreshold: 0.45
)                                          # TACIT         comment is not an arg

PresenceArbiter(
    sensors: ["camera"],
    presentThreshold:
    0.50
)                                          # OVERRIDE 0.50

PresenceArbiter(
    sensors: ["camera"],
    emaAlpha: 1.0,
)                                          # presentThreshold TACIT, emaAlpha OVERRIDE
```

Labeled multiline Swift is honest. The comment that *looks* like `presentThreshold: 0.45` is not a SHADOW. That is the object.

Python `split_top` does not skip `#`. A restated default split by a comment becomes BOUND, not SHADOW:

```
greet(
    "x",
    greeting=  # restated default
        "hi",
)   # BOUND greeting=""   should be SHADOW "hi"
```

Clap is line-bound. `--agent` is matched on the whole file, then bound to the *line* that holds the flag:

```
let i = "kizu hook-post-tool \
    --agent claude-code";
```

Line 32 has `hook-post-tool` and no `--agent` → **TACIT**. Line 33 has `--agent claude-code` and no subcommand → `pick_clap_callees` sees HookPostTool + HookStop + HookNamed sharing `agent` and returns `[]` → **SHADOW dropped**. A restated default across a line break is reported as a rider.

---

## 3. Swift labels — trailing closure is TACIT of the defaulted completion (conceptual)

External/internal labels work (`mix(from: 0)` SHADOWs `from` / TACITs `to`). Trailing closures do not bind:

```swift
public func fetch(url: String, timeout: Double = 30, completion: (Int) -> Void = { _ in }) {}
fetch(url: "x") { n in }    # completion TACIT `{ _ in }`
fetch(url: "x")             # completion TACIT
```

The trailing `{ n in }` is not `completion:`. The site that overrode the default completion is classified as a rider. `self.init(driftDelay: 15)` is not a `Thresholds` call (callee is `self`). Documented-adjacent: CANDIDATE already parked unlabeled first; trailing closures are the same class of “Swift that is not a label inside the paren.”

---

## 4. Clap flags — TACIT is a command-shaped line; kizu TACIT=6 is a gold lie (conceptual, load-bearing)

kizu `--all --summary agent` still prints the CANDIDATE table:

```
HookPostTool  agent  "claude-code"  TACIT=6 SHADOW=14 OVERRIDE=4 BOUND=1
HookStop      agent  "claude-code"  TACIT=0 SHADOW=4  OVERRIDE=3 BOUND=1
```

SHADOW / OVERRIDE / BOUND are real hook strings:

- tests restate `--agent claude-code` (SHADOW: a default change will not update installed hooks)
- `install.rs` interpolates `{agent_arg}` (BOUND)
- cline / cursor are OVERRIDE

The **6 TACIT** are not omitted `--agent` on a command that will run:

| file:line | text | why it fired |
| --- | --- | --- |
| `settings_json.rs:15` | doc-comment `"command": "kizu hook-post-tool ..."` | `kizu ` + `command:` + kebab, no `--agent` |
| `settings_json.rs:152` | `// \`hook-post-tool\` from an older kizu install` | `kizu ` in “kizu install” |
| `tests.rs:53` | `.contains("kizu hook-post-tool")` | assertion substring |
| `tests.rs:97` | comment `` `hook-post-tool` `` + `` `kizu init` `` | comment |
| `tests.rs:198` | comment `[kizu hook-post-tool,` | comment |
| `tests.rs:308` | comment `original kizu hook-post-tool` | comment |

`find_clap_uses` searches the **unmasked** source. Comments and strings are the harvest. TACIT is “this line names the kebab and looks command-shaped and does not contain `--flag`”, not “this invocation omitted the flag.” Production install always writes `--agent {agent_arg}`. There is no real clap TACIT rider in kizu.

Fixture holes on the same matcher:

```
--agent claude-code          SHADOW          ok
--agent=claude-code          SHADOW          ok
--agent \"claude-code\"      BOUND  \        first token is the backslash
--agent 'claude-code'        (absent)        quoted values are skipped
kizu hook-post-tool          TACIT           ok for a real omit
please run hook-post-tool    (absent)        documented marker miss
kizu hook-post-tool \        TACIT           multiline lie (§2)
    --agent claude-code
// comment: kizu hook-post-tool …   TACIT    comment
"older kizu install of hook-post-tool"  TACIT

#[arg(long = "agent-id", default_value = "claude-code")] agent: String
--agent-id claude-code       (absent)        flag is the field name, not long =
--agent claude-code          SHADOW HookNamed  wrong callee

kizu timeout --timeout 30    SHADOW timeout "30"
                             TACIT  timeout —     \btimeout\b inside --timeout
```

`default_value_t = 30` *is* harvested (the regex accepts digits). The double row on `--timeout` is the extra lie: the flag token supplies a false TACIT beside the real SHADOW.

CANDIDATE: “Clap TACIT needs a command-shaped line (`kizu ` / `command:`). Prose `kizu hook-post-tool` in README is a miss unless it contains those markers.” Honest about README. Not honest that the 6 TACIT in the dogfood table are riders.

---

## 5. Nested `Thresholds()` — unfold reads the ctor *signature*, not the constructed default (conceptual, load-bearing)

This is the object CANDIDATE claims against `rg` and against sow. Fixture:

```swift
SessionProfile(..., thresholds: Thresholds = Thresholds())
PinProfile(...,    thresholds: Thresholds = Thresholds(driftDelay: 20))
DotInit(...,       thresholds: Thresholds = .init())

SessionProfile(name: "coding")                               # a
SessionProfile(name: "x", thresholds: Thresholds())          # b
SessionProfile(name: "y", thresholds: Thresholds(driftDelay: 15))  # c
SessionProfile(name: "z", thresholds: Thresholds(driftDelay: 20))  # d
PinProfile(name: "p")                                        # e
```

| site | SessionProfile.thresholds | unfold driftDelay | Thresholds() as its own call |
| --- | --- | --- | --- |
| a omitted | TACIT `Thresholds()` | TACIT **15** | (the default expr at the signature is also a Thresholds call) |
| b pass `Thresholds()` | SHADOW `Thresholds()` | **no unfold** | TACIT 15 |
| c pass `Thresholds(driftDelay: 15)` | BOUND (not a literal — `Foo(args)` fails `is_literal`) | no unfold | SHADOW 15 |
| d pass `Thresholds(driftDelay: 20)` | BOUND | no unfold | OVERRIDE 20 |
| e PinProfile omitted | TACIT `Thresholds(driftDelay: 20)` | TACIT **15** | signature default is OVERRIDE 20 as a Thresholds call |

`PinProfile(name: "p")` rides `driftDelay=20`. Unfold reports `thresholds.driftDelay` TACIT **15**. That is a lie about the world the site inhabits. `ctor_name` returns `Thresholds` from any `Thresholds(...)` and unfold walks `Thresholds`’s *init defaults*, not the constructed arguments.

`.init()` does not match `IDENT()`, so `DotInit()` has no unfold at all.

`is_literal` treats empty `Foo()` as a literal and `Foo(driftDelay: 15)` as not. Passing the nested default explicitly is therefore SHADOW of the constructor token (will not follow a SessionProfile default change — correct for the *outer* slot) and is not a SHADOW of `15`. The inner SHADOW exists only because `Thresholds(driftDelay: 15)` is *also* harvested as a `Thresholds` call. Two rows, two callees, for one nested restatement. A filter of `SessionProfile driftDelay` sees site **a** and misses site **c**.

sitbone `SessionProfile.makeDefault()` is `SessionProfile(name: "default", colorHue: 0.45)` — SHADOW hue, TACIT `thresholds`, unfold TACIT `thresholds.driftDelay=15`. That gold is honest. `SessionProfileTests` then `XCTAssertEqual(..., 15)`: CANDIDATE already parked that as echo / zanei, not a SHADOW call. Confirmed not harvested as SHADOW.

---

## 6. Default-moving diffs — same-name move is gold; insert-before-rename poisons pairing (conceptual)

Same-name `presentThreshold 0.45 → 0.50`, five call shapes:

```
BLAST   TACIT      —
FOSSIL  OVERRIDE   0.45
PRE     SHADOW     0.50
LOCK    OVERRIDE   0.99
BOUND   BOUND      provider
```

That is the primitive. `--check` on this tree exits 1 (BLAST present). A FOSSIL-only tree (every caller restated `0.45`, default moved to `0.50`) emits FOSSIL and **`--check` exits 0**. Designed: the gate is riders, not restatements. A default-change PR that pins every site to the old literal is a clean check.

`0.45 → 0.450` and `"hi" → 'hi'` emit no diff rows (`values_equal` via float / unquote). `0.40` after a move from `0.4` is FOSSIL (float-equal to the old default). Honest.

Rename at the **same index** (`threshold=0.4` → `presentThreshold=0.45`):

```
BLAST   TACIT      presentThreshold  0.4→0.45
FOSSIL  OVERRIDE   presentThreshold  0.4→0.45  passed 0.4
```

Insert a slot *before* the renamed one (`threshold` → `absentThreshold, presentThreshold`):

```
BLAST   TACIT      absentThreshold   0.4→0.35     # paired with the old threshold
BLAST   TACIT      presentThreshold  0.45         # born, not 0.4→0.45
LOCK    OVERRIDE   presentThreshold  0.45  0.4    # FOSSIL became LOCK
PRE     SHADOW     presentThreshold  0.45  0.45
```

Position pairing is not “the same slot kept its meaning.” It is “the defaulted name at this index is the old defaulted name at this index, unless that old name still exists.” e9b0f75 inserted `absentThreshold` *after* the renamed slot and kept `emaAlpha`, so index 1 stayed `threshold → presentThreshold` and index 2 was not stolen. The gold commit is order-lucky. The shift fixture is the same Darwin object with the new lower threshold listed first, and FOSSIL dies.

Clap default `"claude-code" → "cursor"`: FOSSIL / PRE / BLAST on the three fixture lines. Diff of clap *works* for unquoted flags.

---

## 7. FOSSIL of old vs new — pairing is load-bearing for FOSSIL, not for e9b0f75 BLAST (gold lie)

CANDIDATE: “Name-only join would report death of `threshold` and birth of `presentThreshold` with no BLAST. Position pairing is load-bearing.”

Patched `pair_renames` to name-only (keep same names, drop index fallback) and re-ran `diff_rows` on sitbone `e9b0f75^..e9b0f75`:

```
paired:    PresenceArbiter rows=54  BLAST=54  FOSSIL=0  defaults: 0.35, 0.4→0.45
name-only: PresenceArbiter rows=54  BLAST=54  FOSSIL=0  defaults: 0.35, 0.45
```

Birth is BLAST (`TACIT and (changed or born)`). Name-only join still emits **BLAST 54**. The only loss is the `0.4→` arrow. There is no FOSSIL on real e9b0f75 either way: no caller restated `0.4`.

The *fixture* rename is where pairing pays rent:

```
WITH pairing:  BLAST presentThreshold 0.4→0.45  —
               FOSSIL presentThreshold 0.4→0.45  0.4
NAME-ONLY:     BLAST presentThreshold 0.45      —
               LOCK  presentThreshold 0.45      0.4
```

Position pairing is load-bearing for **FOSSIL after a rename**. It is not why e9b0f75 is BLAST 54. Calling e9b0f75 the witness that “name-only has no BLAST” is a gold lie. The born-only repo (`init(sensors:)` → `init(sensors:, presentThreshold: = 0.45)`) is BLAST 1 / PRE 1 with no rename at all.

---

## 8. Comments that look like args — line comments are honest; block comments delete the call (conceptual)

```
// PresenceArbiter(sensors: ["camera"], presentThreshold: 0.50)     not a call
PresenceArbiter(sensors: ["camera"]) // presentThreshold: 0.45      TACIT
PresenceArbiter(sensors: ["camera"] /* presentThreshold: 0.50 */)   TACIT
PresenceArbiter(/* presentThreshold: 0.45 */ sensors: ["camera"])   ABSENT
"PresenceArbiter(..., presentThreshold: 0.99)"                      not a call
# greet("x", greeting="yo")                                         not a call
```

`mask` hides line comments and strings from `find_calls`, so residue and string literals do not become OVERRIDE 0.99. `split_top` does not skip `/* */`. A block comment before the first label makes `passed` empty and the Swift “require a label or empty `()`” guard **drops the entire call**. A real TACIT `PresenceArbiter(sensors:)` becomes invisible because of a comment that looks like an arg.

---

## 9. sitbone e9b0f75 / kizu / tenaoshi gold — three truths, two lies, one false call

### sitbone holds

```
./tacit -C sitbone --all --summary presentThreshold
PresenceArbiter  presentThreshold  0.45  TACIT=27  SHADOW=0  OVERRIDE=0  BOUND=0

./tacit -C sitbone --git e9b0f75^ e9b0f75 --summary PresenceArbiter
BLAST 54
PresenceArbiter  presentThreshold  27
PresenceArbiter  absentThreshold   27
```

`SitboneCore.swift:68` is TACIT. Every hysteresis test is `PresenceArbiter(sensors:, emaAlpha: 1.0)` — OVERRIDE `emaAlpha`, TACIT both thresholds. The tests document `0.45` in comments and in the `0.40` middle-band stimulus. The call does not lock the default. `SessionProfile.makeDefault()` is SHADOW `colorHue 0.45`. `--check` on e9b0f75 exits 1.

27+27=54 counts the born `absentThreshold` as BLAST. Advertised. Not a lie.

The lie is the pairing story (§7), not the count.

### kizu TACIT=6 is not six riders

See §4. SHADOW=14 / OVERRIDE=4 / BOUND=1 survive.

### tenaoshi wrapper signature is a false TACIT

```
SHADOW  prod  reopenUnit  returningToFinal  true  true  ReviewSession.swift:267
TACIT   test  reopenUnit  returningToFinal  true  —     ReviewSessionTests.swift:98
TACIT   prod  reopenUnit  returningToFinal  true  —     PanelSession.swift:623
TACIT   prod  reopenUnit  returningToFinal  true  —     PanelSession.swift:624
TACIT   prod  reopenUnit  returningToFinal  true  —     PanelView.swift:421
```

`:267` is `reopenUnit(id: id, returningToFinal: true)` inside `reopenFocusedFinalUnit` — real SHADOW. `:624` and `:421` are real TACIT. `:623` is

```swift
func reopenUnit(id: String) {
    review?.reopenUnit(id: id)
}
```

v0.2 skips *the harvested signature paren* (`reopenUnit(id:, returningToFinal: = true)` at `:270`). A wrapper with the same name and no default is a call. `id: String` looks like a labeled arg; `returningToFinal` is omitted → TACIT. demo.sh asserts “signature not a call” by grepping `Bool = true`, which only the harvested sig contains. `:623` is not in that grep. Fixture `wrap.swift` reproduces: `func reopenUnit(id: String)` is TACIT.

---

## 10. Overload merge / `values_equal` — first default wins (survived as honesty-adjacent)

```swift
init(width: Double = 10)
init(width: String = "10")
Box()            TACIT 10
Box(width: 10)   SHADOW
Box(width: "10") SHADOW   # unquote + float
Box(width: 20)   OVERRIDE
```

`merged_params` keeps the first default seen. `"10"` SHADOWs `10`. Not a sitbone-shaped object (the two PresenceArbiter inits share the same numeric defaults). `values_equal("True","true")` is false; `None` ≠ `nil`. Cross-language comparison is not the product.

---

## What survived

- sitbone `presentThreshold`: 27 TACIT, 0 SHADOW. Hysteresis rides 0.45. Production `SitboneCore.swift:68` rides it.
- sitbone `e9b0f75`: BLAST 54, `--check` rc=1. `0.4→0.45` on `presentThreshold`, born `absentThreshold=0.35`.
- `SessionProfile.makeDefault()` SHADOW `colorHue 0.45`.
- Same-name default move: BLAST / FOSSIL / PRE / LOCK / BOUND, one row each.
- Rename-at-same-index fixture: BLAST + FOSSIL with `0.4→0.45`.
- `0.45→0.450` and `"hi"→'hi'` are stable (no false BLAST).
- `0.40` is FOSSIL of `0.4`.
- Python keyword/positional mix without `*args`.
- Multiline labeled Swift, including `//` between label and value.
- Line-comment residue and string-literal fake calls are not OVERRIDE.
- kizu SHADOW / OVERRIDE / BOUND of `--agent`.
- tenaoshi `:267` SHADOW `true`, PanelView TACIT.
- `--selftest` 33/33. `./demo.sh` 32/32. No rewrite.

---

## Kill / keep

**Keep. Mutate. Do not rewrite in this pass.**

The object is still “this site omitted a default / restated it / overrode it / bound it,” and “this default moved; these riders BLAST, these restatements are FOSSIL.” sitbone 27/54, hysteresis, `makeDefault` SHADOW, and the five-way same-name diff still name that object. Killing tacit because clap TACIT is a line regex, or because unfold does not parse `Thresholds(driftDelay: 20)`, would throw away the only verb that distinguishes two inhabitants of `0.45`.

| do not kill because | mutate toward |
| --- | --- |
| sitbone 27 TACIT / 0 SHADOW; e9b0f75 BLAST 54 rc=1; same-name BLAST/FOSSIL/PRE/LOCK/BOUND; makeDefault SHADOW hue | **Unfold the constructed default, not the ctor signature.** `PinProfile` default `Thresholds(driftDelay: 20)` is OVERRIDE 20, not TACIT 15. `.init()` should unfold or be parked as un-unfoldable (already listed). |
| | **Passing `Thresholds(driftDelay: 15)` is SHADOW of the nested slot**, not BOUND of the outer token. Filter `SessionProfile driftDelay` must see it. |
| | **Clap TACIT is an invocation that omitted `--flag`, not a command-shaped line.** Mask comments. Do not TACIT `contains("kizu hook-post-tool")`. Bind `--flag` to the nearest subcommand across `\` continuations. Use `long =` as the flag. Quoted `--agent "claude-code"` is SHADOW. `--timeout` is not a tacit mention of `timeout`. kizu TACIT=6 should become 0. |
| | **Signature-skip is every `func reopenUnit(`, not only the defaulted sig.** tenaoshi `:623` is not a call. |
| | **`*args` / `**kwargs` do not occupy positional slots.** `splat(1)` is TACIT `timeout`. TS does not have `name =` keywords; `delay = 200` is positional. |
| | **`paint("red")` is TACIT of every defaulted labeled slot** after an unlabeled first. Do not drop the call. |
| | **Pairing is identity of a defaulted slot, not index.** Insert-before-rename must keep FOSSIL on `presentThreshold: 0.4`. e9b0f75 BLAST does not need pairing (birth already BLASTs); stop claiming it does. Pairing stays for FOSSIL-after-rename. |
| | **Block comments are not unlabeled args.** `/* presentThreshold: 0.45 */ sensors:` is still a call. |
| | Trailing closures bind the last defaulted function-typed slot, or stay parked with unlabeled first. `--check` can stay rider-only; FOSSIL-only rc=0 is defensible. |

A one-line “skip `#` in `split_top`” would hide the Python BOUND and would not touch clap TACIT=6, PinProfile 15, or `*args`. Not applied.

Do not grow a review platform. The next mutation is *honest omission of a nested constructed default* plus *clap invocations not command-shaped lines*, not a prettier TSV.
