# MUTATE identjson (applied 2026-09-02 14:56 JST)

Exceptional jump after harvest: leftover IdentityJSON vs nil schema
without terraform cty.

```yaml
origin:
  method: hdd
  trial: hdd-tfident
  specimens: [specimen-081]
  mutation: typed-null vs omitted; EmptyObject unmarshal of {}; schema list with spaces
  parent: candidate-identjson
archive: lab-runs/specimen-hdd-20260902-1112/lineages/candidate-identjson/
cli_sha256_before: 357b9f2df62faca8cccbd0f4fcb376a027606f32230bc2390b4364648cc17c6b
cli_bytes_before: 3900
cli_sha256_after: 9bac058a6ada10a173f13b9e96393555d13bf135c1a8e866dc1b787821c01255
cli_bytes_after: 4536
```

Not merged to `main`. No terraform. No cty. No worktree (archive-only harvest).

`python3 -m unittest tests/test_identjson.py -v` twice — 10/10 OK.

`./demo.sh` ×2, `demo-1.log` / `demo-2.log` byte-identical. Wrapper exit 0.

## What was kept

The object: name the decode class of leftover identity JSON against a nil
or present identity schema.

Owned 081-nil-leftover (`IdentityJSON {"id":"foo"}` vs `Identity: nil`)
stays `decode error` / `error_class unsupported-attribute` / rc=1.

Kept classes:

| case | decode | error_class | rc |
| --- | --- | --- | --- |
| leftover JSON vs nil schema | error | unsupported-attribute | 1 |
| matching JSON vs present schema | object | - | 0 |
| omitted JSON | omitted | - | 0 |
| mismatch `arn` vs `id` | error | unsupported-attribute | 1 |

## Jump (honest packet joins)

The packet lists four answers Decode could have produced: present object,
typed null, omitted/zero value, or the same unsupported-attribute class as
a schema mismatch. Harvest only named object / omitted / error. These
three joins were already in the Decode snippets, not in the CLI.

1. **typed-null vs omitted.** Decode takes the identity branch only when
   `IdentityJSON != nil`. Nil/empty/`-`/`none`/`nil` skips (zero value →
   `omitted`) for **both** nil and present schema. JSON `null` is bytes
   present: Unmarshal of `null` against ImpliedType is typed null.
   Before: omitted JSON + present schema was labeled `typed-null`; JSON
   `null` was a parse error. After: they split.

2. **empty JSON object `{}` vs nil schema.** `specType` on a nil
   `*configschema.Object` returns `cty.EmptyObject`. Unmarshal of `{}`
   into EmptyObject succeeds (empty object, not omitted, not typed-null,
   not unsupported-attribute). Unmarshal of `{"id":"foo"}` into
   EmptyObject stays the owned error.

3. **schema list with spaces.** Identity schema is a NestingSingle object
   of named attributes. `schema	id  arn` and `schema	id, arn` are the
   same field list. Matching JSON is `object`. Treating `id  arn` as one
   token would have been `unsupported-attribute`.

## Before → after

Present schema + omitted JSON (`081-present-omitted.rec`):

```
# before
decode	typed-null
# after
json	omitted
decode	omitted
rc=0
```

JSON `null` (`081-typed-null.rec` / `081-typed-null-present.rec`):

```
# before
identjson: identity_json must be a JSON object   # rc=1
# after
json	null
decode	typed-null
rc=0
```

`{}` vs nil schema (`081-empty-object.rec`):

```
schema	nil
json	empty-object
decode	empty-object
rc=0
```

Spaced / comma-spaced identity attrs (`081-schema-spaces.rec`,
`081-schema-comma-spaces.rec`): `decode object`, rc=0.

Owned leftover unchanged:

```
schema	nil
json	present
decode	error
error_class	unsupported-attribute
rc=1
```

## Leftover (THIN_WRAPPER — not faked)

Cannot beat `json.loads` plus extra-key subset without cty. This cut names
the packet's null / omitted / EmptyObject-of-`{}` / spaced-attr joins. It
does not become terraform Decode.

Documented, not hidden:

- **Missing required attrs are still object.** `{}` vs present schema
  `id` has no extra keys, so decode stays `object`. Real
  `ctyjson.Unmarshal` against a required identity object would fail.
  Do not fake that error.
- Attribute **types** are not checked (`{"id": 1}` vs string `id` is
  still `object`). Nested identity objects, NestingList, schema version,
  Encode, and `decodeIdentityCache` are out.
- JSON duplicate keys last-wins via `json.loads`. Non-object JSON other
  than `null` is still a parse error, not a decode class.
- This CLI **names** the failing leftover class. It does not apply PR
  37709 (skip leftover when `schema.Identity == nil`). Owned
  081-nil-leftover remains error.

If a later mutation still is only `json.loads` + `keys - fields` and
calls that cty, KILL as THIN_WRAPPER.

## Isolation

No terraform checkout. No `go-cty`. No merge onto `main`.
