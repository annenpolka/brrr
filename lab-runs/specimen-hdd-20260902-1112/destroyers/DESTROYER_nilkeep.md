# DESTROYER nilkeep

Date: 2026-09-02 14:35 JST
RUN_ID: specimen-hdd-20260902-1112
Target (harvested): `/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-nilkeep/nilkeep`

sha256 `1d7d89e19547774aca7d46fc36cb9051b063c4fd87438ccc18faa45966b57e68` (3303 bytes). No `nilkeep` worktree. Parent tree is coordinator-only; this object was not merged onto `main`. Helm was not executed (`helm` not on PATH).

Origin claim (`CANDIDATE.md` / harvest `hdd-helmnull` / specimen-079): name a user-null key dropped by empty-map default coalesce and kept by a null chart default. rc=1 when dropped is nonempty. Kind: USEFUL_COMPOSITION. Owned packet: chart `data: {}` + user `baz: ~` → `map[foo:bar]`; chart `data: ~` + same user → `map[baz:<nil> foo:bar]`. Rejected: invented helm template / coalesce.go theater. Constraint: owned two coalesce records. No helm.

Happy path is real. Unit tests 3/3 pass (`python3 -m unittest discover -s tests -v` → `Ran 3 tests in 0.077s` `OK`). `demo.sh` twice, `demo-1.log` / `demo-2.log` byte-identical (`cmp` rc=0). That is not enough.

This candidate is a **THIN_WRAPPER** of `if default==empty-map and value is null`. `inspect()` never coalesces two maps, never emits an omitted-vs-present-nil result map, never contrasts empty-map vs null default on the same user keys. Host replica of `inspect` + `format_report` is **byte-identical** to the CLI on the owned pair and on unseen (`cmp` rc=0, 54 / 51 / 57 bytes). `awk` of `user` rows whose value is in `{~,null,nil,<nil>,-}` prints `baz`. The harvest AND (dropped-by-empty-map ∩ kept-by-null) is exactly `user_nulls`. Decision: **KILL**.

CLI used below:

```text
CLI=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-nilkeep/nilkeep
FIX=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-nilkeep/fixtures
S079=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-079
```

No merge onto `main`. No helm. Do not fold this printer into a coalesce simulator as a “fix”.

---

## What still works

Owned empty-map record, owned null-default record, unseen `gone`/`keep`, and any other TSV whose `default` token is `empty-map`/`{}`/`null`/`~` and whose `user` values are already classified as null-or-not.

```bash
python3 "$CLI" "$FIX/079-empty-map.rec"; echo rc=$?
python3 "$CLI" "$FIX/079-null-default.rec"; echo rc=$?
python3 "$CLI" "$FIX/unseen.rec"; echo rc=$?
```

```text
default	empty-map
user_nulls	baz
kept	foo
dropped	baz
rc=1

default	null
user_nulls	baz
kept	foo	baz
dropped	-
rc=0

default	empty-map
user_nulls	gone
kept	keep
dropped	gone
rc=1
```

`default {}` aliases empty-map. `default ~` aliases null. Symlink, FIFO (writer concurrent), process substitution, filename with a space, CRLF, Unicode key `バツ`: same predicate, rc=1 when a user-null is present under empty-map. Missing path / directory / empty file / `/dev/null` / comments-only / invalid UTF-8 / BOM: `nilkeep: …` rc=1. No args / extra arg: argparse rc=2.

That is the whole useful surface. It is also what `if default==empty-map and is_null(val)` already does. Attacks below break the claim that this names a coalesce identity, or show the primitive cannot grow without becoming helm theater.

---

## Implementation

`inspect()` / `is_null()` in full:

```python
def is_null(value: str) -> bool:
    return value in {"~", "null", "nil", "<nil>", "-"}

def inspect(rec: dict) -> dict:
    kept: list[str] = []
    dropped: list[str] = []
    for name, val in rec["user"].items():
        if rec["default"] == "empty-map" and is_null(val):
            dropped.append(name)
        else:
            kept.append(name)
    return {
        "default": rec["default"],
        "kept": kept,
        "dropped": dropped,
        "user_nulls": [n for n, v in rec["user"].items() if is_null(v)],
    }
```

`inspect.__code__.co_names` is `('items', 'is_null', 'append')`. `is_null.co_names` is `()`. There is no map merge, no src/dst, no omitted-vs-present-nil result.

When `default` is `empty-map`, `dropped == user_nulls` always. When `default` is `null`, `dropped` is always empty and `kept` is every user key. The advertised composition (dropped by empty-map **and** kept by a null default) is therefore `user_nulls` on one record. Two quoted maps still leave the default-shape join as a hand comparison. Two CLI runs do too.

### 1. THIN_WRAPPER: `if default==empty-map and value is null` is the product

Host replica of `inspect` + `format_report` on the owned pair is byte-identical to the CLI (`wrapper == cli: True`, `cmp` rc=0):

| file | bytes | rc | cmp |
| --- | --- | --- | --- |
| `079-empty-map.rec` | 54 | 1 | 0 |
| `079-null-default.rec` | 51 | 0 | 0 |
| `unseen.rec` | 57 | 1 | 0 |

Same replica also matched both-non-null, empty-user, foo-null-too, and `{}`/`~` aliases (`stdout_eq=True` on all eight).

Nearest ordinary workflow, host-executed:

```bash
awk -F'\t' '$1=="user" && ($3=="~"||$3=="null"||$3=="nil"||$3=="<nil>"||$3=="-"){printf("%s%s",(n?"\t":""),$2); n=1} END{if(!n) printf("-"); print ""}' "$FIX/079-empty-map.rec"
```

```text
baz
```

`awk == dropped == user_nulls` on empty-map and on unseen. On the null-default sibling, `dropped` is `-` while `user_nulls` is still `baz`. The default token is a boolean that either copies `user_nulls` into `dropped` or prints `-`.

Hand join of the two owned runs:

```text
empty-map dropped ['baz']  kept ['foo']     user_nulls ['baz']
null      dropped ['-']    kept ['foo','baz'] user_nulls ['baz']
dropped_empty ∩ kept_null == {'baz'} == user_nulls
```

The harvest delta (“kept no vs kept yes for baz”) reconstructs from the user-null column of **one** file. Concatenating the two reports does not discover a coalesce. It reprints `is_null`.

### 2. Both non-null: default shape is a sticker

```text
default	empty-map
user	foo	bar
user	baz	qux
```

and the same user rows under `default	null`:

```text
default	empty-map
user_nulls	-
kept	foo	baz
dropped	-
rc=0

default	null
user_nulls	-
kept	foo	baz
dropped	-
rc=0
```

Bodies after the `default` line are **byte-identical**. rc=0 both. Empty-map vs null default does not change kept, dropped, user_nulls, or exit. The specimen contrast requires a user-null. Without one, the CLI is a default-kind echo plus `kept` of names the caller already typed.

### 3. Default misspell

Real misspellings refuse (`default must be empty-map or null`, rc=1, no stdout): `empty_map`, `emptymap`, `Empty-map`, `EMPTY-MAP`, `empty map`, `empty`, `map`, `none`, `None`, `nil`, `undefined`, `[]`, `false`, `0`, `Null`, `NULL`, `{ }`, `emptyMap`, `empty-maps`. Honest. Not a save.

`rest.strip()` makes surrounding whitespace on an **allowed** token succeed: `' empty-map'`, `'empty-map '`, `'null '`, `' ~'` all classify. `{}\t` strips to `{}` and aliases empty-map (owned TSV, rc=1). `default {}` and `default ~` are the documented aliases, not misspellings.

The allowlist is four strings. A non-empty table default (`{foo: bar}`, the other helm table path that also runs `coalesceTablesFullKey`) is unrepresentable. `merge=true` is unrepresentable. The specimen’s mechanism is table-default vs nil-default. The CLI’s switch is the harvest nickname `empty-map`.

### 4. Empty user

```text
default	empty-map
```

and `default	null` with no `user` rows:

```text
default	empty-map
user_nulls	-
kept	-
dropped	-
rc=0

default	null
user_nulls	-
kept	-
dropped	-
rc=0
```

Bodies after `default` are identical. Nothing is named. rc=0 is “dropped empty”, which is also success of keep. An empty-map coalesce of an empty user table vs a null default of an empty user table is not a contrast the CLI can state, because it never builds a result map.

Same TSV as a user key literally named `-` with a non-null value (`user	-	bar`, empty-map): `user_nulls	-` / `kept	-` / `dropped	-` / rc=0. `stdout_eq=True` against empty user. A user key named `-` whose value is `~` prints the **same three dashes**, rc=1. Only the exit bit distinguishes “dropped the key named `-`” from “dropped nothing”. The empty-list sentinel is also a null token and also a legal key.

### 5. Foo null too

```text
default	empty-map
user	foo	null
user	baz	~
```

```text
default	empty-map
user_nulls	foo	baz
kept	-
dropped	foo	baz
rc=1
```

Null default: `user_nulls	foo	baz` / `kept	foo	baz` / `dropped	-` / rc=0. Both user-nulls are copied to `dropped` under empty-map. There is no coalesced `map[…]`. There is no chart-default key that was not in the user file. `foo` was non-null in the specimen and survived; making it null too does not change the rule, it only lengthens `user_nulls`. Order is insertion order. `foo	~` and `foo	null` are the same class.

The harvest identity is omitted vs present-nil **in `.Values.data`**. This printer lists names. `kept	-` with `dropped	foo	baz` is not `map[]`. `kept	foo	baz` under null default is not `map[baz:<nil> foo:bar]`.

### 6. Stdin

```text
python3 "$CLI" -          # with owned body on the pipe
nilkeep: [Errno 2] No such file or directory: '-'
rc=1

python3 "$CLI"            # same body on stdin, no argv
usage: nilkeep [-h] record
rc=2

python3 "$CLI" /dev/stdin # same body
default	empty-map
user_nulls	baz
kept	foo
dropped	baz
rc=1
```

`-` is not stdin. Argv-less invocation ignores the pipe. `/dev/stdin` happens to work because `Path.read_text` opens that node. Tests never pass `-`. Fine as a file tool; hostile as a pipe component.

### 7. `is_null` is a five-string set; empty values cannot be written

Under empty-map, `baz` is dropped iff the value token is exactly one of `~` `null` `nil` `<nil>` `-`. Host-executed:

| value | dropped | notes |
| --- | --- | --- |
| `~` `null` `nil` `<nil>` `-` | `baz` | allowlist |
| `~ ` (trailing space) | `baz` | `rest.strip()` eats trailing space **before** the name/value split |
| `null\t` | `baz` | trailing tab stripped the same way |
| ` ~` / `  ~` (leading space on value) | `-` | value is not stripped after the second split; not in the set |
| `NULL` `Null` `None` `none` `Nil` `<NIL>` | `-` | kept as ordinary strings |
| `false` `0` `{}` `[]` `"~"` `'~'` `!!null` | `-` | kept |
| empty / whitespace-only value | parse error | `user needs name<TAB>value` — `rest.strip()` deletes the value tab |

YAML empty (`baz:`) and quoted `"~"` are not this dialect. `nil` and `<nil>` are Go-quote spellings pasted into the allowlist; they are not YAML null. `-` is YAML null **and** the empty-list sentinel (see §4).

### 8. Duplicate keys last-wins, silent rc on the last value

`user baz bar` then `user baz ~` (empty-map): `dropped	baz` rc=1, as if baz had always been null. Reverse: `dropped	-` rc=0, the first null is gone. Two `default` lines: last-wins. `default empty-map` then `default null` keeps baz. Tests never repeat a key.

Unknown field / `Default` capitalized / spaces instead of tabs / YAML `data: {}` / specimen `helm_template_split.txt` / `coalesce_tables_failing.go` / `OBSERVED.md`: `expected key<TAB>value` or `unknown field`, rc=1. Honest refuse. It also means the origin packet cannot enter. The owned fixtures are already the harvest sentence, typed as TSV.

### 9. Huge kept dump; no cap

10000 user keys, one `~` at `k7` (~168kB): `dropped	k7`, `kept` is the other 9999 names, rc=1, ~0.03s. 2000 all-null keys: stdout 21824 bytes, 2000 dropped names, rc=1, ~0.03s. Fine as a printer; hostile as a pipe predicate. The useful bit is still `user_nulls`.

UTF-8 BOM is `unknown field '\ufeffdefault'` (rc=1). Invalid UTF-8 / embedded NUL: codec / unknown-field rc=1. No filename on the codec error.

---

## Primitive

Reality-stripped operation: parse a TSV of `default KIND` plus `user NAME VALUE`; `KIND in {empty-map,{},null,~}`; if KIND is empty-map, copy names whose value is in `{~,null,nil,<nil>,-}` to `dropped`, else `dropped` is empty; print TSV; rc=1 iff `dropped` is nonempty.

Nearest ordinary workflow: `awk` of user-null tokens, or `python3 -c '… is_null …'` on the same TSV, or printing both harvest maps (`map[foo:bar]` vs `map[baz:<nil> foo:bar]`) and comparing by eye. Observable capability lost if nilkeep vanishes: **none**. The two coalesce records already are the input. The default-shape join is still a hand comparison after one or two CLI runs. `user_nulls` is the product.

That is why this is KILL, not MUTATE. The *question* (this user-null was omitted under an empty-map chart default and present-nil under a null chart default) is a real debugging object. This embodiment does not ask it of two maps. It asks `if default==empty-map and is_null(val)` on caller-labeled tokens. Pairing two records and printing `dropped_A ∩ kept_B` would still be `user_nulls`. Ingesting chart YAML + user YAML and running a coalesce would be implementing the helm theater the harvest rejected, and would be a new harvest, not a patch of this 100-line if. Constitution: a THIN_WRAPPER does not gain exotic features to escape classification. Worker rule: do not send THIN_WRAPPER back to R1 with “make this more novel.”

Hardcoded ceiling:

- `dropped` = `user_nulls` when default is empty-map, else empty
- default shape is a sticker when there are no user-nulls (both-non-null, empty user)
- `is_null` = five strings; `NULL` / quoted `~` / empty value are not null; empty value is unparseable
- `-` is null and empty-list and a legal key; those three TSV columns collide
- unary record; the harvest AND is two invocations plus a hand join
- non-empty table default and `merge=true` cannot be written
- origin YAML / go excerpts refuse
- `-` is not stdin; argv-less stdin is argparse rc=2
- duplicate user/default last-wins
- 10k `kept` names dump
- rc=1 iff the if’s dropped list is nonempty, including the sentinel key `-`
- Dreamer helm template / coalesce.go was rejected; this is that coalesce, reduced to the harvest sentence as an if

Honor KILL. Dreamer ancestry is not protection.

Do not grow a helm coalesce or a YAML loader to escape THIN_WRAPPER. Do not merge this join onto `main`.

---

KILL
