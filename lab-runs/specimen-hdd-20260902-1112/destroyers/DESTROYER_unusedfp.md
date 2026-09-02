# DESTROYER unusedfp

Date: 2026-09-02 14:20 JST
RUN_ID: specimen-hdd-20260902-1112
Target (harvested): `/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-unusedfp/unusedfp`

sha256 `73aed45f4558748510bb91815c8474af744317991ae5e4c63f7fb7c3b76c3b50` (3852 bytes). No `unusedfp` worktree. Parent tree is coordinator-only; this object was not merged onto `main`. Gradle was not executed.

Origin claim (`CANDIDATE.md` / harvest `hdd-ccprop` / specimen-076): name unread snapshot keys that entered a full identity and changed, while used keys did not. rc=1 when `invalidate_unused`. Kind: USEFUL_COMPOSITION. Owned analog `files/cc_unused_prop.py` already prints the four 12-char hashes and `invalidate_unused True` for hardcoded `path` / `idea.io.use.nio2`. Rejected: invented cache-probe.

Happy path is real. Unit tests 3/3 pass (`python3 -m unittest discover -s tests -v` → `Ran 3 tests in 0.087s` `OK`). `demo.sh` twice, `demo-1.log` / `demo-2.log` byte-identical (`cmp` rc=0). Analog hashes match the CLI (`cd6312a323ca` / `e8e424f35bd2` / `a963701a18cc`). That is not enough.

This candidate is a **THIN_WRAPPER** of two `sha256(json.dumps(..., sort_keys=True))[:12]` hashes plus set difference of keys not in `--used`. `inspect()` never observes a read, never execs a build, never fingerprints like configuration-cache. Host replica of `inspect` + `format_report` is **byte-identical** to the CLI on the owned pair (`cmp` rc=0, 210 bytes). `awk` of first-`=` plus “key not used and values differ” prints `idea.io.use.nio2`. `comm -3` on the two fixtures is the same two lines. Decision: **KILL**.

CLI used below:

```text
CLI=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-unusedfp/unusedfp
FIX=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-unusedfp/fixtures
ANALOG=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-076/files/cc_unused_prop.py
```

No merge onto `main`. No Gradle. Do not fold this printer into a configuration-cache log parser as a “fix”.

---

## What still works

Owned pair and unseen `ORG_GRADLE_PROJECT_value` pair, **when the caller already knows `--used` and both maps are `NAME=VALUE` with no spaces around `=`**.

```bash
python3 "$ANALOG"
python3 "$CLI" "$FIX/076-first.env" "$FIX/076-second.env" --used path
echo rc=$?
```

```text
used_keys path
unused idea.io.use.nio2
all_first cd6312a323ca all_second e8e424f35bd2 all_same False
used_first a963701a18cc used_second a963701a18cc used_same True
invalidate_unused True
analog_rc=0

used	path
unused	idea.io.use.nio2
changed_unused	idea.io.use.nio2
all_first	cd6312a323ca
all_second	e8e424f35bd2
used_first	a963701a18cc
used_second	a963701a18cc
all_same	no
used_same	yes
invalidate_unused	yes
rc=1
```

Unseen `src` / `ORG_GRADLE_PROJECT_value`: `changed_unused	ORG_GRADLE_PROJECT_value`, rc=1. Symlink, FIFO, process substitution, filename with a space, CRLF: same owned TSV, rc=1. Missing path / directory / invalid UTF-8 / empty name `=value`: `unusedfp: …` rc=1. No args / one arg: argparse rc=2.

That is the whole useful delta. It is also what two hashes of caller-supplied dicts plus `k not in used and a.get(k) != b.get(k)` already do. Attacks below break the “unread keys entered identity” claim, or show the primitive cannot grow.

---

## Implementation

`ident` / `inspect` in full:

```python
def ident(props: dict[str, str]) -> str:
    return hashlib.sha256(json.dumps(props, sort_keys=True).encode()).hexdigest()[:12]

# unused = keys not in used (first, then second, unique)
# changed_unused = [k for k in unused if first.get(k) != second.get(k)]
# used_first = {k: first[k] for k in used if k in first}
# invalidate_unused = (not all_same) and used_same and bool(changed_unused)
```

`inspect.__code__.co_names` is `('append', 'get', 'ident', 'bool')`. `ident.co_names` is `('hashlib', 'sha256', 'json', 'dumps', 'encode', 'hexdigest')`. Identity of `{}` is `44136fa355b3`. Identity of `{"path":"/app"}` is `a963701a18cc`. Those four hex strings are not Gradle configuration-cache entry IDs.

### 1. THIN_WRAPPER: two hashes plus set difference is the product

Host replica of `inspect` + `format_report` on the owned pair is byte-identical to the CLI (`wrapper == cli: True`, `cmp` rc=0, 210 bytes). Same for unseen and for used-also-changed.

Nearest ordinary workflow, host-executed:

```bash
python3 -c '
import hashlib, json, sys
def parse(p):
    d = {}
    for raw in open(p, encoding="utf-8"):
        line = raw.strip()
        if not line or line.startswith("#"): continue
        k, _, v = line.partition("=")
        d[k] = v
    return d
def ident(d):
    return hashlib.sha256(json.dumps(d, sort_keys=True).encode()).hexdigest()[:12]
a, b, used = parse(sys.argv[1]), parse(sys.argv[2]), sys.argv[3:]
unused = []
for k in list(a) + [k for k in b if k not in a]:
    if k not in used and k not in unused: unused.append(k)
changed = [k for k in unused if a.get(k) != b.get(k)]
ua = {k: a[k] for k in used if k in a}; ub = {k: b[k] for k in used if k in b}
inv = (ident(a) != ident(b)) and ident(ua) == ident(ub) and bool(changed)
print("changed", *changed or ["-"])
print("all", ident(a), ident(b), ident(a) == ident(b))
print("usedh", ident(ua), ident(ub), ident(ua) == ident(ub))
print("invalidate", inv)
sys.exit(1 if inv else 0)
' "$FIX/076-first.env" "$FIX/076-second.env" path
echo replica_rc=$?
comm -3 <(sort "$FIX/076-first.env") <(sort "$FIX/076-second.env")
```

```text
changed idea.io.use.nio2
all cd6312a323ca e8e424f35bd2 False
usedh a963701a18cc a963701a18cc True
invalidate True
replica_rc=1
idea.io.use.nio2=false
	idea.io.use.nio2=true
```

`awk` of first `=` plus “key ≠ used and values differ” prints `idea.io.use.nio2` (rc=0). `demo.sh` already says the nearest operation is “print two hashes” and that those hashes do not name the unread key. The CLI names it by set difference of keys the caller marked unused. The analog already knew the name: `UNUSED = "idea.io.use.nio2"`. The harvest said printing both encodings still leaves the unread key as a hand join. The CLI still leaves `--used` as a hand join.

### 2. Used key that also changed: predicate rc=0; spaces around `=` invert it

`path=/app` → `path=/other` and `idea.io.use.nio2=false` → `true`, `--used path`:

```text
used	path
unused	idea.io.use.nio2
changed_unused	idea.io.use.nio2
all_same	no
used_same	no
invalidate_unused	no
rc=0
```

The unread key changed and is named. `invalidate_unused` is false because used also changed. Fine as the documented AND. Used-only change (`nio2` stable): `changed_unused	-`, rc=0. Two `--used` keys with one changed: same rc=0. Used present only in first, unused stable: `used_same	no`, `changed_unused	-`, rc=0.

`path = /app` vs `path = /other` (spaces around `=`), same nio2 flip, still `--used path`:

```text
used	path
unused	path 	idea.io.use.nio2
changed_unused	path 	idea.io.use.nio2
used_first	44136fa355b3
used_second	44136fa355b3
used_same	yes
invalidate_unused	yes
rc=1
```

`raw.strip()` then `partition("=")` keeps `path ` as the name and ` /app` as the value. `--used path` matches neither map. Used identity is `sha256("{}")` on both sides. The used key **did** change and the CLI reports unused invalidation. Java `.properties` trims around `=`. This parser does not.

`--used idea.io.use.nio2` on the owned pair (caller lies, or the unread key was actually read): `changed_unused	-`, `used_same	no`, rc=0. The CLI believes argv.

### 3. Unused that did not change

Owned nio2 flip plus `stable=1` both sides, `--used path`:

```text
unused	idea.io.use.nio2	stable
changed_unused	idea.io.use.nio2
invalidate_unused	yes
rc=1
```

`stable` stays on `unused` and is omitted from `changed_unused`. Identical maps: `changed_unused	-`, `all_same	yes`, rc=0. Key order only (`sort_keys=True`): `all_same	yes`, rc=0. Unused added or dropped (presence): `changed_unused` names it, rc=1. Empty value vs missing (`idea.io.use.nio2=` vs absent): changed, rc=1.

That is set difference. It is the whole product. Tests never hit an unchanged unused key.

### 4. Empty maps

Empty file / comments-only / `/dev/null` vs itself, `--used path`:

```text
used	path
unused	-
changed_unused	-
all_first	44136fa355b3
all_second	44136fa355b3
used_first	44136fa355b3
used_second	44136fa355b3
all_same	yes
used_same	yes
invalidate_unused	no
rc=0
```

`44136fa355b3` is `sha256(b"{}")[:12]`. Used key `path` is absent; used identity is the empty dict, same as all-identity of an empty map.

Empty vs `idea.io.use.nio2=true` (used still absent): `used_same	yes`, `invalidate_unused	yes`, rc=1. Empty vs `path=/app`: `used_same	no`, rc=0. Empty values `path=` / `idea.io.use.nio2=` vs themselves: rc=0, unused named, unchanged.

`--used not_a_key` on the owned pair is the empty-used-identity trick: `used_first` / `used_second` are both `{}`, `used_same	yes`, `changed_unused	idea.io.use.nio2`, rc=1. Dummy `--used` makes every value change look like unused invalidation.

### 5. Missing `--used`: same rc as invalidate

```text
python3 "$CLI" "$FIX/076-first.env" "$FIX/076-second.env"
unusedfp: need at least one --used key
rc=1
```

Owned invalidate is also rc=1. A pipe cannot tell “forgot the flag” from “unread key changed.” Empty maps without `--used`: same stderr, rc=1.

`--used ''` is **not** missing. `if not args.used` is false for `['']`:

```text
used
unused	path	idea.io.use.nio2
changed_unused	idea.io.use.nio2
used_first	44136fa355b3
used_second	44136fa355b3
invalidate_unused	yes
rc=1
```

`--used path --used path` duplicates the used column (`used	path	path`) and still invalidates. `--used path,idea.io.use.nio2` is one dummy name, not two keys: used identity empty, rc=1. `--used path --used idea.io.use.nio2` (both keys actually listed): `unused	-`, `used_same	no`, rc=0. The harvest question was which keys configuration **read**. The CLI demands that answer as argv and will not discover it.

### 6. Extra equals

`partition("=")` keeps everything after the first `=` as the value. That is correct for `FOO=bar=baz` and lethal for identity-as-Gradle.

| input vs owned-false | result |
| --- | --- |
| `idea.io.use.nio2==false` | value `=false`, hash `2aabe52226f8`, `changed_unused` nio2, rc=1 |
| `url=http://x` vs `url=http://x?a=1&b=2` | `changed_unused	url`, rc=1 |
| `FOO=bar=baz` vs `FOO=bar` | `changed_unused	FOO`, rc=1 |
| `=value` / `=` / `path=/app` then `==` | `empty name`, rc=1 |
| `path:/app` (Java colon separator) | `expected NAME=VALUE`, rc=1 |
| `path /app` (no `=`) | `expected NAME=VALUE`, rc=1 |
| `path = /app` (spaces) | key `path `, `--used path` misses, see §2 |
| `idea.io.use.nio2=false` then `=true` vs `=true` | last-wins, `all_same	yes`, `changed_unused	-`, rc=0 |
| `idea.io.use.nio2\=false` | extra unused key `idea.io.use.nio2\`, both unused keys “changed”, rc=1 |

Duplicate last-wins is silent. A store that wrote false then true compared to a store that wrote true looks identical. Tests never hit extra `=`, colon, spaces, or duplicates.

### 7. Stdin

```text
python3 "$CLI" - "$FIX/076-second.env" --used path
unusedfp: [Errno 2] No such file or directory: '-'
rc=1
```

Second `-`: same ENOENT rc=1. Pipe without paths: argparse rc=2. `/dev/stdin` as first with the first map redirected: owned TSV, rc=1 (one file can be stdin). `/dev/stdin` `/dev/stdin` with one map on the pipe:

```text
all_first	cd6312a323ca
all_second	44136fa355b3
used_first	a963701a18cc
used_second	44136fa355b3
used_same	no
invalidate_unused	no
rc=0
```

First open consumes the pipe; second is the empty map. Used identity disagrees because `path` is only on the first side. The unread nio2 change is still printed (`changed_unused	idea.io.use.nio2`) and the predicate is false. False negative vs the owned case. Process substitution and FIFO of two real files still work (rc=1).

### 8. Parse edges (non-fatal except where noted)

| input | rc | note |
| --- | --- | --- |
| missing path | 1 | `No such file or directory` |
| directory as map | 1 | `Is a directory` |
| empty file / `/dev/null` | 0 | empty identity `44136fa355b3` |
| invalid UTF-8 | 1 | `'utf-8' codec can't decode` |
| UTF-8 BOM | 0 | key `\ufeffpath`; `--used path` misses; `used_same	no` |
| NUL-prefixed `path=/app` | 0 | key `\x00\x01\x02path`; used misses; `used_same	no` |
| tab in unused value | 1 | value differs; TSV still one field on `changed_unused` (names only) |
| 5000 unused keys | 1 | 57956-byte stdout, one tab-separated `unused`/`changed_unused` line, 0.17s, no cap |
| 2MB unused value | 1 | stdout 186 bytes (names the key `blob`, hashes the blob) |
| two positional extras | 2 | argparse |
| comments / blank lines | 0 | skipped |
| CRLF | 1 | `splitlines`, owned invalidate |
| symlink / space in filename | 1 | works |

BOM and binary-prefix do not save the identity holes. They make `--used path` miss, so used-same becomes a comparison of `{}` vs `{path:/app}`.

Tests never hit used-also-changed, unchanged unused, empty maps, extra `=`, stdin, BOM, duplicates, or dummy `--used`. Three tests: owned, unseen copy of owned, missing `--used` (rc=1 only, no stderr assert).

---

## Primitive

Reality-stripped operation: parse two `NAME=VALUE` files into dicts; `sha256(json.dumps(sort_keys=True))[:12]` of all keys vs the subset whose names appear in `--used`; print unused keys whose `dict.get` values differ; rc=1 iff all-hash changed **and** used-hash did not **and** that set is nonempty.

Nearest ordinary workflow: `comm -3` / `diff` of the two maps, or the owned analog which already prints the four hashes and `invalidate_unused`. Observable capability lost if unusedfp vanishes: **none**. The two property files already are the input. `--used` is still a hand join after the TSV. The 12-char strings are JSON dumps, not configuration-cache fingerprints. `cc_miss.txt` already names `idea.io.use.nio2`. This CLI will not read that log.

That is why this is KILL, not MUTATE. The *question* (an unread system property entered snapshot identity and flipped the second configuration-cache store) is a real debugging object. This embodiment does not ask it. It asks `sha256(json.dumps(a))` vs `sha256(json.dumps(used-subset))` plus set difference. Adding a Gradle log parser, an observed read-set, or a real fingerprint would be implementing the composition this artifact failed to embody — a new harvest, not a patch of two hashes. Constitution: a THIN_WRAPPER does not gain exotic exec features to escape classification. Worker rule: do not send THIN_WRAPPER back to R1 with “make this more novel.”

Hardcoded ceiling:

- identity = truncated JSON sha256 of caller maps, including empty `{}` = `44136fa355b3`
- `--used` is argv, including `''`, absent names, comma-as-one-name, and “I used the key that changed”
- used identity **omits** missing used keys, so dummy `--used` and spaces around `=` make used-same of two empty dicts
- `changed_unused` = `get` inequality, including extra `=`, presence, empty-vs-missing
- duplicate keys last-wins
- `-` is not stdin; two `/dev/stdin` is empty-second map, rc=0
- missing `--used` and invalidate share rc=1
- 5000-key dumps; BOM/NUL hide `--used path`
- Dreamer cache-probe was rejected; this is that inspect, reduced to two hashes plus set difference

Honor KILL. Dreamer ancestry is not protection.

Do not merge onto `main`. Do not execute Gradle to mint a remainder.

---

KILL
