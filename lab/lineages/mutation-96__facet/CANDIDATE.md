# mutation-96 — facet

## Primitive

Same-object field cover of a composite needle: whole JSON field values of **one object**, not greedy substrings that happen to appear across records.

## Why this might not exist

Beck names the earliest pipeline stage whose output already contains a needle, then covers leftover bytes with longest earlier fragments. That is the right object for unpiped stderr and for `sed` prefixes. It is the wrong object for `kizu@0.7.0` against `cargo metadata`:

1. **Byte-cover is not field-cover.** Greedy longest-match at needle byte 4 absorbs `@0.7.0` from `notify-debouncer-full@0.7.0` in another package's `.id`. The `@` jq minted is not glue; it is stolen from an unrelated crate.
2. **`grep -o` / `jq` source** are the workarounds, and they answer different questions. Grep names the first substring. Reading `.name + "@" + .version` is inverse-printf of the transform (forbidden here). The missing verb is: *which JSON object jointly owns these pieces?*
3. Nested `.targets[].name == "kizu"` is a different object. A sibling cover has to refuse it.

Not leftover-name. Not inverse-printf. Not a wait-source. The object changed: **same `{...}`**, not first producer of a byte.

## How to run

```bash
chmod +x ./facet ./demo.sh
./facet --selftest
./demo.sh
./demo.sh 0
./facet --help
printf '%s' '{"packages":[{"name":"kizu","version":"0.7.0","id":"path+kizu#0.7.0"},{"name":"notify-debouncer-full","version":"0.7.0","id":"reg#notify-debouncer-full@0.7.0"}]}' | ./facet -n 'kizu@0.7.0'
cargo metadata --format-version 1 --offline --manifest-path /Users/annenpolka/ghq/github.com/annenpolka/kizu/Cargo.toml | ./facet -n 'kizu@0.7.0'
./facet --quiet --cwd /Users/annenpolka/ghq/github.com/annenpolka/kizu -n 'kizu@0.7.0' \
  --sh 'cargo metadata --format-version 1 --offline | jq -r ".packages[] | select(.name==\"kizu\") | .name + \"@\" + .version"'
```

Python 3.10+, stdlib, `bash`. Exit 0 found, 1 none, 2 usage.

## Empirical transcript

### v0.1 — same-object siblings vs greedy coincidence

`--selftest` 12/12. Tiny fixture is the clean witness: two packages, needle `kizu@0.7.0`.

```
FACET  siblings  $.packages[0]  name=kizu
       pieces    .name 'kizu'  +  glue '@'  +  .version '0.7.0'
       greedy    COINCIDENCE
                 'kizu'    $.packages[0].name
                 '@0.7.0'  $.packages[1].id  name=notify-debouncer-full
```

kizu cargo metadata (1.3MB, 290 packages, 2026-08-20):

```
FACET  siblings  $.packages[103]  name=kizu
       cover     9/10  fields 2  keys name,version
       field     .name     'kizu'    byte 367060
       glue      '@'
       field     .version  '0.7.0'   byte 367077
       greedy    COINCIDENCE
                 'kizu'    $.packages[103].name
                 '@0.7.0'  $.packages[128].id  name=notify-debouncer-full  byte 448982
```

Pipeline `cargo metadata | jq '.name + "@" + .version'`: wrap stage 1 jq, JSON stage 0 cargo, same sibling cover, same coincidence. Facet does not read the jq program.

`notify-debouncer-full@0.7.0` binds that package's `.name`+`.version` (not kizu). Greedy *agreed* here in v0.1 because the whole needle already lives inside the same object's `.id` — a derived echo, not a sibling cover. Version-only `0.7.0` is `field` on kizu (first `.version`), silent about notify-debouncer-full and ratatui-macros (also `0.7.0`).

Nested `{"name":"kizu","inner":{"version":"0.7.0"}}` is not siblings. Split `[{"name":"kizu"},{"version":"0.7.0"}]` is not siblings; greedy still coincides.

### v0.2 — also-occupancy + echo vs siblings

From that run: a single-field needle is occupancy of a field value, not a first hit. A same-object greedy match via a superstring `.id` is **echo**, not identity.

After:

Version-only `0.7.0` against kizu cargo metadata:

```
FACET  field  $.packages[103]  name=kizu
       keys   version
       also   3 objects share this field
              $.packages[128]  name=notify-debouncer-full  .version
              $.packages[171]  name=ratatui-macros  .version
       note   pass a composite needle to bind one object
```

`kizu@0.7.0` stays unambiguous siblings (also empty). Composite needle is what turns occupancy into identity.

`notify-debouncer-full@0.7.0`:

```
FACET  siblings  $.packages[128]  name=notify-debouncer-full
       pieces    .name + glue @ + .version
       greedy    ECHO  (same object, derived superstring field)
                 from  'notify-debouncer-full@0.7.0'  .id
       note      derived field contains the spelling; identity is sibling fields
```

v0.1 called this "same object (byte-cover already agreed)" and hid that greedy ate `.id`, not `.name`+`.version`. `--selftest` 14/14. `./demo.sh 0` **36 passed, 0 failed**.

## Dogfood targets

- `./facet --selftest` (14): offsets, fixture coincidence, nested, split array, NDJSON, escaped strings, printf|jq, also-occupancy, echo vs siblings.
- `./demo.sh` 36: fixture, skeptic greedy, nested, split, jq wrap, kizu cargo, kizu pipeline, notify-debouncer-full echo, version-only also.
- `/Users/annenpolka/ghq/github.com/annenpolka/kizu` — `cargo metadata --format-version 1 --offline | jq`.

## Surprises

- Cargo metadata never contains the exact spelling `kizu@0.7.0` (path package id is `path+file://…#0.7.0`). It *does* contain `notify-debouncer-full@0.7.0` as a substring of `.id`. That is why greedy is coincidence for kizu and echo (derived `.id`) for notify-debouncer-full.
- `kizu` also lives on `.targets[].name`. Those objects have no sibling `.version` `0.7.0`. Scoring sibling covers above single-field covers is what keeps the package, not the target.
- Three packages share `.version == 0.7.0`: kizu, notify-debouncer-full, ratatui-macros. Composite needle disambiguates; the version-only needle is occupancy (v0.2 lists them).
- Greedy "same object" on `notify-debouncer-full@0.7.0` was a lie of omission: one find() of the whole needle inside `.id`. Echo vs siblings is the real split.

## Failures

- Occupancy still names a winner (first object by byte offset) and lists `also`. It does not refuse to pick.
- Pretty-printed JSON works; JSON with comments does not.
- Array-of-scalars (keywords) are not direct fields of the parent object, by design.
- Inner `$()` pipelines are one outer stage (same as beck). `--sh` buffers each stage.
- Inverse-printf of the jq source would have named `.name` and `.version` without looking at cargo. That is a different, forbidden object.

## Suggested mutations

- **identity keys** (`name`,`version`,`id`) as a default ranking when two sibling covers tie.
- YAML/TOML field-cover of the same composite needle.
- Byte-span of a sibling field through a wrap (map `.version`'s JSON offset onto the constructed needle).

## Kill / keep

**Keep.** The hole in beck is empirical: `kizu@0.7.0` against real cargo metadata pairs with `notify-debouncer-full@0.7.0` under byte-cover and with kizu's own `.name`+`.version` under field-cover. `tee | grep` and inverse-printf of jq both miss that distinction.
