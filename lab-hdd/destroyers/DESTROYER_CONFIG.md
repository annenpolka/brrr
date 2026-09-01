# DESTROYER — config (envfrom / stated / effect)

Empirical attacks after **05:00 JST** on implementation **and** primitive.
Each serious finding is exactly one of `FIX` / `MUTATE` / `KILL`.
Entertaining harvest text is not protection.

Transcripts: `/tmp/destroy-config/logs/attack.out`
Harness: `/tmp/destroy-config/attack.py` (real CLIs, no imported internals)
Work: `/tmp/destroy-config/work/`

| object | tree | shipped CLI |
| --- | --- | --- |
| envfrom parent | `lab-hdd/lineages/candidate-05__envfrom` | `./envfrom` |
| envfrom `--json` | `lab-hdd/lineages/mutation-01__envfrom-json` | `./envfrom` |
| stated clean-room | `lab-hdd/lineages/reimpl-01__stated` | `./stated` |
| stated compact-JSON | `lab-hdd/lineages/mutation-05__stated-jsonobj` | `./stated` |
| stated×envfrom hybrid | `lab-hdd/lineages/hybrid-01__effect` | `./effect` |

Attacks actually run: huge `.env` (9.1MB / 200k lines), huge source (16.7MB), missing DIR, `--dir` as file / `/dev/null`, binary/invalid UTF-8, NUL, interpolations (`${BAR}`, `$BAR`, `KEY+=`, getenv default), self-symlink `.env`, circular `DIR/loop → DIR`, empty-override vs process-empty vs unset, cwd vs explicit DIR, stdin pipes, BOM+CRLF, hyphen/unicode keys, compact JSON, nested JSON, `.env` as declaration, case `TIMEOUT`/`timeout`, same-side two YAMLs, `node_modules` skip, `rg` / `printenv` honesty.

**Do not kill any of the three primitives.** Empty-override vs inherited is not `printenv`+`grep`. The disagreement pair is not `rg KEY`. Deferred-name EFFECTIVE is not `stated KEY; envfrom KEY`. Implementations have FIX holes; several primitive edges are MUTATE.

---

## Verdicts

| object | primitive | implementation |
| --- | --- | --- |
| **envfrom** (c05 + m01) | **MUTATE** — not env+grep | **FIX** missing DIR / binary crash / BOM / text `VALUE=` smash |
| **stated** (r01 + m05) | **MUTATE** — not rg; pair is real, scanner is still a line token | **FIX** per lineage (see below); **MUTATE** `.env`-as-declaration, case, nested path |
| **effect** (hybrid-01) | **MUTATE** — join is real; concatenation loses WAIT | **FIX** compact JSON miss, binary `.env` crash, silent 2MiB skip that lies about EFFECTIVE |

Unix First Selection already wanted stated killed as grep-plus-status. This pass does **not** honor that as a KILL: `rg timeout` on the disagree fixture hits the docstring; `stated timeout` emits one comparable pair and exits 2. That is the object. The scanner is still grep-shaped. Mutate the scanner, do not delete the pair.

effect's own kill test (*"Kill if a judge can replace it with `stated KEY; envfrom KEY` and lose nothing"*) **fails on the deferred fixture**. Keep the four-field record; fix the implementation.

---

## 1. envfrom — primitive restated

Name a variable. Report whether the **would-apply** value is process env, a dotenv `file:path:line`, or unset. A file line `KEY=` is an **empty override** even when the process already has `KEY`. `--run` prints that provenance then execs; `--load` actually applies it.

Nearest Unix: `printenv KEY` plus opening `.env`. What that loses: which line wiped the key, inherited-next-to-empty, empty-override vs process-empty vs unset as three records, `--fail-empty` before exec.

mutation-01 adds `--json` `{key,value,source,empty_override,inherited}` with `inherited: null` (not the text token `(unset)`). Same primitive, machine encoding.

### 1.1 Empty-override vs unset vs process-empty — holds

`printenv` cannot say this. `grep` cannot say this. The three-way split is the primitive.

```text
$ env -i PATH=/usr/bin:/bin HOME=/tmp PROC_EMPTY= FILE_EMPTY=inherited \
    python3 mutation-01__envfrom-json/envfrom --json --dir /tmp/destroy-config/work/empty-vs-unset \
    FILE_EMPTY PROC_EMPTY UNSET_BOTH FILE_SET
```

```json
[
  {"key":"FILE_EMPTY","value":"","source":"file:…/.env:1","empty_override":true,"inherited":"inherited"},
  {"key":"PROC_EMPTY","value":"","source":"env","empty_override":false,"inherited":""},
  {"key":"UNSET_BOTH","value":"","source":"unset","empty_override":false,"inherited":null},
  {"key":"FILE_SET","value":"x","source":"file:…/.env:2","empty_override":false,"inherited":null}
]
```

`--fail-empty` fires only on file empty-override, not on inherited `PROC_EMPTY=""`. Honest.

Unix honesty on the shipped empty-override fixture:

```text
$ env LIBRARY_PATH=/usr/local/lib:/usr/lib printenv LIBRARY_PATH
/usr/local/lib:/usr/lib

$ grep -n LIBRARY_PATH fixtures/empty-override/.env
1:# LIBRARY_PATH is emptied here …
2:LIBRARY_PATH=

$ env LIBRARY_PATH=/usr/local/lib:/usr/lib python3 envfrom --dir fixtures/empty-override LIBRARY_PATH
LIBRARY_PATH
VALUE=
SOURCE: file:…/.env:2
EMPTY_OVERRIDE: yes
INHERITED: /usr/local/lib:/usr/lib
```

`printenv` reports the live map. `grep` reports a line. envfrom is the join, with file:line. **Not env+grep. Not KILL.**

`--run` without `--load` still prints would-apply empty override, then the child keeps inherited `LIBRARY_PATH='/usr/lib'`. That split is the honest rule, not a bug.

### 1.2 Missing DIR / `--dir` is a file / `/dev/null` — **FIX** (c05 and m01)

stated and effect exit 1 on a missing directory. envfrom does not check. `os.path.isfile(dir/.env)` is false, so it reports process env as if the tree were empty.

```text
$ python3 envfrom --dir /no/such/envfrom-dir LIBRARY_PATH PATH
LIBRARY_PATH
VALUE=/already
SOURCE: env
PATH
VALUE=/bin
SOURCE: env
# rc=0, stderr empty
```

Same rc=0 `SOURCE: env` for `--dir /tmp/destroy-config/work/not-a-dir.txt` and `--dir /dev/null`.

`--json --dir /no/such/dir PATH` still dumps the whole login PATH as `source: "env"`. A script that treats missing tree as "no dotenv, inherit everything" will load the wrong world.

**FIX:** exist/isdir check, exit 1, like stated.

### 1.3 Binary / invalid UTF-8 `.env` — **FIX** (c05, m01, and effect's copy)

```text
$ printf 'FOO=ok\nBAR=\xff\xfe\x00notutf8\nBAZ=1\n' > /tmp/destroy-config/work/binary/.env
$ python3 candidate-05__envfrom/envfrom --dir …/binary FOO
# rc=1, Traceback UnicodeDecodeError in parse_dotenv (open encoding=utf-8, uncaught)
```

`OSError` is wrapped as `envfrom: cannot read …`. `UnicodeDecodeError` is not. Permission-denied `.env` correctly exits 1 (`[Errno 13]`). Binary should too, without a traceback.

NUL-containing `.env` that is still valid UTF-8 is parsed as a line with an embedded NUL. Not a crash; still a bad record.

### 1.4 UTF-8 BOM on the first key — **FIX**

```text
$ printf '\xef\xbb\xbfFOO=bom\r\nexport BAR\r\nBAZ=ok\r\n' > …/bom/.env
$ python3 envfrom --dir …/bom FOO BAR BAZ
FOO
VALUE=
SOURCE: unset
BAR
VALUE=
SOURCE: unset
BAZ
VALUE=ok
SOURCE: file:…/.env:3
```

CRLF is fine (`BAZ=ok`). BOM is not whitespace in `str.strip()`, so the key is `\ufeffFOO`, `VALID_KEY` fails, the assignment is **silently dropped**. `FOO` looks unset. `export BAR` (no `=`) is skipped; that one is honest.

### 1.5 Quoted `\n` smashes the text block — **FIX** (text) / already encoded in `--json`

```text
$ printf 'MSG="hello\\nworld"\nNEXT=ok\n' > …/nlval/.env
$ python3 envfrom --dir …/nlval MSG NEXT
MSG
VALUE=hello
world
SOURCE: file:…/.env:1
…
```

Candidate CANDIDATE.md already named this. mutation-01 `--json` round-trips `"hello\nworld"`. Default text mode is still not a record. **FIX** the text encoder (or refuse unescaped newlines). Do not treat `--json` as a complete close.

### 1.6 Self-symlink `.env` and `.env` as a directory — **FIX**

`os.path.isfile` is false for a self-symlink and for a directory named `.env`. Both become silent `SOURCE: env`.

A symlink **to a real file** is followed (`SECRET=linked`, `SOURCE: file:…/.env:1`). Unix-honest. `--dir` symlink-to-a-directory is followed. Good.

**FIX:** if `.env` exists and is not a regular (or resolvable) file, error. Do not pretend the file was absent.

### 1.7 Interpolation / `KEY+=` / hyphen keys — **MUTATE**

Documented: no `${OTHER}`, no `KEY+=`. Still a provenance hole: the file **is** the source of `FOO`, but the effective value is not `${BAR}`.

```text
BAR=realbar
FOO=${BAR}
BAZ=$BAR
DEF=${BAR:-fallback}
PLUS+=more
APP_URL=${HOST}:${PORT}
```

```text
FOO   VALUE=${BAR}          SOURCE: file:.env:2
BAZ   VALUE=$BAR            SOURCE: file:.env:3
PLUS  VALUE=                SOURCE: unset      # KEY+= silently dropped (PLUS+ fails VALID_KEY)
```

Hyphen / digit / unicode keys in the file are also silent unset:

```text
$ grep -n . oddkeys/.env
1:FOO-BAR=hyphen
2:1ABC=digit
3:CAFÉ=cafe
4:_OK=uscore

$ python3 envfrom --dir oddkeys FOO-BAR _OK
FOO-BAR
VALUE=
SOURCE: unset
_OK
VALUE=uscore
SOURCE: file:…/.env:4
```

`grep` sees `FOO-BAR=hyphen`. envfrom reports unset. Dotenv grammar may reject hyphen keys; **silence is the bug**. **MUTATE:** either parse interpolation/`+=`, or emit `source: skipped` / stderr for dropped lines. Do not report unset for a line that exists.

### 1.8 Pipes / stdin — **MUTATE**

`printf 'FROMSTDIN=piped\n' | envfrom --dir DIR FROMSTDIN` ignores stdin (FROMSTDIN stays process/unset). No `-`, no `--file`.
`envfrom` with no KEY and a piped name: `envfrom: provide KEY...` rc=1.
`--run` **does** forward stdin to the child (`CHILD_STDIN=hello-stdin`). That half is honest.

`--json --run` concatenates the JSON document and the child on the same stdout. `json.loads` fails. mutation-01 CANDIDATE.md already named this. **MUTATE:** provenance on stderr / fd 3, or refuse `--json --run` without a split.

### 1.9 cwd vs `--dir` — honored (not a finding)

Default DIR is cwd. `--dir there` while cwd is `here` reads `there/.env`. `--dir ''` behaves like cwd. SOURCE path shape is inconsistent: cwd → `file:.env:1` (relative); `--dir /abs` → `file:/abs/.env:1`. Ugly, not false. Optional MUTATE for relative-when-under-cwd (already in suggested mutations).

### 1.10 Huge `.env` — survives

9.1MB / 200003 lines parsed in ~0.33s. Last-wins `KEEP=last-wins` at line 200003. `TAIL=` still `EMPTY_OVERRIDE: yes`. No size cap. Fine for this night; a 2GiB `.env` would still be unbounded.

### 1.11 Last-wins hides the chain — **MUTATE**

`.env FOO=first` then `FOO=second`, `.env.local FOO=third` → only `file:.env.local:1`. Nested `sub/.env` is invisible. `.env.example` is ignored (by design). These are scope mutations, not kills.

### Primitive call

**MUTATE envfrom, do not kill.** The object is empty-override vs inherited vs unset at file:line. `--json` is the right encoding mutation. Next cuts: missing-DIR FIX, binary/BOM FIX, dropped-line visibility, interpolation as a *deferred* name (effect already went there), source chain.

---

## 2. stated — primitive restated

Given KEY, scan config-like files for `KEY:` / `KEY=` and source for assignments of the same identifier. Comparable scalars become a **disagreement pair** (exit 2). One-sided / agree / unknown / none exit 0. Interpolations and calls are UNKNOWN, not a fake match.

Nearest Unix: `rg KEY` then read both hits. What rg loses: comparable vs not, comments labeled and ignored, exit 2 only when literals disagree.

reimpl-01 is a clean-room of that object (NUL-skip, start-anchored config pattern, no 2MiB cap).
mutation-05 is ordinary mutation of candidate-02: compact `{"timeout": 5}` is a declaration.

### 2.1 Disagreement pair is not `rg` — holds

```text
$ rg -n timeout reimpl-01__stated/fixtures/disagree
app.py:1:"""App that hardcodes a different timeout than config.yaml."""
app.py:3:timeout = 10
config.yaml:1:timeout: 5

$ python3 reimpl-01__stated/stated timeout fixtures/disagree
status: DISAGREE
disagreement:
  declared     5	config.yaml:1	timeout: 5	value=5
  contradicted 10	app.py:3	timeout = 10	value=10
# rc=2
```

rg hits the docstring. stated does not pair it. **Not KILL.**

Interpolation fixture: both lineages UNKNOWN, not DISAGREE. reimpl keeps `value=${WAIT}`. mutation-05 does not (see 2.4).

Missing DIR / file-as-DIR: all three stated CLIs exit 1. Empty DIR: NONE exit 0. cwd vs explicit DIR honored (agree here vs disagree there). Symlink DIR to a real tree works. `DIR/loop → DIR` does not hang (`followlinks=False`). `node_modules` and hidden dirs skipped. 5 vs `"5"`, `yes` vs `True`, `5.0` vs `5` AGREE. Typed `timeout: int = 10` stays UNKNOWN (expression), not a fake 10.

### 2.2 Compact JSON — mutation-05 / reimpl hold; parent candidate-02 still blind

```text
$ python3 mutation-05__stated-jsonobj/stated timeout reimpl-01__stated/fixtures/compact_json
status: DISAGREE   # config.json {"timeout": 5} vs app.py timeout = 10, rc=2

$ python3 candidate-02__stated/stated timeout …/compact_json
status: ASSIGNED_ONLY  value: 10   # the hole mutation-05 exists to close
```

Nested `{"server": {"timeout": 5}}` is **ASSIGNED_ONLY** on every stated. `stated server.timeout` is NONE. Line token, not a path. **MUTATE** (documented limit; still a weekly config shape).

Indented YAML `server:\n  timeout: 5` **does** match as a line token. DISAGREE vs `timeout = 10`. Honest for the line-token primitive.

JSON array `[{"timeout": 5}, {"timeout": 7}]`: mutation-05/reimpl declare **only 5**, miss 7. First-token cut, not a JSON parser. **MUTATE**.

### 2.3 `.env` is a declaration — **MUTATE** (this is why effect exists)

On effect's disagree fixture (`.env TIMEOUT=30`, `config.yaml timeout: 5`, `app.py timeout = 10`):

```text
$ python3 stated TIMEOUT …/hybrid-01__effect/fixtures/disagree
status: DECLARED_ONLY
value: 30
declarations:
  .env:2	TIMEOUT=30	value=30
```

Dotenv is config, not env-layer. Case-sensitive: `stated timeout` does **not** pair `TIMEOUT: 5` in YAML with `timeout = 10` in Python (ASSIGNED_ONLY). Env keys are often case-insensitive at the process boundary; stated is not. **MUTATE.**

### 2.4 mutation-05 `first_member_token` eats `${WAIT}` — **FIX**

```text
$ python3 mutation-05__stated-jsonobj/stated timeout reimpl-01__stated/fixtures/unknown
  config.yaml:1	timeout: ${WAIT}	value=${WAIT (not comparable: interpolation)

$ python3 mutation-05__stated-jsonobj/stated --json timeout …/unknown
# declarations[0].raw_value == '${WAIT'   (missing closing brace)
```

`_json_sibling_follows` treats leftover `}` as a JSON closer. Compact-JSON mutation damaged interpolation display. Status is still UNKNOWN (no false DISAGREE). **FIX.** reimpl-01 is clean here.

### 2.5 mutation-05 false assignment from a string literal — **FIX**

```text
# app.py:  msg = "timeout = 99 is wrong"
$ python3 mutation-05__stated-jsonobj/stated timeout …/strlit
status: UNKNOWN
assignments:
  app.py:1	msg = "timeout = 99 is wrong"	value=99 is wrong" (not comparable: unparsed)

$ python3 reimpl-01__stated/stated timeout …/strlit
status: DECLARED_ONLY
value: 5
# start-anchored pattern never saw the string
```

Not DISAGREE (unparsed), but it **flips DECLARED_ONLY → UNKNOWN** by inventing an assignment site. source_key_re is `.*?timeout` anywhere on the line. **FIX** (quote-aware scan, or keep start-anchor for assignments that are not typed prefixes).

### 2.6 reimpl-01 misses `/* x */ int timeout = 10;` — **FIX**

```text
$ python3 reimpl-01__stated/stated timeout …/inline-cmt
status: DECLARED_ONLY   # C assignment invisible

$ python3 mutation-05__stated-jsonobj/stated timeout …/inline-cmt
status: DISAGREE
  contradicted 10	legacy.c:1	/* x */ int timeout = 10;	value=10
```

reimpl comment mask + start-anchored pattern cannot see code after a same-line block comment. mutation-05's line splitter can. **FIX** reimpl (or admit line-level comments cannot do C).

### 2.7 Binary / huge files — split honesty

reimpl skips any file containing NUL (`app.py` with `timeout = 10\n\x00…` vanished → DECLARED_ONLY). mutation-05 `errors=replace` plus no NUL check: `blob.c` of random bytes classified by `file(1)` as *Targa image data* still yields `int timeout = 99` and DISAGREE. **MUTATE** mutation-05: 2MiB cap + replace is not a binary policy.

mutation-05 / candidate-02 `MAX_FILE_BYTES = 2MiB` **silently skips** a 16.7MB `app.py` that starts with `timeout = 10` and ends with `timeout = 99`:

```text
$ python3 mutation-05__stated-jsonobj/stated timeout …/huge-src
status: DECLARED_ONLY
value: 5
# rc=0  — assignment side gone; looks like config-only

$ python3 reimpl-01__stated/stated timeout …/huge-src
status: DISAGREE   # pairs 5 vs 10 and 5 vs 99, 0.45s
```

Head-only 100-byte copy of the same `app.py` DISAGREEs. The cap, not the content, hid the contradiction. **FIX** (announce skip) and **MUTATE** if a cap that can invert DECLARED_ONLY vs DISAGREE is acceptable.

### 2.8 Same-side two configs, no source — **MUTATE**

```text
a.yaml: timeout: 5
b.yaml: timeout: 10
# no app.py
status: DISAGREE
  declared 5 a.yaml:1
  contradicted 10 b.yaml:1
# rc=2
```

The README says the pair is declaration vs assignment. Same-side literals still DISAGREE with the assignment slot filled by another declaration. The algebra is "any two comparable scalars that don't match", not "config vs source". **MUTATE** the pair definition or the copy.

### 2.9 Newline in filename / stdin — **MUTATE**

`config.yaml\nextra` is not a `.yaml` suffix (`path.suffix` is `.yaml\nextra`). ASSIGNED_ONLY from `app.py`. Pathological names drop declarations.

stdin ignored: `printf 'timeout: 5\n' | stated timeout empty-dir` → NONE. Cannot consume `rg` hits. Unix already scored composability 2. **MUTATE** if the pair is going to sit in a pipeline; otherwise leave it a DIR walker and say so.

### Primitive call

**MUTATE stated, do not kill.** The pair + UNKNOWN + exit 2 is the object. mutation-05's compact-JSON leader is the right cut (parent c02 still fails it). Next cuts: quote-aware assignment scan (FIX m05 string site), don't eat `}` of `${WAIT}` (FIX m05), `.env` is env-layer not declaration (effect already flipped this), nested path, case fold for env-shaped keys, announce 2MiB skips.

---

## 3. effect — primitive restated

One record for KEY:

- **DECLARED** — config sites, **excluding dotenv**
- **ASSIGNED** — source assignments
- **ENV_SOURCE** — process/dotenv provenance of KEY, case variant, and names sites defer to (`${WAIT}`, `os.getenv`, `os.environ.get`, `process.env.WAIT`, …)
- **EFFECTIVE** — comparable scalar if layers agree; else `unknown` + reason

Exit 2 only for declared-literal vs assigned-literal. Env provenance is still printed.

Kill test from `hybrid-01__effect/CANDIDATE.md`: *Kill if `stated KEY; envfrom KEY` loses nothing.*

### 3.1 Concatenation loses the deferred join — do not kill

Deferred fixture: `timeout: ${WAIT}`, `timeout = os.getenv("WAIT")`, `.env` `export WAIT=10`, process `WAIT=from-shell`.

```text
$ env WAIT=from-shell python3 effect timeout fixtures/deferred
DECLARED:  config.yaml:1  timeout: ${WAIT}     (interpolation)
ASSIGNED:  app.py:3       os.getenv("WAIT")    (call)
ENV_SOURCE:
  timeout  unset           why=key
  WAIT     file:.env:1     value=10  INHERITED: from-shell  why=deferred
EFFECTIVE:
  10
# rc=0

$ python3 stated timeout fixtures/deferred
status: UNKNOWN
# (mutation-05 even prints value=${WAIT  without the closing brace)

$ env WAIT=from-shell python3 envfrom --dir fixtures/deferred timeout
timeout
VALUE=
SOURCE: unset

$ env WAIT=from-shell python3 envfrom --dir fixtures/deferred WAIT
WAIT
VALUE=10
SOURCE: file:…/.env:1
INHERITED: from-shell

$ env WAIT=from-shell printenv WAIT
from-shell

$ rg -n timeout fixtures/deferred
app.py:3:timeout = os.getenv("WAIT")
config.yaml:1:timeout: ${WAIT}
```

To recover EFFECTIVE 10 from the parents you must **read the sites, name WAIT, and ignore printenv's inherited from-shell**. That is the hybrid. Concatenation of `stated timeout; envfrom timeout` is UNKNOWN + unset. **Not KILL.**

Empty-override of a deferred name also holds:

```text
# fixtures/empty-override: timeout: 5, os.getenv("TIMEOUT", "5"), .env TIMEOUT=
TIMEOUT  file:.env:2  value=(empty)  EMPTY_OVERRIDE: yes  INHERITED: /already/set  why=deferred
EFFECTIVE: unknown    literal 5 vs env (empty)
# rc=0  — not exit 2; env disagreement is not declared-vs-assigned
```

Disagree fixture: `.env TIMEOUT=30` is **not** under DECLARED (stated would have put it there). TIMEOUT shows as `why=case-variant` and does **not** tie-break EFFECTIVE. Honest.

On the agree fixture, concatenation loses little (stated AGREE 5, envfrom timeout unset, effect EFFECTIVE 5). That is not a license to kill; the deferred fixture is the object.

### 3.2 Compact JSON declaration missed — **FIX**

stated mutation-05/reimpl see `{"timeout": 5}`. effect's `config_key_re` is still start-of-line indent/export only — the **pre-mutation** stated pattern.

```text
$ python3 effect timeout /tmp/destroy-config/work/eff-compact
DECLARED:
  (none)
ASSIGNED:
  app.py:1	timeout = 10	value=10
EFFECTIVE:
  10
# rc=0, disagree=false
```

`--json` confirms `"declared": []`, `"effective": {"status":"value","value":"10"}`. The declaration exists; EFFECTIVE is a **false assigned-only 10**. Hybrid dropped the compact-JSON cut its stated parent just grew. **FIX** (copy mutation-05 leaders), not a primitive kill.

### 3.3 Binary `.env` crash — **FIX**

Same uncaught `UnicodeDecodeError` as envfrom (`path.read_text(encoding="utf-8")` in `parse_dotenv`). Source files use `errors="replace"`; dotenv does not. **FIX.**

Self-symlink `.env` is skipped (`WAIT unset`, EFFECTIVE unknown / sites defer to unset env), no hang. Symlink-to-real-file is followed. Good.

### 3.4 Silent 2MiB source skip lies about EFFECTIVE — **FIX**

`app.py` = `timeout = 10\n` + 3MiB of `#`:

```text
DECLARED: config.yaml timeout: 5
ASSIGNED: (none)
EFFECTIVE: 5
# rc=0
```

The assignment exists. EFFECTIVE reports the declared literal as if source were empty. Same class of lie as mutation-05's huge skip, worse because EFFECTIVE claims a value. **FIX:** refuse / note skipped files; never emit `status=value` after a silent drop.

### 3.5 getenv default / computed keys / nested dotenv — **MUTATE**

```text
timeout = os.getenv("MISSING", "5")   # declared 5
EFFECTIVE: unknown   sites defer to unset env
# default 5 is not used even though it agrees with declared 5
```

`process.env[k]` with `k = 'WAIT'` does not follow WAIT; `.env WAIT=10` vanishes. Nested `sub/.env WAIT=99` is invisible (`load_dotenv` only `DIR/.env` and `DIR/.env.local`). `iter_files` skips **any** name starting with `.`, so `.config.yaml timeout: 5` is DECLARED none and EFFECTIVE becomes assigned-only 10. **MUTATE** (follow defaults? walk nested dotenv? don't skip `.config.yaml`?).

### 3.6 `/* */` leftover on the same line — **FIX**

`int timeout = 10; /* café */` (latin-1 `.c`): inline stripper handles `#` and `//`, not `/* */`. Value becomes `10; /* café */` (expression). EFFECTIVE unknown despite a comparable 10. **FIX.**

### 3.7 cwd / missing DIR / pipes / symlink loops

Missing DIR and file-as-DIR: exit 1. cwd vs DIR honored (agree vs disagree). Symlink dir loop does not hang. stdin ignored (same as stated). `.env.local WAIT=` empty-override wins over `.env WAIT=1`; EFFECTIVE `(empty) empty override of WAIT`. Empty KEY: exit 1.

### Primitive call

**MUTATE effect, do not kill.** The four-field record with deferred-name env join is the product. Implementation must not drop compact JSON (FIX), must not crash on binary dotenv (FIX), must not report EFFECTIVE 5 after skipping the file that assigned 10 (FIX). Next cuts: getenv default as a static fallback, nested dotenv, `.config.yaml`, source chain, copy stated's compact-JSON leaders.

---

## 4. Cross-object

| attack | envfrom | stated | effect |
| --- | --- | --- | --- |
| missing DIR | **FIX** silent env | exit 1 | exit 1 |
| binary input | **FIX** traceback | r01 skips NUL; m05 reads junk | **FIX** traceback on `.env`; source `replace` |
| huge file | 9.1MB ok | r01 16.7MB ok; m05 **FIX/MUTATE** silent 2MiB skip | **FIX** silent 2MiB skip → false EFFECTIVE |
| interpolation | **MUTATE** literal `${BAR}` | UNKNOWN (m05 **FIX** `${WAIT` cut) | deferred join **holds** |
| symlink loop | self-`.env` **FIX** silent | dir loop ok | dir loop ok; self-`.env` skipped |
| empty override vs unset | **holds** (the object) | n/a (`.env` is declaration — **MUTATE**) | **holds** on deferred TIMEOUT= |
| cwd vs DIR | honored | honored | honored |
| pipes | stdin ignored (**MUTATE**); `--run` forwards | stdin ignored (**MUTATE**) | stdin ignored (**MUTATE**) |
| compact JSON | n/a | m05/r01 hold; c02 miss | **FIX** miss → false EFFECTIVE 10 |

Unix tools used as honesty checks: `printenv`, `grep`, `rg`, `file`. None of them emit the records these CLIs exist to emit. They do expose silence (hyphen keys, missing DIR, skipped huge files).

---

## 5. Mutation loci (Gen 3, not this pass)

1. **envfrom FIX pack:** exist/isdir on `--dir`; catch UnicodeDecodeError; strip BOM; error on `.env` that exists but is not a readable file; encode newlines in text `VALUE=` (or refuse).
2. **envfrom MUTATE pack:** dropped-line record (`KEY+=`, `FOO-BAR`, invalid UTF-8 line) instead of unset; `${NAME}` as deferred (effect already has the join); source chain `.env` → `.env.local`; `--json --run` stdout split.
3. **stated FIX pack:** mutation-05 `first_member_token` must not cut `${WAIT}`; quote-aware assignment scan (string `"timeout = 99"` is not an assignment); reimpl same-line `/* */` then code; announce MAX_FILE_BYTES skips.
4. **stated MUTATE pack:** dotenv is env-layer (effect's flipped assumption); nested JSON path; case-variant pairing for env-shaped keys; pair algebra when both sides are declarations.
5. **effect FIX pack:** compact-JSON leaders from mutation-05; dotenv decode policy from envfrom FIX pack; never emit EFFECTIVE value after a silent file skip; strip `/* */` leftovers.
6. **effect MUTATE pack:** `os.getenv("X", "5")` static default; nested dotenv; do not skip `.config.yaml` just because it is hidden; computed `process.env[k]` remains out of scope unless a later jump wants it.

No new primitive. No KILL. Concentrate breeding on the join (effect) and the empty-override record (envfrom). stated stays as the pair engine those two sit on — mutate the scanner, keep the pair.
