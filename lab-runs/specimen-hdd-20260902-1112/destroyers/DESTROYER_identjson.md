# DESTROYER identjson

Date: 2026-09-02 14:59 JST
RUN_ID: specimen-hdd-20260902-1112
Target (harvested, post exceptional jump): `/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-identjson/identjson`

sha256 `9bac058a6ada10a173f13b9e96393555d13bf135c1a8e866dc1b787821c01255` (4536 bytes, 144 lines). Jump parent `357b9f2df62faca8cccbd0f4fcb376a027606f32230bc2390b4364648cc17c6b` (3900 bytes) is recorded in `lineages/candidate-identjson/MUTATE.md` (applied 14:56 JST). No `identjson` worktree. Parent tree is coordinator-only; this object is not tracked on `main` and was not merged. `terraform` is on PATH (`/opt/homebrew/bin/terraform`) and **was not executed**. No cty.

Origin claim (`CANDIDATE.md` / harvest `hdd-tfident` / specimen-081 leftover IdentityJSON vs nil identity schema): name the decode class of leftover identity JSON against a nil or present identity schema — object, omitted, typed-null, empty-object, or unsupported-attribute error. rc=1 on decode error. Kind: USEFUL_COMPOSITION. Owned packet: leftover `{"id":"foo"}` + `Identity: nil` → error; same JSON + schema `id` → object; omitted JSON → omitted; `{"arn":"foo"}` vs schema `id` → same unsupported-attribute class. Jump added JSON `null` → typed-null, `{}` vs nil → empty-object, spaced schema lists. Rejected: invented terraform Decode transcripts. Constraint: no terraform.

Happy path is real. Unit tests 10/10 pass (`python3 -m unittest discover -s tests -v` → `Ran 10 tests in 0.265s` `OK`). `demo.sh` twice, `demo-1.log` / `demo-2.log` byte-identical (`cmp` rc=0). That is not enough.

This candidate is a **THIN_WRAPPER** of `json.loads` + key subset. The 14:56 jump split omit-tokens from JSON `null` and labeled empty keys `empty-object`. `inspect()` still never unmarshals against ImpliedType, never constructs a typed null of a schema type, never checks missing required attributes or value types. Host replica of current `inspect` + `format_report` is **byte-identical** to the CLI on all ten fixtures (`cmp` rc=0) and on unseen missing-required / values-ignored / `{}` vs `id` / JSON `null` / omit vs present schema / extra spaces (`stdout_eq=True`). `jq 'keys - $allow'` prints the extra keys the CLI names `unsupported-attribute`. A python one-liner classifies all ten fixtures as the CLI’s `decode` column (`match True`). `MUTATE.md` leftover: “If a later mutation still is only `json.loads` + `keys - fields` and calls that cty, KILL as THIN_WRAPPER.” This is that mutation. Decision: **KILL**.

CLI used below:

```text
CLI=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-identjson/identjson
FIX=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-identjson/fixtures
S081=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-081
```

No merge onto `main`. No terraform. Do not fold this printer into a cty/terraform Decode simulator as a “fix”. Do not send it back to R1 to make the wrapper more novel.

---

## What still works

Owned leftover, owned present schema, owned omitted JSON, owned arn-vs-id mismatch, jump fixtures (JSON `null`, present-schema omitted, `{}` vs nil, spaced / comma-spaced field lists), and any other TSV whose `schema` token is `nil`/`-`/`none`/`empty`/`{}`/`empty-object` or a split field list and whose `identity_json` is already a one-line JSON value or an omit token.

```bash
python3 "$CLI" "$FIX/081-nil-leftover.rec"; echo rc=$?
python3 "$CLI" "$FIX/081-schema-present.rec"; echo rc=$?
python3 "$CLI" "$FIX/081-nil-json.rec"; echo rc=$?
python3 "$CLI" "$FIX/081-mismatch.rec"; echo rc=$?
python3 "$CLI" "$FIX/081-typed-null.rec"; echo rc=$?
python3 "$CLI" "$FIX/081-empty-object.rec"; echo rc=$?
```

```text
schema	nil
json	present
decode	error
error_class	unsupported-attribute
rc=1

schema	present
json	present
decode	object
error_class	-
rc=0

schema	nil
json	omitted
decode	omitted
error_class	-
rc=0

schema	present
json	present
decode	error
error_class	unsupported-attribute
rc=1

schema	nil
json	null
decode	typed-null
error_class	-
rc=0

schema	nil
json	empty-object
decode	empty-object
error_class	-
rc=0
```

`error_class` is only `unsupported-attribute` or `-`.

Symlink, FIFO (writer concurrent), process substitution, filename with a space, CRLF: same predicate. 10000-key leftover vs nil (~158kB JSON): `decode	error`, rc=1, stdout still 71 bytes. Missing path / directory / empty file / `/dev/null` / comments-only / invalid UTF-8 / BOM: `identjson: …` rc=1. No args / extra arg: argparse rc=2.

That is the whole useful surface. It is also what `json.loads` + `(keys - schema)` plus `obj is None` / `not keys` already does.

---

## Implementation

Current `inspect()` (post-jump):

```python
OMITTED_JSON = {None, "", "-", "none", "nil"}
NIL_SCHEMA = {"nil", "-", "none", "empty"}
EMPTY_SCHEMA = {"{}", "empty-object"}

def schema_fields(schema: str) -> list[str] | None:
    if schema in NIL_SCHEMA:
        return None
    if schema in EMPTY_SCHEMA:
        return []
    return [p for p in schema.replace(",", " ").split() if p]

def inspect(rec: dict) -> dict:
    fields = schema_fields(rec["schema"])
    schema_kind = "nil" if fields is None else "present"
    raw = rec["identity_json"]
    if raw in OMITTED_JSON:
        return {..., "json": "omitted", "decode": "omitted", ...}
    obj = json.loads(raw)
    if obj is None:
        return {..., "json": "null", "decode": "typed-null", ...}
    if not isinstance(obj, dict):
        raise ValueError("identity_json must be a JSON object")
    keys = list(obj.keys())
    json_kind = "empty-object" if not keys else "present"
    empty_implied = fields is None or fields == []
    if empty_implied:
        if keys:
            return {..., "decode": "error", "error_class": "unsupported-attribute"}
        return {..., "decode": "empty-object"}
    extra = [k for k in keys if k not in fields]
    if extra:
        return {..., "decode": "error", "error_class": "unsupported-attribute"}
    return {..., "decode": "object"}
```

`inspect.__code__.co_names` is `('schema_fields', 'OMITTED_JSON', 'json', 'loads', 'JSONDecodeError', 'ValueError', 'isinstance', 'dict', 'list', 'keys')`. `schema_fields.co_names` is `('NIL_SCHEMA', 'EMPTY_SCHEMA', 'replace', 'split')`. There is no ImpliedType, no Unmarshal, no typed null of a schema type, no required-attribute check.

When schema is nil or `{}`/`empty-object`, `decode==error` iff `json.loads` is a nonempty object. When schema is a field list, `decode==error` iff any key is outside that list. Missing keys are object. Values are never read. JSON `null` is `obj is None`. Omit tokens never call `loads`. The advertised composition (leftover-vs-nil shares the mismatch error class; `{}` is EmptyObject success; `null` is typed-null) is therefore `json.loads` result-kind plus `keys - allow`, with nil/`{}` schema meaning `allow=[]`.

---

## Attacks

### 1. THIN_WRAPPER: `json.loads` + key subset is still the product

Host replica of current `inspect` + `format_report` on all ten fixtures is byte-identical (`stdout_eq=True`, `cmp` rc=0):

| file | decode | bytes | rc | cmp |
| --- | --- | --- | --- | --- |
| `081-nil-leftover.rec` | error | 71 | 1 | 0 |
| `081-schema-present.rec` | object | 56 | 0 | 0 |
| `081-nil-json.rec` | omitted | 53 | 0 | 0 |
| `081-mismatch.rec` | error | 75 | 1 | 0 |
| `081-typed-null.rec` | typed-null | 53 | 0 | 0 |
| `081-typed-null-present.rec` | typed-null | 57 | 0 | 0 |
| `081-present-omitted.rec` | omitted | 57 | 0 | 0 |
| `081-empty-object.rec` | empty-object | 63 | 0 | 0 |
| `081-schema-spaces.rec` | object | 56 | 0 | 0 |
| `081-schema-comma-spaces.rec` | object | 56 | 0 | 0 |

Same replica also matched missing-required, values-ignored nested array, `{}` vs schema `id`, `{}` vs schema `{}`, JSON `null` vs `id`, omit vs `id`, extra spaces in the schema list (`stdout_eq=True` on all seven).

Python one-liner (`omit-tokens → omitted`; `json.loads`; `None → typed-null`; empty implied + keys → error else empty-object; else extra keys) classifies all ten fixtures as the CLI `decode` column (`match True`).

Nearest ordinary workflow, host-executed:

```bash
echo '{"id": "foo"}' | jq -c 'keys - []'      # leftover vs empty object
echo '{"id": "foo"}' | jq -c 'keys - ["id"]'  # present schema
echo '{"arn": "foo"}' | jq -c 'keys - ["id"]' # mismatch
echo '{}' | jq -c 'keys - []'
python3 -c 'import json; print(json.loads("null"), type(json.loads("null")))'
```

```text
["id"]
[]
["arn"]
[]
None <class 'NoneType'>
```

`jq extra nonempty` == CLI `decode	error` / `error_class	unsupported-attribute`. `jq extra []` on leftover-vs-`id` == `decode	object`. `jq keys []` on `{}` == empty-object success. `json.loads("null") is None` == typed-null. The harvest delta (leftover-vs-nil is the same class as arn-vs-id) reconstructs from `keys - allow` with `allow=[]` vs `allow=["id"]`. The jump’s typed-null / empty-object labels reconstruct from `loads` returning `None` vs `{}`. Concatenating the reports does not discover a decode. It reprints `json.loads` result-kind plus extra keys.

The 14:56 jump did not add a decode. It named more of what `json.loads` already returns. Constitution: a THIN_WRAPPER does not gain exotic features to escape classification. Worker rule: do not send THIN_WRAPPER back to R1 with “make this more novel.” `MUTATE.md` already recorded that leftover.

### 2. Empty JSON object vs nil schema: `not keys`, and `{}` vs present schema is still object

Host-executed `schema	nil` + `identity_json	{}`:

```text
schema	nil
json	empty-object
decode	empty-object
error_class	-
rc=0
```

Same `{}` against `-` / `none` / `empty` (nil aliases): identical empty-object body, schema column `nil`. `{ }` with a space: same. Nested `{"id": {}}` vs nil: nonempty keys → leftover error, rc=1.

`empty_implied = fields is None or fields == []` unifies nil with schema `{}` / `empty-object` for this branch. After the jump, `{}` vs schema `{}` is empty-object (schema column `present`), not object. Leftover `{"id":"foo"}` vs schema `{}` / `empty-object` is error with `schema	present`.

`{}` vs a **present field list** is not empty-object decode:

| schema | JSON `{}` | json column | decode | rc |
| --- | --- | --- | --- | --- |
| `nil` / `-` / `none` / `empty` | `{}` | empty-object | empty-object | 0 |
| `{}` / `empty-object` | `{}` | empty-object | empty-object | 0 |
| `id` | `{}` | empty-object | **object** | 0 |
| `id arn` | `{}` | empty-object | **object** | 0 |

`json.loads('{}')` is falsy and has `keys []`. Against schema `id` there are no extra keys, so decode is object. Missing required `id` is success. `MUTATE.md` documents this and refuses to fake a cty required-attribute error. That is honest. It is also the wrapper’s ceiling: extra keys only.

### 3. Typed-null vs omitted: two tokens of `json.loads`, not a type

After the jump, omit tokens (`-` / `nil` / `none` / missing field) are `decode	omitted` for **both** nil and present schema. JSON `null` is `decode	typed-null` for both. Tests lock that split (`081-present-omitted.rec` vs `081-typed-null-present.rec`). Replica match.

Host-executed:

```text
schema	id
identity_json	-
```

```text
schema	present
json	omitted
decode	omitted
error_class	-
rc=0
```

```text
schema	id
identity_json	null
```

```text
schema	present
json	null
decode	typed-null
error_class	-
rc=0
```

Same pair vs schema `nil`: omitted vs typed-null, schema column `nil`. `schema {}` / `empty-object` + `-` → omitted; + `null` → typed-null.

That distinction is `raw in {None, "", "-", "none", "nil"}` vs `json.loads(raw) is None`. It is not Unmarshal of `null` against `schema.Identity.ImpliedType()`. The schema token never enters the typed-null branch except as a sticker on the `schema` column.

Still not typed-null:

| `identity_json` | schema | result |
| --- | --- | --- |
| `NULL` | nil | `Expecting value`, rc=1, no TSV |
| `"null"` (JSON string) | nil | `must be a JSON object`, rc=1 |
| `{"id": null}` | `id` | `decode	object`, rc=0 |
| `{"id": null}` | nil | leftover `unsupported-attribute`, rc=1 |
| `""` (JSON empty string) | nil | not-object, rc=1 |
| `true` / `0` / `[]` | nil | not-object, rc=1 |

`{"id": null}` with schema `id` is object because values are not read. A real identity decode of a null attribute is not this class.

`raw in OMITTED_JSON` includes `""`, but parse never produces `""`: `line.strip()` eats a trailing tab, so `identity_json<TAB>` → `expected key<TAB>value`, rc=1. Empty identity JSON cannot be written as a value. Missing field (`raw is None`) is the omit path.

### 4. Extra spaces in the schema list: `split()`, now tested

`schema_fields` is `replace(",", " ").split()`. Jump fixtures `081-schema-spaces.rec` (`id  arn`) and `081-schema-comma-spaces.rec` (`id, arn`) with matching JSON: `decode	object`, rc=0. Host-executed further:

| schema token | JSON | result |
| --- | --- | --- |
| `  id  ` | `{"id":"foo"}` | object, rc=0 |
| `id  arn` | `{"id":"foo"}` (arn absent) | **object**, rc=0 |
| `id,` trailing comma | `{"id":"foo"}` | object, rc=0 |
| `id  ,  arn` | `{"id":"foo"}` | object, rc=0 |
| `NIL` / `Nil` / `null` | leftover `id` | schema **present**, field name `NIL`/`null`; extra → error, rc=1 |
| pretty-printed JSON (newline in value) |  | `expected key<TAB>value`, rc=1 |

Extra spaces are not a schema parser. They are `str.split`. The jump locked the happy path. Missing `arn` under `id  arn` is still object. `NIL` is not `nil`. `schema null` is a field named `null`, not typed-null.

### 5. Stdin

Owned leftover body on the pipe:

```text
python3 "$CLI" -          # body on stdin
identjson: [Errno 2] No such file or directory: '-'
rc=1

python3 "$CLI"            # same body, no argv
usage: identjson [-h] record
rc=2

python3 "$CLI" /dev/stdin
schema	nil
json	present
decode	error
error_class	unsupported-attribute
rc=1

python3 "$CLI" <(printf 'schema\tnil\nidentity_json\t{"id": "foo"}\n')
# same leftover TSV, rc=1
```

`-` is not stdin. Argv-less invocation ignores the pipe. `/dev/stdin` and process substitution work because `Path.read_text` opens that node. Tests never pass `-`. Fine as a file tool; hostile as a pipe component. The jump did not touch argv.

### 6. Key subset, not identity decode: missing required and values ignored

`schema	id arn` + `{"id": "foo"}` (arn absent): `decode	object`, rc=0. Replica match. The harvest mismatch is extra `arn` vs schema `id`, which this catches; missing required is success. `MUTATE.md` says do not fake that error. Agreed — then the primitive is extra keys, not decode.

Values never inspected. All of these are `decode	object`, rc=0, against schema `id`:

```text
{"id": 1}
{"id": {"n": true}}
{"id": []}
{"id": false}
{"id": [1,2,{"x":true}]}
{"id": null}
```

`{"ID":"foo"}` vs schema `id`: extra, error, rc=1. Non-object JSON other than `null` (`true` / `""` / `[]`): parse error, rc=1, no decode class. Origin `decode_identity_failing.go`: `expected key<TAB>value`, rc=1. The origin packet cannot enter. The owned fixtures are already the harvest sentence, typed as TSV.

### 7. Parse / IO / last-wins / huge

Missing schema / empty file / comments-only / `/dev/null`: `missing schema`, rc=1. Unknown field / `Schema` capitalized / spaces instead of tabs / BOM: unknown-field or expected-tab, rc=1. Directory: `Is a directory`. Missing path: `No such file`. Last-wins: `schema nil` then `schema id` + leftover id JSON → object, rc=0; reverse → leftover error, rc=1. 10000 keys vs nil: `decode	error`, rc=1, stdout 71 bytes. `error_class` never names the attribute, unlike the specimen’s `unsupported attribute "arn"`.

---

## Primitive

Reality-stripped operation: parse a TSV of `schema TOKEN` plus optional `identity_json VALUE`; TOKEN in `{nil,-,none,empty}` means nil allowlist, TOKEN in `{{},empty-object}` means `[]`, else split on comma/whitespace; if VALUE is in `{None,-,none,nil}` print omitted; else `json.loads` and if `None` print typed-null, if empty keys and empty allowlist print empty-object, if extra keys print unsupported-attribute rc=1, else object; rc=1 also on parse/IO.

Nearest ordinary workflow: `jq 'keys - $allow'` or `python3 -c '… json.loads …'` on the same JSON the caller already typed, or printing IdentityJSON and `Identity: nil` and comparing by eye. Observable capability lost if identjson vanishes: **none**. The harvest records already are the input. The decode-class join is still a hand comparison after `json.loads`. Extra keys plus `loads` result-kind are the product.

That is why this is KILL, not MUTATE. The *question* (leftover IdentityJSON against a nil identity schema: object, typed-null, omitted, empty-object, or the same unsupported-attribute class as a schema mismatch) is a real debugging object. This embodiment does not ask it of a schema pointer and a JSON buffer. It asks `json.loads` + key subset on caller-labeled tokens. The 14:56 jump named JSON `null` and empty keys. That is still `loads`. Ingesting terraform state + provider schema and running Decode would be implementing the terraform theater the harvest rejected, and would be a new harvest, not a patch of this 144-line loads. Constitution: a THIN_WRAPPER does not gain exotic features to escape classification. Worker rule: do not send THIN_WRAPPER back to R1 with “make this more novel.” `MUTATE.md` leftover instruction: if still `json.loads` + `keys - fields`, KILL.

Hardcoded ceiling:

- decode error iff extra keys (nil/`{}` schema ⇒ every key is extra); missing required is object
- values never read; `{"id": null}` / nested / wrong type are object
- empty JSON vs nil/`{}` schema is `empty-object`; vs present field list is `object` with `json	empty-object`
- typed-null is `json.loads is None`; omitted is a five-token set; they do not use the schema type
- `NULL` / `"null"` / empty JSON string are not typed-null
- empty identity_json / schema values unparseable (`line.strip()` eats the tab)
- schema list is `replace(",", " ").split()`; extra spaces and commas succeed; `NIL` is a field name
- unary record; the harvest “same error class as mismatch” is two invocations plus a hand join
- `error_class` never names the attribute
- origin go / schema-split refuse
- `-` is not stdin; argv-less stdin is argparse rc=2
- duplicate schema/json last-wins
- 10k-key leftover vs nil still 71-byte error sticker
- rc=1 on extra keys **or** parse/IO; only the former prints a decode class
- Dreamer terraform Decode was rejected; this is that Decode, reduced to the harvest sentence as `json.loads` + key subset, then relabeled

Honor KILL. Dreamer ancestry is not protection. An exceptional jump that names more `json.loads` cases is not protection.

Do not grow a cty unmarshaler or a terraform Decode to escape THIN_WRAPPER. Do not merge this join onto `main`.

---

KILL
