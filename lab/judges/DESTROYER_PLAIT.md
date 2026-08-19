# DESTROYER — plait

Adversarial pass on the composition algebra of review-suggestion strands. No rewrites: the failures are conceptual, not one-line bugs. Binary stdin / high-byte trees crash (operational); left unpatched so the algebra holes stay visible.

- **plait** (candidate-38) — `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01b56-ac5a-7b03-a99f-437a44b4b3bf`
- Transcript: `/tmp/destroy-plait/transcript.txt`
- Follow-up: same dir, commands re-run after the battery
- Fixtures: `/tmp/destroy-plait/fixtures/`
- Attack driver: `/tmp/destroy-plait/attack.py`
- `./plait --selftest` → `selftest 23/23 passed` after the attacks (CANDIDATE said 21). `./demo.sh` → `PASS=35 FAIL=0`.

Attacks: overlapping same-line after-images, inverted timestamps, markdown vs JSON, empty stream, huge 100-comment dump, unicode, suggestions that apply only after another, identical echoes.

Verdict: **mutate, do not kill.** COMMUTE and JAM are real. Gold `fixtures/commute.jsonl` is still `PARALLEL` rc=0; gold `jam.jsonl` is still `JAMMED` rc=2; cli/cli PR #7 is still `#333030758,#333031216` commuting. The attacks show where ECHO is image-identity not locus-identity, where an empty markdown before is a SPLIT, and where an inverted clock plus two live images reports `same-tree` on the wrong tree.

---

## Primitive restated

A review suggestion is a strand (span + before→after). plait is the composition of those strands with each other (COMMUTE / STACK / ECHO / SPLIT / SUBSUME / JAM), not occupancy against a tree and not GitHub "outdated". Apply schedules (`line` / `time` / `topo`) are witnesses. Exit 0 composable, 1 SPLIT, 2 JAMMED, 3 error.

---

## 1. Overlapping same-line after-images — replacement is the object; "same after" is not union (conceptual)

Two GitHub suggestions on one line with two afters are SPLIT. That is the pitch, and it holds:

```
$ ./plait /tmp/destroy-plait/fixtures/same-line-compatible-words.jsonl
plait  n=2  files=1  components=1  SPLIT=1
  SPLIT    app.py  #left@1  #right@1  same before, two afters
# rc=1
```

`hello world` → `HELLO world` and `hello world` → `hello WORLD` would compose as word-patches to `HELLO WORLD`. They are two after-images of one span. Apply is refused (`error: split`). Not a miss: GitHub "Commit suggestion" replaces the line. Word-level commute is a different algebra.

Same-span `foo(bar)` → `foo(BAR)` vs `FOO(bar)`: SPLIT, rc=1. Overlapping *ranges* that share a line and disagree: JAM, rc=2.

```
$ ./plait /tmp/destroy-plait/fixtures/same-line-overlap-jam.jsonl
  JAM      app.py  #wide@1-2  #tail@2-3  overlapping spans, incompatible
# rc=2
```

**Same after-image on the shared line is still JAM.** `wide` after `["A","SHARED"]`, `tail` after `["SHARED","C"]`:

```
$ ./plait /tmp/destroy-plait/fixtures/same-line-overlap-same-after.jsonl
  JAM      app.py  #wide@1-2  #tail@2-3  overlapping spans, incompatible
# rc=2  apply:line=fail,time=fail,topo=fail  error=wide:no-before
```

The join line agrees. The spans do not. A union would be `A, SHARED, C`. The object is replacement, not hunk-union. Honest JAM.

**Same line, same after, different befores → ECHO via the overlap branch.** Trailing space on `before` (`beta` vs `beta  `):

```
$ ./plait /tmp/destroy-plait/fixtures/same-line-same-after-diff-before.jsonl
  ECHO     app.py  #a@2  #b@2  overlap, same after
# rc=0
```

`--ignore-space` upgrades the reason to `same before→after`. Collapse keeps one strand. The trailing-space twin is treated as a duplicate even though its before-image would miss on disk. Overlap + equal after is enough.

---

## 2. Inverted timestamps — topo still beats the clock; both-images makes the clock look true (conceptual, load-bearing)

Gold STACK with inverted `created_at` (round2 clock-earlier than round1) still does the thing CANDIDATE exists for, with one lie in the table:

```
$ ./plait -C /tmp/destroy-plait/trees/stack fixtures/stack.jsonl
  STACK    app.py  #round1@2  #round2@2  after(a)==before(b)  a>b
  SERIES   app.py  #round1,#round2  unique apply order
          apply:line=ok,time=fail,topo=ok  different-trees
# rc=0
```

CANDIDATE's schedule table says stack `line=fail`. Empirical: `line=ok`, order `['round1','round2']`. Both spans are line 2, so "line" is id order, which happens to be topo. `time` is `round2:no-before` (honest). `topo` digest `1831752c954d` = `['alpha','beta3','gamma']`. The witness that is supposed to catch inverted clocks is **time**, not line. The table is wrong; the primitive is not.

**Both images live in the tree and inverted time reports same-tree on the wrong tree:**

base = `alpha / beta / beta2 / gamma` (round1's before *and* round2's before both present).

```
$ ./plait -C /tmp/destroy-plait/trees/stack-both invert-stack-both-present.jsonl
  SERIES   app.py  #round1,#round2  unique apply order
          apply:line=ok,time=ok,topo=ok  same-tree
# rc=0
  line order=['round2','round1'] digest=fcb8901f5c21
  time order=['round2','round1'] digest=fcb8901f5c21
  topo order=['round1','round2'] digest=fcb8901f5c21
```

`fcb8901f5c21` is `['alpha','beta2','beta3','gamma']`. Intended stack is `1831752c954d` = `['alpha','beta3','gamma']`. Time applies round2 first (`beta2`→`beta3` in place) then round1 (`beta`→`beta2` in place). Topo applies round1 first (`beta`→`beta2`, now two `beta2`) then round2's unique-image fallback rewrites one of them to `beta3`. Same digest, **not** the SERIES tree. `same_tree=True` means "three schedules agreed," not "the stack happened."

COMMUTE with inverted clock + insert still same-tree (shift works either order). Malformed timestamps (`yesterday`, `2020-13-40T99:99:99Z`) and equal timestamps stay PARALLEL. Clocks that do not parse fall back to string sort; they do not crash.

---

## 3. Markdown vs JSON — quoted commute matches; empty before is SPLIT; one junk line empties a JSONL (conceptual + operational)

JSON commute and markdown *with* a quoted before are the same algebra (ids differ, verdicts do not):

```
$ ./plait json-commute.jsonl
  COMMUTE  app.py  #alice@1  #bob@3  disjoint spans
  PARALLEL … compose in any order
# rc=0  n=2  recon=explicit

$ ./plait md-commute-quoted.md
  COMMUTE  app.py  #…md:1:app.py@1  #…md:2:app.py@3  disjoint spans
  PARALLEL …
# rc=0  n=2  recon=markdown  before=['alpha'] / ['gamma']
```

**Markdown without a quote fence mints `before=[]` for every suggestion.** Two disjoint edits then have the same before:

```
$ ./plait md-commute-noquote.md
plait  n=2  files=1  components=1  SPLIT=1
  SPLIT    app.py  #…@1  #…@3  same before, two afters
# rc=1
  strands before=[] after=['ALPHA'] span=1
          before=[] after=['GAMMA'] span=3
```

JSON of the same edits is COMMUTE. Markdown of the same edits, missing the quoted original, is "reviewers disagree." Apply is refused (`error: split`) even against a tree that has `alpha` / `gamma` sitting on disk. The image-equality test runs *before* span-disjoint. Empty before is a universal key.

`file: app.py:1` headers and `<!-- path: app.py -->` still ingest. `{not json` at the start of a markdown file recovers as markdown (`n=1`). That recovery is the *other* direction of the next hole:

```
$ cat json-then-md.jsonl
{"id":"a",…after:["ALPHA"]}
this is not json
{"id":"b",…after:["GAMMA"]}

$ ./plait json-then-md.jsonl
plait  n=0  files=0  components=0
(no strands)
# rc=0
```

One garbage line raises `JSONDecodeError` out of `_iter_json_docs`; `ingest` swallows it and markdown-parses the whole buffer. JSON objects are not path headers. **Both valid strands vanish.** A prefix-only JSONL (`{"id":"a",…}`) is `n=1`. Fail-open EMPTY, not a parse error.

Markdown SPLIT of two quoted afters on the same line still matches JSON SPLIT. The quoted-before path is the same tool. The unquoted path is a different object.

---

## 4. Empty stream — honest zero (survived)

```
$ printf '' | ./plait -
plait  n=0  files=0  components=0
(no strands)
# rc=0

$ echo '[]' | ./plait --json -
unanimous=EMPTY  n=0  component_counts={}
```

Empty bytes, newline, whitespace, `[]`, `{}`, `{"comments":[]}`, `{"review_comments":[]}`, `null`, `[{}]` (no path), a body with no ````suggestion```` and no `--remarks`: all `n=0` rc=0, no traceback. `--remarks` on `{"id":"x","path":"a.py","line":1,"body":"lgtm"}` is one PARALLEL remark. Vacuous composition is success. Same class as zanei's empty diff. Not a walk. Survived.

TTY with no args is still `plait: pass a review stream or '-' for stdin` rc=3 (documented). A pipe of empty is the stream.

---

## 5. Huge 100-comment dump — GitHub sample holds; C(n,2) is a firehose; one-file `--remarks` is one COVER (operational + conceptual)

Real cli/cli last 100 review comments (3 suggestions) still the v2 story:

```
$ ./plait fixtures/cli-cli-comments.json
plait  n=3  files=1  components=1  PARALLEL=1
  COMMUTE  command/pr.go  #333030758@347  #333031216@400  disjoint spans
  COMMUTE  … #333030758@347  #335420325@23  distinct commits; images independent
# rc=0  elapsed=0.040s

$ ./plait --remarks fixtures/cli-cli-comments.json
plait  n=100  files=12  components=50  PARALLEL=17 THREAD=33
  json n=100  component_counts={'THREAD': 33, 'PARALLEL': 17}
       pair_counts={'DISJOINT': 4880, 'THREAD': 67, 'COMMUTE': 3}
       n_pairs_emitted=70  elapsed=0.060s
```

4880 DISJOINT hidden. Suggestion PARALLEL intact. COVER-on-replies still gone. The sample survived.

**100 identical echoes / 100 commuting nits / 100 same-span afters** finish in <0.08s. The kernel is cheap. Pretty output is not:

| dump | n | unanimous | pairs emitted | pretty |
| --- | ---: | --- | ---: | --- |
| 100 ECHO same span | 100 | ECHO | 4950 | 4950 ECHO lines + one 100-id plait |
| 100 COMMUTE consecutive lines | 100 | PARALLEL, same-tree | 4950 | 4950 COMMUTE lines |
| 100 same-span different afters | 100 | SPLIT rc=1 | 4950 | 4950 SPLIT lines |

v2 hid DISJOINT as the Cartesian miss. COMMUTE of 100 independent nits *is* the object, and it is C(100,2) lines. `--json` is the composable form. Human default is a dump.

The 100 overlapping rewrites were intended as JAM. Same before + many afters is SPLIT. That is the algebra working: JAM is overlapping *different ranges*, not N after-images of one span.

**One-file mixed 100 (`--remarks`) collapses to one COVER.** 15 suggestions + 85 remarks, reply-linked, all on `app.py`:

```
$ ./plait --remarks --json huge-100-mixed.jsonl
n=100  kinds={'suggestion','remark'}  n_sug=15  n_remark=85
unanimous=COVER  components=1  n_strands=100
pair_counts={'COMMUTE': 105, 'COVER': 60, 'DISJOINT': 4589, 'THREAD': 196}
```

COMMUTE joins the suggestions. COVER joins a remark that sits on one of them. THREAD joins the reply chains. CONNECTING is the union of those, so the file is one component; `component_verdict` hits COVER before THREAD. The 15-suggestion PARALLEL plait is gone. The GitHub 100-comment sample escaped because suggestions and remarks live on *different files*. Same-file review is the common case. v2's "COVER is remark×suggestion only" still *connects* them into one plait.

---

## 6. Unicode — CJK applies; NFC/NFD is ECHO of afters and DISJOINT of paths (conceptual)

```
$ ./plait -C trees/cjk unicode-cjk.jsonl
  COMMUTE  日本語.py  #jp@1  #emoji@3  disjoint spans
  PARALLEL 日本語.py  #jp,#emoji  … apply:line=ok,time=ok,topo=ok same-tree
# rc=0
  タイムアウト = 10 → 30    print('🌀') → print('✅')
```

Japanese path, Japanese binding, emoji after-image. Apply witnesses fire. Paths are not the hole.

**NFC `café` vs NFD `cafe\u0301` as befores, same after, same span → ECHO:**

```
$ ./plait unicode-echo-lookalike.jsonl
  ECHO     app.py  #a@1  #b@1  overlap, same after
  strands  ['café'] → ['tea']
           ['café'] → ['tea']
```

Befores are not equal (first image-check misses). Spans overlap, afters match, overlap-branch ECHO. Collapse keeps one. A tree holding the other normalization would miss the kept before.

**NFC path vs NFD path are two files, one APFS inode:**

```
$ ./plait --all-pairs -C trees/nfd unicode-path-nfd.jsonl
plait  n=2  files=2  components=2  PARALLEL=2
  DISJOINT  café.py  #a  #b  cross-file
  PARALLEL café.py  #a  apply … same-tree
  PARALLEL café.py  #b  apply … same-tree
# same inode 120929194; nfc exists True, nfd exists True
```

Two PARALLEL singletons on one file. They will not COMMUTE. They will not shift each other. Occupancy already named `core.quotepath`; this is the same class on the path *key*.

---

## 7. Suggestions that apply only after another — STACK is image-equal; subset is COMMUTE that cannot commute (conceptual, load-bearing)

Classic STACK still SERIES:

```
$ ./plait -C trees/stack stack-classic.jsonl
  STACK    app.py  #a@2  #b@2  after(a)==before(b)  a>b
  SERIES   … apply:line=ok,time=ok,topo=ok same-tree
# rc=0   (clocks not inverted here)
```

Three-way `v1→v2→v3→v4` is SERIES. Adjacent pairs STACK; `r1`×`r3` is COMMUTE (`after(r1)=v2 ≠ before(r3)=v3`, distinct commits). The component still chains. Transitive stack is a plait property. Create-file then edit (`after(create)==before(edit)`) is STACK even with empty create-before. Image-equal is the kernel and it is real.

**B edits a line that only exists in A's after, and after(A) ≠ before(B):**

A replaces `pass` with a three-line function; B rewrites `    return 1` → `    return 2` on the next commit.

```
$ ./plait -C trees/insert-fn stack-subset.jsonl
  COMMUTE  app.py  #insert-fn@1  #edit-return@2  distinct commits; images independent
  PARALLEL app.py  #insert-fn,#edit-return  independent; compose in any order
          apply:line=fail,time=fail,topo=ok  different-trees
# rc=0
  line/time error=edit-return:no-before
  topo order=['insert-fn','edit-return']  (span-start, not STACK)
```

The note is "compose in any order." Line and time cannot. Topo can because `topo_order` with no STACK edges is span order, insert lands the function, unique-image fallback finds `    return 1`. The apply witness that works is an accident of leftover unique text, not a declared SERIES. Cross-commit with unequal images is hard-coded COMMUTE (`distinct commits; images independent`) after the STACK check misses.

Rename then use-site (`old = 1` → `new = 1`, later `print(new)`): COMMUTE, **all three schedules fail** (`use:no-before`). PARALLEL of two edits, one of which has no image in the tree. Independent in the span sense; not independent in the apply sense.

**A↔B cycle is SERIES, not JAMMED.** `before=A after=B` stacked with `before=B after=A`:

```
$ ./plait -C trees/cycle stack-cycle.jsonl
  STACK    app.py  #a@1  #b@1  after(a)==before(b)  a>b
  SERIES   … unique apply order  apply:line=ok,time=ok,topo=ok same-tree
# digest 06f961b802bc == ['A']   (the original tree)
```

The reverse STACK is an `elif`, so only `a>b` is recorded. `_has_cycle` never sees `b>a`. Apply a then b is A→B→A, a no-op that reports unique order. `component_verdict` has a cycle branch. This pair does not reach it.

---

## 8. Identical echoes — apply-once is right on one locus, lethal on two (conceptual, lethal to ECHO)

Same span, same before→after, two authors: ECHO, collapse to `['alice']`, tree `x` → `y`. Three-way ECHO, delete-ECHO, cross-commit ECHO: all ECHO, apply once. That is the pitch.

**Same before→after on line 1 and line 10 is also ECHO:**

```
$ ./plait -C trees/dup-sites echo-dup-sites.jsonl
  ECHO     app.py  #site1@1  #site2@10  same before→after
  ECHO     app.py  #site1,#site2  duplicate strands
          apply:line=ok,time=ok,topo=ok same-tree
# rc=0  order=['site1']  digest=4fad3e4d4674
```

`4fad3e4d4674` is `['return 1', 'keep'×8, 'return 0']`. Line 10 is leftover. Image-equality runs before spans. Duplicate `return 0` nits — the thing a reviewer clicks twice — become one apply. Two sites that *should* COMMUTE (disjoint spans, same snapshot) never reach the span check.

Whitespace-different befores, same after, overlapping spans: ECHO via `overlap, same after` (same as §1). `--ignore-space` makes it `same before→after`. 100 identical echoes: one ECHO plait, 4950 pairs, apply `['e0']` once. Clique collapse works; pretty does not.

---

## 9. Binary — stdin and high-byte trees crash rc=1 (operational)

```
$ printf '\x00\xff' | ./plait -
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff in position 1: invalid start byte
# rc=1  traceback from sys.stdin.read()

$ ./plait -C trees/bin2 bin2.jsonl     # secret.bin = x\x00y\xffz
UnicodeDecodeError: … byte 0xff in position 3
# rc=1  traceback from load_tree_file read_text
```

Exit 1 is SPLIT. A crash is "reviewers disagree." Missing file and directory inputs are already rc=3 (`plait: … No such file` / `Is a directory`). NUL-only files are valid UTF-8 and do not crash; apply then fails closed (`line=fail`). High bytes are the uncaught path.

A `decode(..., "replace")` or `die(..., 3)` is a robustness patch, not a primitive fix. Not applied. Same class as zanei/cinch binary stdin; cinch closed it because isolation became unaskable. plait's algebra does not need a tree.

---

## What survived

- Gold **COMMUTE**: `fixtures/commute.jsonl` PARALLEL rc=0, `#alice@1` × `#bob@3` disjoint spans. cli/cli PR #7 `#333030758,#333031216` one PARALLEL plait. kizu two export nits PARALLEL + apply (demo case 10).
- Gold **JAM**: `fixtures/jam.jsonl` JAMMED rc=2. Shared-line overlap with disagreeing afters JAM rc=2. kizu overlapping rewrite + nits → JAMMED, apply fails (demo).
- Gold **STACK** with a single live image: topo `beta→beta3`, inverted time `round2:no-before`. Three-way image chain SERIES.
- Gold **SPLIT** vs **ECHO** on one locus: two afters rc=1; same after rc=0, apply once.
- Gold **100-comment GitHub stream**: 3 suggestions, 1 PARALLEL, `--remarks` 33 THREAD + 17 PARALLEL, 4880 DISJOINT hidden, no COVER-on-replies.
- Empty / `[]` / `{}` / `null` / no-suggestion body: `n=0` `(no strands)` rc=0.
- CJK path + Japanese line + emoji: COMMUTE, apply same-tree.
- Malformed timestamps do not crash. COMMUTE insert+edit with inverted clock still same-tree.
- `--selftest` 23/23. `./demo.sh` 35/35. No rewrite.

---

## Kill / keep

**Keep. Mutate. Do not rewrite in this pass.**

COMMUTE and JAM are not extinct. A developer about to click two GitHub suggestions on one file still gets PARALLEL / JAMMED / SPLIT before the third click fails. The 100-comment sample and the kizu overlap are still why the verb exists. Nothing in this battery turned those into occupancy or into `git apply --check`.

Do not kill because of markdown-empty-before, NFC paths, or the binary traceback. Those are mutations. Killing them would throw away a real pair-algebra to hide an ingest footgun.

| do not kill because | mutate toward |
| --- | --- |
| PR #7 COMMUTE, jam.jsonl rc=2, kizu commute×jam, 100-comment PARALLEL of 3 suggestions, STACK topo vs inverted time when only one image lives | **ECHO is a locus, not an image.** Same before→after on two spans is COMMUTE (apply twice), not apply-once. Image-equality must not outrank disjoint spans. |
| | **Empty before is not a before.** Markdown without a quote fence must not SPLIT disjoint afters. Missing image is `recon=none`, not `[] == []`. |
| | **STACK is "B applies only after A", not only `after(A)==before(B)`.** Subset / insert-then-edit is SERIES (or an explicit residual), not COMMUTE "any order". Cross-commit COMMUTE must not claim independence when a before is absent. |
| | **Schedules that agree on the wrong tree are not `same-tree`.** Both-images + inverted clock produced `alpha,beta2,beta3` and called it SERIES. Witness the result against the STACK fold, or refuse time when it is not topo. |
| | **A↔B is a cycle.** Record both STACK directions; `component_verdict`'s cycle branch should fire. No-op SERIES is a lie. |
| | **`--remarks` CONNECTING must not COVER-absorb the suggestion plait** on one file. Suggestions stay a PARALLEL/SERIES component; remarks THREAD around them. |
| | Pair listing: hide or summarize C(n,2) COMMUTE/ECHO the way DISJOINT is hidden. 4950 lines is not a plait. |
| | JSONL: a junk line is exit 3 (or skip the line), not EMPTY of the valid prefix. NFC-normalize paths. Binary stdin / `--root` high bytes fail closed (exit 3), not `UnicodeDecodeError` rc=1. CANDIDATE's stack `line=fail` row should match the id-tie. |

A one-line `sys.stdin.buffer` decode-or-die would hide the traceback and would not touch duplicate-site ECHO, empty-before SPLIT, or subset-as-COMMUTE. Not applied.

Do not grow a review platform. The next mutation is *locus-aware* ECHO/STACK (span + image, residual befores), not a prettier 100-comment dump.
