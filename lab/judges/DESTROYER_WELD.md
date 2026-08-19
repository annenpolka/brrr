# DESTROYER — weld

Adversarial pass on the expr-first concat stream filter. No rewrites: the failures are conceptual, not one-line bugs. Coordinator banned a second inverse-printf walker / rustc parser; this pass attacks the stream filter.

- **weld** (mutation-59, v0.2.0) — `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01b85-3a6f-77f2-a6bf-caff208a0972`
- Lineage: `lab/lineages/mutation-59__weld/`
- Peels: rime (mutation-79 leftover bind), caulk (mutation-91 complete leftover operand)
- Prior: DESTROYER_PIN_INVERT, DESTROYER_STUMP_PIN (concat as sibling of invert/stump)
- Transcript: `/tmp/destroy-weld/transcript.txt`
- Fixtures / driver: `/tmp/destroy-weld/fixtures/`, `/tmp/destroy-weld/attack.py`
- `./weld --selftest` → `selftest: ok` before and after the attacks. weld 0.2.0. Victim not rewritten.

Attacks: `cleaned + "\n"`, fence `"```json\n"`, one-hole every-log-line, middle-drop stuffing, truncated leftovers, `fmt.Sprint` vs `+`, Swift wrap lookback, `MAX_FILE_BYTES` silent omit, dynamic format / Join / `push_str`.

Verdict: **mutate, do not kill.** The flipped assumption is still visible. splice misses `response() + "\nDone."`; weld binds `{response}`. tenaoshi wrapped `+` is still one 4-hole splice. The attacks show where proving-string-backward pretends to be inverse-printf of concat, leftover, prefix-of-instance, and Sprint.

---

## Primitive restated

Inverse printf as a stream filter whose concat template may **start at an expression**. A later string operand proves the chain. Names bind. Truncation is a **prefix of an instance**. Middle-drop stuffing is a miss. The wrap is a gap, not a stop. rustc locators refused. No walk.

The extractor welds **backward from a proving string** through `+` / `<>` / `fmt.Sprint`. That is the mutation. It is not a leftover consumer (rime/caulk), not `strings.Join` / `push_str`, and not “every quoted import is a log line.”

---

## Controls that survived (do not kill for these)

```
$ ./weld --selftest
selftest: ok

$ ./weld --templates fixtures/src/concat.js $'{"ok":true}\nDone.'
  tmpl:  {response}\nDone.
  {response} = {"ok":true}

$ ./weld --templates fixtures/src/concat.swift $'```json\n{"ok":true}\n```'
  tmpl:  ```json\n{response}\n```
  {response} = {"ok":true}

$ ./weld --templates fixtures/src/concat.go 'failed read with EPERM'
— no template for: failed read with EPERM   # rc=1  (3-hole later witness)

$ ./weld --templates fixtures/src/prefix.rs -e '   --> src/git/revert.rs:46:18'
— rustc locator, not a template query

$ ./weld --templates fixtures '…'
weld: refusing to walk directory   # rc=2
```

Dogfood, same object:

| paste | result |
| --- | --- |
| tenaoshi `response() + "\nDone."` | `{response}={"ok":true}` |
| tenaoshi `"Here is the plan:\n" + response()` | `{response}={"ok":true}` |
| tenaoshi wrap `source graphemes` | 4-hole `{unitID}=u1` `{start}=3` `{end}=8` `{sourceGraphemeCount}=12` score=1.08 |
| tenaoshi full fence | `{response}={"ok":true}` |
| kizu `--> src/git/revert.rs:46:18` | refused |
| kizu timestamp + spawn | span `prefix: 2026-08-19T23:50:01Z ERROR ` |

A one-line `if truncated and not bindings: return None` would not touch sibling-template stuffing, leftover `\nDone.`, Sprint spaces, or `MAX_FILE_BYTES`. Not applied.

---

## 1. `cleaned + "\n"` — leftover-only concat is invisible; hydrate floods the file (conceptual, load-bearing)

CANDIDATE already lists newline-only suffix as a miss. Confirmed, and the miss is the other half of “do not match every log line.”

kizu `src/init/teardown.rs:86`:

```
std::fs::write(&hook_file, cleaned + "\n")?;
```

```
$ rg -n -g '*.rs' 'cleaned \+' kizu | ./weld --templates - --extract
# hydrates the whole file. 30+ string literals.
# teardown.rs:15 holes=0 static=13 kizu teardown
# teardown.rs:98 holes=1 static=0 {1}
# no weld {cleaned}\n

$ … | ./weld --templates - $'keep\n'
— no template for: keep   # rc=1

$ … | ./weld --templates - --open never --extract
teardown.rs:86:1: lang=rust holes=0 static=43 std::fs::write(&hook_file, cleaned + "\n")?;
```

The proving string is `"\n"`. `emit` drops spliced one-hole templates with `visible < 4`. That is why `{cleaned}\n` is not a template. `--open never` does not recover the concat: extract_templates finds nothing worth emitting, then `fragment_to_template` publishes the **source statement** as a no-hole log line.

skills `JsonSerializer.Serialize(entry) + "\n"` is the same object. `--open never` extracts `debug.log` (the other string on the line). Query `{"h":"H1"}\n` misses.

sitbone `fields.joined(separator: ",") + "\n"` is Join + newline. Hydrate of `joined(separator` slurps CSV header names (`timestamp`, `camera_present`, …) and `presence_{timestamp}.csv`. The `+ "\n"` chain is absent.

rime/caulk exist because leftover `\n` after a contentful bind is inverse-printf and a fresh line is not. weld cannot be both. Lowering `visible < 4` so `{cleaned}\n` extracts would make every log line a hit (see §3). That is a sibling (rime), not a patch.

`normalize_query` strips the proving newline off argv:

```
$ ./weld --templates concat.js $'\nDone.'
— no template for: Done.   # rc=1
```

Same on tenaoshi `Done.` leftover. Full `{"ok":true}\nDone.` still binds (control). Truncated proving string `{"ok":true}\nDon` also misses — caulk’s complete-operand refuse, accidental on weld because `\nDone.` is not a prefix long enough for `MIN_STATIC_PREFIX=10`.

---

## 2. Fence `"```json\n"` — full paste holds; incomplete fence is a truncated success (conceptual)

v0.2 kept escaped trailing newlines. Full tenaoshi fence still binds.

```
$ rg -n -g '*.swift' json tenaoshi/Engine/Tests \
    | ./weld --templates - $'```json\n{"ok":true}\n```'
  tmpl:  ```json\n{response}\n```
  {response} = {"ok":true}    # rc=0
```

The closer is optional under truncation:

```
$ … | ./weld --templates - $'```json\n{"ok":true}'
  tmpl:  ```json\n{response}\n```
  {response} = {"ok":true}
  truncated: \n```            # rc=0
```

That is not a prefix of an instance missing a hole. It is a proving **operand** cut in half (`"\n```"`). caulk refuses leftover `\nDon` of `\nDone.` as not a complete operand. weld accepts the analogous fence cut as inverse-printf.

Body-only `{"ok":true}` misses (honest: no proving static). Closer-only `\n```` strips to ` ``` ` and misses.

Split operands `"```json" + "\n" + response() + "\n" + "```"` still weld into one template (the scanner concatenates adjacent string operands). Unclosed `"```json\n" + response()` extracts `{response}` with no closer; a complete fenced paste then binds `{response}` to `{"ok":true}\n```` — the closer stuffed into the hole.

---

## 3. One-hole every-log-line — the 4-char floor is the product’s footgun (conceptual, lethal to “a proving string”)

Newline-only is refused so that `{x}\n` does not match every line. The floor is `visible >= 4` for one-hole splices, and **no floor that matters** for two-hole leading welds (`match_template` allows `static >= 1` when `holes >= 2` and `parts[0] == ""`).

```
# thin.go
cleaned + "\n"     # not extracted
body + "\nOK"      # not extracted (visible 2)
body + "abcd"      # weld {body}abcd
a + ":" + b        # weld {a}:{b}  static=1
"open " + path     # splice open {path}
```

```
$ ./weld --templates thin.go 'ERROR worker crashed abcd'
  tmpl:  {body}abcd
  {body} = ERROR worker crashed     # every log line ending abcd

$ ./weld --templates thin.go 'https://example.com:443'
  tmpl:  {a}:{b}
  {a} = https
  {b} = //example.com:443           # every colon line
```

CANDIDATE: “The proving string can be short (`": "`) if there are two expression holes.” That is `{path}: {err}` — and also `{a}:{b}` on a URL.

The fixture 1-hole `"open " + path` is the same class:

```
$ ./weld --templates concat.go 'open the pod bay doors'
  tmpl:  open {path}
  {path} = the pod bay doors        # score=0.67 via=full
  tmpl:  open {path}: {err.Error}
  {path} = the pod bay doors
  truncated: : {err.Error}          # also a hit
```

Go import paths are proving strings too. concat.go line 4 is `"errors"`:

```
$ ./weld --templates concat.go errors
concat.go:4:2: score=1.00 holes=0 via=full
  tmpl:  errors
```

v0.2 dropped a leading-hole weld that is a suffix of a longer splice **on the same paste**. It still hits when the longer splice is not in the stream (rg of `path + ": "` only, or `--extract | rg weld`):

```
$ ./weld --templates concat.js --extract | rg weld \
    | ./weld --templates - --from index 'open /tmp/x: permission denied'
  tmpl:  {path}: {err}
  {path} = open /tmp/x              # the DESTROYER_STUMP_PIN decoy, back
```

Alone, `/tmp/x: permission denied` is the honest tail weld. The ranking fix is occupancy of the longer template, not a property of the extractor.

---

## 4. Middle-drop stuffing — fixture 7-hole / 3-hole miss; sibling templates and 2-hole still stuff (conceptual, lethal to the pitch)

lede’s kernel: later statics that appear inside the would-be hole refuse the match. Fixture `failed {op} on {path} with {err}` vs `failed read with EPERM` still misses (`" with "` is a later witness in the rest). Demo `awayRecovered=0` vs the **7-hole** fixture still misses.

That check is **template-local**. A shorter sibling that does not contain the dropped tail still stuffs.

Real sitbone `SitboneCore.swift` has three `transition … → …` loggers. rg `awayRecovered` hydrates the file. Query `transition focused → idle awayRecovered=0`:

```
SitboneCore.swift:562 score=0.71 holes=2/5 via=truncated
  tmpl:  transition {oldPhase.rawValue} → {newPhase.rawValue} reason={reason.name} duration={duration}s …
  {oldPhase.rawValue} = focused
  {newPhase.rawValue} = idle awayRecovered=0     # stuffed
  truncated:  reason={reason.name} duration=…

SitboneCore.swift:569  same stuffing into the site= sibling
# 7-hole line 554 is absent: later witness awayRecovered= fired
```

The 7-hole refuse is real. The dogfood stream still **exits 0 with a wrong binding**, because the duration=/site= siblings share the prefix and do not mention `awayRecovered`. DESTROYER_STUMP_PIN’s lethal middle-drop is closed on the fixture and open on the tree the fixture was copied from.

Same kernel, 2-hole concat without a later witness in the rest:

```
# "failed " + op + " on " + path
$ ./weld --templates twohole.go 'failed read /tmp/x'
  tmpl:  failed {op} on {path}
  {op} = read /tmp/x
  truncated:  on {path}             # rc=0
```

`user 42 found` vs `user {uid} not found` is not a prefix of any instance (`user 42 not found`). Later witness is `" not found"`, which is **not** in `"42 found"`, so:

```
  {uid} = 42 found
  truncated:  not found             # rc=0
```

Truncation still means “static literals that are present, in order,” not “query is a prefix of an instance.”

---

## 5. Truncated leftovers — remainder is the rest of the *same* template; extra suffix is silent (conceptual)

Prefix truncation of the 7-hole still binds names (control). The printed `truncated:` field is `deserted={0}…` — rest of this template, not a next concat. Consuming it as leftover would be leftover-name search. rime/caulk refuse it. weld cannot reconstruct `"\nDone."` from it either.

Holed templates accept extra trailing text up to `max(24, static)` and do not print it:

```
$ ./weld --templates user.py 'user 42 not found today'
  tmpl:  user {uid} not found
  {uid} = 42
  via=full                          # no suffix= note
```

Empty hole scores **0.94**: `user  not found` → `{uid}=`. JSON wrap is span leftover (`prefix: {"msg":"`) — invert harvest, not a new lie.

`--any` still stops on the first truncated hit:

```
$ { echo 'user 42 not'; echo 'ERROR [worker] user 7 not found'; } \
    | ./weld --templates user.py --any
  {uid} = 42
  truncated:  found                 # second line never read
```

`--any --complete` is the advertised knob and still works (demo). Default `--any` is a probe that stops on the false-positive class in §4–§5.

Leading-hole leftover as a fresh query is stripped (`$'\nDone.'` → `Done.`). `"Here is the plan:\n" + response()` binds the full paste and misses the body leftover `{"ok":true}`. That is rime’s object.

---

## 6. `fmt.Sprint` vs `+` — Sprint is not concat (conceptual)

Go spec: Sprint adds spaces **when neither operand is a string**. Sprintln **always** adds spaces and a newline.

```
fmt.Sprint(1, 2, " items")  →  "1 2 items"     # go run
fmt.Sprintln("open ", "/tmp/x") → "open  /tmp/x\n"
fmt.Sprint("open ", "/tmp/x") → "open /tmp/x"
```

weld extracts Sprint as a `+` chain:

```
$ ./weld --templates sprint.go --extract
sprint.go:3:34: holes=2 static=6 weld {n}{m} items     # no space
sprint.go:4:37: holes=1 static=5 splice open {path}    # Sprintln: no extra space, no \n
```

Actual runtime vs template:

```
$ ./weld --templates sprint.go '1 2 items'    # what Go prints
  tmpl:  {n}{m} items
  {n} = 1 2 items
  unbound: {m}                    # greedy first of two leading holes

$ ./weld --templates sprint.go '12 items'     # what the template looks like
  {n} = 12 items
  unbound: {m}
```

Neither query binds `{n}=1` `{m}=2`. Adjacent empty parts collapse to one hole.

Sprintln actual `open  /tmp/x` hits `open {path}` with `{path}= /tmp/x` (leading space stuffed). The `+` runtime `open /tmp/x` also hits. The template cannot tell them apart.

`fmt.Fprint` / `strings.Join` / `strings.Builder.WriteString` are not operators. Fprint leaves `"open "` and `": boom"` as separate no-hole fragments. Query `open /tmp/x: boom` then ranks `open {path}` with `{path}=/tmp/x: boom` over the expr-first `{path}: {err}` (`{path}=open /tmp/x`). Join of `"open ", path, ": ", err` extracts `"open "` only; the runtime paste misses.

---

## 7. Swift wrap — gap within `MAX_WELD_LOOKBACK=4000`; beyond that, splice’s suffix leak returns (conceptual)

tenaoshi `EditPlanComposer.swift:70` wrap is still one 4-hole splice (control). Same-line comment between two unrelated concatenations does **not** weld them (`{foo}AAA_UNIQUE` and `{bar}BBB_UNIQUE` stay two templates).

250 comment lines (~5k) between `body +` and the proving string:

```
$ ./weld --templates lookback.go --extract
lookback.go:254:5: lang=go holes=0 static=18 \nLOOKBACK_UNIQUE.
# no weld {body}…

$ ./weld --templates lookback.go $'payload\nLOOKBACK_UNIQUE.'
— no template for: payload
LOOKBACK_UNIQUE.                  # rc=1
```

The flipped assumption is “wrap is a gap.” It is a gap of at most 4000 bytes looking backward from the proving string. Past that, weld is splice: suffix literal leaks as holes=0, expr-first paste misses. A one-line raise of `MAX_WELD_LOOKBACK` moves the cliff. A walker would not have one.

`obj["k"] + ": " + obj["e"]` extracts `{obj}: {obj}` — both holes named from the identifier prefix, subscripts dropped. `arr[0]` keeps the index. `foo + bar + "END"` extracts `{foo}{bar}END`; query `hello worldEND` binds `{foo}=hello worldEND`, `{bar}` unbound (same empty-part collapse as Sprint).

---

## 8. `MAX_FILE_BYTES = 2_000_000` — silent omit of a source file; raw ingest has no ceiling (conceptual, same class as DESTROYER_STUMP_PIN §7)

`extract_from_file`: `st.st_size > MAX_FILE_BYTES` → `[]`, no stderr.

```
godfile_bytes 2100000   # unique concat on line 2: prefix + ": GODFILE_WELD_UNIQUE " + err

$ ./weld --templates godfile.go --extract
# no lines

$ ./weld --templates godfile.go '/tmp/x: GODFILE_WELD_UNIQUE permission denied'
weld: 0 templates ingested
— no template for: …              # rc=1
```

1.85 MB sibling with the same unique concat extracts and binds `{prefix}=/tmp/x`. The cutoff is a hard omit, not a warning. kizu-scale generated source as `--templates` goes quiet.

`--from raw` on a 2.1 MB `extracted.txt` **does** hit (`open {path}: {err}`). The ceiling is `extract_from_file` on a source suffix, not ingest. A concatenated extract lives; a godfile `.go` dies. Pin raised this class and added a mint-target fallback. weld still omits.

---

## 9. Dynamic format strings remain invisible; `push_str` is not `+` (conceptual, acknowledged)

```
fmt.Sprintf(msg, args...)     # 0 templates ingested
format!(fmt, x)               # 0 templates
```

kizu `untracked.rs` builds a binary diff with three `push_str`s:

```
out.push_str("Binary files /dev/null and b/");
out.push_str(&display);
out.push_str(" differ\n");
```

Extract (after hydrate) is two no-hole fragments `"Binary files /dev/null and b/"` and `" differ"`. Query of the joined runtime misses:

```
$ rg -n -g '*.rs' 'Binary files' kizu/src \
    | ./weld --templates - 'Binary files /dev/null and b/src/x.rs differ'
— no template for: Binary files /dev/null and b/src/x.rs differ   # rc=1
```

`strings.Join` / `fmt.Fprint` / `push_str` are the sibling operators CANDIDATE already named. Not a walker. Not a one-line `+` patch.

Compiler *messages* still bind; only locators are refused (`error: {e}` → `{e}=mismatched types`; `src/{i}.rs` → `{i}=git/revert`). Same DESTROYER_STUMP_PIN §4.

---

## What survived

- `response() + "\nDone."` is `{response}\nDone.` on concat.js and on tenaoshi EditPlanParserTests.swift:318.
- `"Here is the plan:\n" + response()` binds on the full paste.
- Full fence `"```json\n" + response() + "\n```"` keeps the escaped newline (v0.2 hold).
- tenaoshi wrap `source graphemes` is one 4-hole splice, names `unitID` / `start` / `end` / `sourceGraphemeCount`.
- Fixture 3-hole `failed read with EPERM` still misses; fixture 7-hole middle-drop still misses.
- rustc `-->` / `error[E0308]` refuse on fixtures and on kizu `format!|anyhow!` streams.
- Directories still exit 2. Binary stdin still fail-closed (not re-broken).
- kizu timestamp span on `failed to spawn` still reports `prefix:`.
- `--selftest` ok after the battery. Victim untouched.

---

## Kill / keep

**Keep. Mutate. Do not rewrite in this pass.**

The object is still “concat may start at an expression; a later string proves it.” splice’s `holes=0 static=6 \nDone.` miss is closed. tenaoshi wrap is still one template. Killing weld because leftover `\n`, sibling-template stuffing, or Sprint spaces would throw away the proving-string-backward verb to hide a leftover consumer, a prefix-of-instance kernel, and a third operator family.

Do not grow a rustc parser. Do not start the scanner at every identifier. Do not leftover-name search `deserted={0}`. Do not lower `visible < 4` so `{cleaned}\n` matches every log line. Do not hide wrap with a one-line no-bindings guard.

| do not kill because | mutate toward |
| --- | --- |
| expr-first `{response}\nDone.` on fixture + tenaoshi; full fence keeps `json\n`; 4-hole wrap; locator refuse; 3-hole fixture middle-drop miss | **Leftover proving strings are a different filter** (rime/caulk already peeled this). Fresh-line weld must keep refusing `{x}\n`. Do not strip a leftover newline and call concat done. |
| | **Truncation is a prefix of an instance**, not leftover-into-the-last-hole. Sibling templates that share `transition {from} → {to}` must not stuff `awayRecovered=0` into `{to}` while the 7-hole honestly misses. 2-hole `failed {op} on {path}` vs `failed read /tmp/x` is the same lie. `user 42 found` is not a prefix of `user {uid} not found`. Incomplete fence `\n```` is not a complete operand. |
| | **A 4-char suffix / 1-char two-hole is not inverse-printf.** `{body}abcd` and `{a}:{b}` on URLs are every-log-line. `{path}: {err}` as a *suffix* of `open {path}: {err}` must not hit `open /tmp/x: …` just because the longer splice was not in this stream. Import `"errors"` is not a log template. |
| | **Sprint is not `+`.** Spaces between non-strings, Sprintln always-space+newline. `fmt.Fprint` / `strings.Join` / `push_str` are sibling operators, not a walker. Adjacent empty parts must not collapse to `{n}=1 2 items`. |
| | **Wrap-as-gap needs a bound that is not a silent splice regression.** 4000-byte lookback leaking `\nLOOKBACK_UNIQUE.` as holes=0 is the ancestor miss. Warn (or slurp) `MAX_FILE_BYTES`; raw ingest already has no ceiling. |
| | Compiler *messages* / path format strings remain a different grammar. Dynamic `Sprintf(msg, …)` stays invisible until a sibling that is still a stream filter. |

A one-line `print("weld: skipped huge file")` on `MAX_FILE_BYTES` would hide §8 and would not touch sitbone sibling stuffing, leftover `\nDone.`, or Sprint. Not applied.
