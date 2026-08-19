# DESTROYER — zanei × nagori

Adversarial pass on leftover-*claims* (not leftover names). No rewrites: the failures are conceptual, not one-line bugs.

- **zanei** (残影, candidate-07) — `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01a85-796f-76d0-988f-5c00e96ceb84`
- **nagori** (名残, reimpl-03) — `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01b0f-7ef0-76c0-9975-2cffa17ef5e5`
- Transcript: `/tmp/destroy-zanei-nagori/transcript.txt`
- Follow-up: `/tmp/destroy-zanei-nagori/followup.txt`
- Fixtures: `/tmp/destroy-zanei-nagori/fixtures/`
- Both `self-test` still exit 0 after the attacks.

Attacks: huge diffs, generated files, version numbers in dates, homonyms, polarity true/false, unicode, nested git, empty diff, binary files, JSON-only hunks.

Verdict: **mutate both, do not kill.** The object is still “this diff made a fact false; the dest tree still asserts it.” Complementary holes: zanei cannot *see* a JSON-only fact; nagori can see it and then *throws away* the prose leftover of that fact.

---

## Shared

Primitive restated: a *fact* is a bound name/value, rename, or polarity flip from a unified diff. An *afterimage* is a dest-tree line that still asserts the old fact. Exit `0` clean, `1` leftovers, `2` error.

### 1. Version numbers in dates — month 10 is a leftover timeout (conceptual)

`HOOK_TIMEOUT = 10 → 30`. Dest changelog:

```
## timeout
shipped 2024-10-01
```

Needle for `10` is `(?<![\d.])10(?![\d.])`. A hyphen is not a digit. October is a hit.

```
$ ./zanei --no-color --explain -C $DATES
zanei: 2 afterimages  HEAD → worktree

FACT HOOK_TIMEOUT: 10 → 30   src/config.py:1
   76 docs    CHANGELOG.md:4   shipped 2024-10-01
         why: nearby-name, name-stem, old-value, claim:docs

FACT MAX_RETRIES: 3 → 8   src/config.py:2
   62 docs    docs/dates.md:2  retries=3 landed 2024-03-01.

$ ./nagori --no-color --explain -C $DATES
nagori: 3 afterimages
FACT HOOK_TIMEOUT: 10 → 30
   76 docs    CHANGELOG.md:4   shipped 2024-10-01
   62 docs    docs/dates.md:1  hook timeout default was documented the day we shipped, 2024-10-01.
FACT MAX_RETRIES: 3 → 8
   62 docs    docs/dates.md:2  retries=3 landed 2024-03-01.
```

Isolated `HOOK_TIMEOUT` hunk against the same dest: both still flag `2024-10-01`. `3` does **not** match `2024-03-01` (leading zero); `0.3.0` does **not** match `2024.03.01` (version-dot boundary). The hole is specifically **small integers inside hyphenated ISO dates**, plus a heading that supplies the name (`## timeout` → `nearby-name`).

A one-character class add (`[\d.\-]`) would hide October and would not decide what a date is. Not applied.

`BUILD_DATE = "2024.03.01" → "2024.08.20"` extracts as a version-shaped value in both parsers. Dates *are* facts if you bound them. The failure is treating a *calendar component* as the old bound literal of a different name.

### 2. Generated files — vendor is skipped, `generated/` is a believer (conceptual)

`SKIP_DIRS` has `vendor` and `dist`. It does not have `generated/`. Leftover `const MAX_RETRIES = 3` in a “do not edit” bundle scores like a forgotten claim:

```
$ ./zanei --no-color --explain -C $GENERATED
zanei: 4 afterimages

FACT MAX_RETRIES: 3 → 8   src/config.py:1
   72 code    generated/vendor_bundle.js:2   const MAX_RETRIES = 3;
   62 docs    README.md:1                    retries 3, timeout 10

FACT TIMEOUT: 10 → 30
   62 docs    README.md:1
   56 string  generated/vendor_bundle.js:3   console.log('timeout', 10);

$ ./nagori … 
nagori: 3 afterimages     # same MAX_RETRIES vendor_bundle.js:2 at 72; no string hit
```

`vendor/pkg.js` and `dist/out.js` (identical leftovers) are invisible. The directory name is the policy. A regenerated oracle is not a leftover *claim*; it is a leftover *build*. The primitive cannot tell.

Facts extracted **from** a minified generated hunk: nagori emits `TIMEOUT` + `MAX_RETRIES` rename/value off one `!function(e){var MAX_RETRIES=3,…` line. zanei emits only `TIMEOUT`. One-liners are a different grammar. Not a hang; a firehose waiting for a real vendor diff.

### 3. Binary — NUL is refused, high bytes are claims, stdin crash is exit 1 (operational + conceptual)

NUL in the first 4k/8k: skipped (honest). UTF-16: skipped. A `.dat` with leftover ASCII and **no NUL** in the prefix is decoded as text:

```
FACT TIMEOUT: 10 → 30   src/config.py:1
   72 code    data/nonul.dat:1   TIMEOUT = 10 leftover     # both tools
```

`--diff -` + 8k urandom:

```
$ dd if=/dev/urandom bs=8192 count=1 | ./zanei --diff - -C $BINARY
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xab in position 1
# rc=1

$ … | ./nagori --diff - -C $BINARY
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xc6 …
# rc=1
```

Exit `1` is the **linter-positive**. A crash is “afterimages found.” `--diff FILE` that is binary: zanei crashes the same way (`read_text(encoding="utf-8")`); nagori `errors="replace"`s and reports `no fact mutations` (rc=0). Git’s `Binary files a/x and b/x differ` is honest silence in both.

A `decode(..., "replace")` or `die(..., 2)` is a small robustness patch, not a primitive fix. Left unpatched: refuse vs replace is a design choice, and exit-1-means-dirty makes the choice load-bearing.

### 4. Fullwidth and Japanese *as the binding* — aliases only search, they do not parse (conceptual)

ASCII `TIMEOUT = 10 → 30`, leftover `TIMEOUT = １０`:

```
zanei: 0 afterimages   1 fact(s) changed; none left an afterimage (min-score gated).
nagori: 0 afterimages  1 fact(s) changed; none left an afterimage (min-score gated).
```

`needle_in_line("10", "TIMEOUT = １０")` is False. The afterimage is sitting on disk in the same digits a human would read.

`タイムアウト = 10 → 30` as the **changed line**: **0 facts** in both. `IDENT_RE` is ASCII. The alias table (`timeout ↔ タイムアウト`) only fires when the *fact name* is already English and the leftover line contains the Japanese stem. Confirmed the other way: ascii `timeout = 10 → 30` **does** hit `タイムアウトは 10 秒です` (score 62, `name-stem`) in both.

Unicode *filenames* (NFC `café.py`, `docs/日本語.md`, `docs/emoji 🌀.md`) round-trip. NFD `src/café.py` in a `--diff` header still extracts `timeout` and searches the NFC tree. Paths are not the hole. Bindings are.

### 5. Nested git — worktree walk works; historical dest is a commit tree (documented, confirmed)

Uncommitted parent `TIMEOUT = 10 → 30`, leftover only in a nested repo:

```
   62 docs    nested/inner/note.md:1   # nested still says timeout is 10    # both
```

`HEAD~1 HEAD` (dest = `git ls-tree` of the parent commit): nested file gone. Both report only `README.md`. Historical trees do not recurse inner worktrees. CANDIDATE already says this. It is still the case that a leftover *only* inside a nested checkout is invisible to the linter shape `zanei A B`.

### 6. Empty diff — honest

Empty stdin, newline-only stdin, clean `HEAD`→worktree: both `0 afterimages` / `no fact mutations` / rc=0. `Binary files differ` same. Not a walk. Survived.

### 7. Huge diffs — prose remames stay dead; godfiles go silent (conceptual omit)

400-line `Exit`/`Patch`/`request`/`experiment` rewrite (48 KB hunk): **0 facts** both (5.5s / 7.8s). v2 inflection filter holds.

200 leftover docs + a 2-line source hunk: 602 afterimages both. zanei 0.09s, nagori 2.52s. Completes. Not a hang.

Size cap (nagori `MAX_FILE_BYTES = 1_048_576`, zanei `1_500_000`), leftover **only** in the big file:

| file | bytes | zanei | nagori |
| --- | ---: | --- | --- |
| `docs/ok.md` | 720_029 | hit 84 | hit 84 |
| `docs/mid.md` | 1_260_029 | **hit 84** | **omit**, rc=0, “min-score gated” |
| `docs/god.md` | 1_860_029 | omit | omit |

No warning. The leftover is the only believer. Exit 0. nagori’s gated message is a lie: the file was never scored. Same class as pin’s 1 MB godfile omit.

### 8. Polarity table is a comment — unquoted YES/NO, on/off, present/absent extract nothing

zanei’s `POLARITY` dict lists `yes/no`, `on/off`, `present/absent`, `enable/disable`. PAIR_RE’s bool group is `true|false|True|False|YES|NO|…`. `FLAG = YES → NO`, `mode = on → off`, `state = present → absent`: **[] facts both**. Quoted `"present" → "absent"` works. The table does not bind what the regex cannot see.

---

## zanei

### 1. JSON-only hunks are not facts (conceptual, lethal to the JSON side of the pitch)

The gold kizu finding is “crate `0.3.0` → `0.7.0`, plugin still `"version": "0.3.0"`.” That fact is supplied by **unquoted** `version = "0.3.0"` in Cargo.toml. A plugin-manifest hunk alone:

```
$ cat kizu-plugin.diff   # "version": "0.3.0" → "0.7.0"
$ ./zanei --facts-only --diff kizu-plugin.diff -C kizu
zanei: 0 fact(s)

$ ./zanei --min-score 70 --diff kizu-plugin.diff -C kizu
zanei: 0 afterimages
  no fact mutations in this diff.
```

Same on the toy fixture (quoted key, unquoted int `timeout`):

```
$ git diff -- plugin.json | ./zanei --facts-only
zanei: 0 fact(s)

$ ./nagori --facts-only --diff - …
nagori: 1 fact(s)
  value    timeout: '10' → '30'  (plugin.json:5)

$ ./nagori --explain --diff - …
nagori: 3 afterimages
FACT timeout: 10 → 30
  100 config  plugin.json:5     "timeout": 10
   84 docs    README.md:1       plugin version 0.3.0, hook timeout 10 seconds.
   84 docs    docs/help.txt:1   --timeout N   default 10
```

CANDIDATE already notes zanei is silent on JSON-only version hunks. Confirmed, and it is not just version: **any quoted key is invisible**. The primitive is “what this diff made false.” A plugin.json bump *is* that diff. zanei answers a different question: “what this *unquoted-binding* diff made false.”

Quoted-key regex is more than one line (nagori added `QUOTED_KEY_RE` as v0.2). Not applied.

Giving zanei a Cargo.toml sidecar on the same toy tree recovers the README leftover at 84. The gold path still works. The JSON-only path does not.

### 2. `café_timeout` is scraped as `_timeout` (conceptual)

```
-café_timeout = 10
+café_timeout = 30

$ ./zanei --facts-only --diff -
zanei: 1 fact(s)
  value    _timeout: '10' → '30'  (src/x.py:1)

$ ./nagori --facts-only --diff -
nagori: 0 fact(s)
```

`IDENT_RE` stops at `é`. The leftover suffix is minted as a fact name. nagori refuses the line (also a miss, but it does not invent a symbol). Searching dest for `_timeout` would be a different lie.

### 3. `"present"` leftover-matches `presentation` (conceptual)

`mode = "present" → "absent"` emits a **string** fact. String scoring is substring, not ident:

```
STR "present" → "absent"   src/flags.py:4
   96 docs    README.md:3   feature is present          # real
   74 docs    README.md:2   presentation layer stays    # substring
         why: name-stem, old-string, claim:docs
```

`needle_in_line("present", "presentation layer stays", ident=False)` is True. nagori treats it as a *value* and word-bounds: no hit. zanei’s string kind is the unfmt-family blind spot applied to polarity words.

### 4. `DEBUG` is a keyword — a real leftover vanishes (conceptual)

`DEBUG = True → False`, leftover `DEBUG is True` in the README. zanei extracts 5 facts and **does not include DEBUG** (`"debug" in KEYWORDS`). nagori extracts it and reports the leftover at 84.

The polarity the user flipped is the one zanei refused to name.

### 5. Homonym via stem substring — `settimeout(10)` is a leftover hook timeout (conceptual)

`HOOK_TIMEOUT = 10 → 30`. Dest test `assert socket.settimeout(10) or True`:

```
FACT HOOK_TIMEOUT: 10 → 30   src/hook.py:1
   68 assert  tests/test_net.py:2   assert socket.settimeout(10) or True
         why: name-stem, old-value, claim:assert
```

zanei stems are `s in line.lower()`. `timeout` ⊂ `settimeout`. nagori word-bounds the stem, scores 50, stays under 55. `threshold = 0.7` (true homonym binding) is skipped by both. The failure is the *unbound* same-noun: HTTP timeout, socket timeout, hook timeout are one token.

Same class, other package: both flag `pkg_b/pyproject.toml` `version = "0.3.0"` at 103 after `pkg_a` moved to 0.7.0 (`version-config`). Two packages, one noun. That is the kizu-plugin story without a workspace identity. The primitive cannot know which `version` is the one the diff falsified.

---

## nagori

### 1. Homonym-skip truncates `0.3.0` to `0.3` and throws away the leftover (conceptual, lethal to the JSON win)

nagori v0.2’s reason to exist is quoted JSON keys. It extracts `version: 0.3.0 → 0.7.0` from plugin.json. Then it searches dest.

Toy README: `plugin version 0.3.0, hook timeout 10 seconds.`

```
bindings [('version', '0.3')]
bound version 0.3
homonym_skip True
value_in_text 0.3.0 True
score (84, ['same-line-name', 'old-value', 'claim:docs'])   # never applied
```

`NUMBER_RE` is `\d+(?:\.\d+)?`. `version 0.3.0` binds `version = 0.3`. `0.3 ≠ 0.3.0` is “another symbol.” `search_tree` continues. Finding count 0. Banner: `1 fact(s) changed; none left an afterimage (min-score gated).` Score would have been 84. It was not gated. It was discarded as a homonym.

Even with a Cargo.toml sidecar (the path zanei needs), nagori still reports **0 afterimages** on that tree. zanei reports the README line at 84.

kizu still works: `plugin/plugin.json` binds a *quoted* `"0.3.0"`, and `plans/v0.3.md` says `version bump to 0.3.0` (not `version 0.3.0`), so the truncated bind does not fire. The gold case is a lucky phrasing. The common leftover sentence is the one that dies.

Not a one-line fix: the number regex, the homonym rule, and the “gated” message are three objects.

### 2. Polarity homonym — `ENABLE_CACHE` leftover-matches `DEBUG is True` (conceptual)

```
FLIP ENABLE_CACHE: True → False   src/flags.py:1
   76 docs    README.md:4   DEBUG is True
         why: nearby-name, name-stem, old-value, claim:docs
   58 assert  tests/test_flags.py:1   assert ENABLE_CACHE is True   # real
```

`True` is a boolean, not a distinctive value. Nearby window 3 reaches `the cache is enabled` two lines up (`name-stem` / `nearby-name`). Every leftover `True` in the neighborhood of the word `cache` is an afterimage of this flip. zanei does not emit this particular ghost (it also does not emit the DEBUG fact; see above).

### 3. Empty `--kinds` is a clean tree (fail-open)

```
$ ./zanei --kinds "" -C $EMPTY
zanei: empty --kinds
# rc=2

$ ./nagori --kinds "" -C $EMPTY
nagori: empty --kinds
# rc=0
```

Usage error printed to stderr, exit 0. A linter that cannot parse its flags looks like “no afterimages.” One-line fail-closed: `SystemExit(0)` → `SystemExit(2)` in `parse_kinds`. Not applied here — recorded, obvious, not the interesting hole.

### 4. Prose `timeout is 10` is not a fact — nested-only leftover goes dark

After the parent README is updated to `timeout is 30` (the only parent change), leftover lives only in the nested repo:

```
$ ./zanei --no-color --explain -C $NESTED
FACT timeout: 10 → 30   README.md:1
   84 docs    nested/inner/note.md:1   # nested still says timeout is 10

$ ./nagori --no-color --explain -C $NESTED
nagori: 0 afterimages
  no fact mutations in this diff.
```

zanei’s bare-number + shared-stem path treats the sentence as a binding. nagori’s `timeout is 10` matcher wants `timeout 10` or binds `is = 10` and then `allowed_value_name` refuses it. Conservative on fact extraction; blind on the nested afterimage that zanei (and the demo) care about.

### 5. 1.25 MB leftover file — omit looks like a clean tree

See shared §7. Dest’s only believer is 1_260_029 bytes. nagori rc=0. zanei reports it. The two implementations do not implement the same visibility.

---

## What survived

- Gold **kizu** `git diff v0.3.0 v0.7.0 -- Cargo.toml`: both still emit plugin.json `0.3.0` at 103 and two `plans/v0.3.md` lines at 84.
- Gold **sitbone** `e9b0f75^ e9b0f75 --min-score 55`: both still emit the two CLAUDE.md `threshold 0.4` lines. SiteObserver `threshold = 0.7` stays gone.
- Empty / newline / clean worktree / `Binary files differ`: honest 0.
- Nested git on a **worktree** dest: both see `nested/inner/note.md`.
- NFC café / CJK / emoji filenames: both search them.
- Japanese leftover of an *English* fact (`タイムアウトは 10`): both, via alias.
- 400-line prose remame hunk: 0 facts both.
- 200-file leftover scan: finishes, counts match (602).
- `vendor/` and `dist/` skipped as intended.
- NUL / UTF-16 dest files skipped.
- Bound homonym `threshold = 0.7` skipped by both.
- `self-test` still 0 / 0 after the battery.

---

## Kill / keep

**Keep both. Mutate both. Do not rewrite in this pass.**

The object is leftover *claims*. GHOST and the heretic already picked this over leftover names. The gold kizu skew and the sitbone 0.4 tests still come out of both binaries. nagori’s independent reimplementation is proof the interaction is not an accident of one file. It is also proof the interesting bugs are in the *fact* definition, not in the walk.

| tool | do not kill because | mutate toward |
| --- | --- | --- |
| zanei | Cargo.toml→plugin.json still the “why doesn’t this exist?” moment. Sitbone v2 still 2 real tests. JSON silence is a grammar, not a missing `rg`. | Quoted keys are facts (nagori already did this). Stem match must be token-bounded (`timeout` ⊄ `settimeout`, `present` ⊄ `presentation`). Do not mint `_timeout` from `café_timeout`. `DEBUG` is a name. Date components are not old integers. `generated/` is not a believer. Binary stdin / `--diff FILE` fail closed (exit 2). |
| nagori | Recovers the same gold without reading zanei’s source. JSON-only timeout hunk finds the dest leftovers zanei cannot name. Word-bounded stems dodge presentation / settimeout. | Homonym must not truncate `0.3.0` to `0.3` and discard the line that literally contains `0.3.0`. `True` is not distinctive enough to ride a nearby `cache`. Empty `--kinds` is exit 2. Size-cap omit must not print “min-score gated.” Prose `timeout is 10` is either a fact or it is not — pick one, including for nested dests. |

A one-line nagori `SystemExit(0)` → `SystemExit(2)` on empty `--kinds` would hide a usage footgun and would not touch version-truncation, date-months, or generated bundles. Not applied.

Do not grow a review platform. The next mutation is *typed* facts (version, timeout, polarity) with token boundaries, not a smarter walk.
