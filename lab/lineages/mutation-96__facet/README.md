# facet

Bind a composite needle to **sibling JSON fields of one object**.

Beck (byte-cover) will pair `kizu@0.7.0` with `kizu` from kizu's `.name` and `@0.7.0` from `notify-debouncer-full@0.7.0` in another package's `.id`. That is substring coincidence across records. Facet covers the needle with *whole field values*, and those fields must belong to the **same JSON object**.

Not inverse-printf of `jq '.name + "@" + .version'` — the jq program is not read. Not leftover-name. Not a wait-source.

```
{"name":"kizu","version":"0.7.0"}     ←  .name + glue @ + .version
{"id":"…notify-debouncer-full@0.7.0"} ←  greedy byte-cover stops here
         ▲
         same-object field cover, not this foreign substring
```

## Install / run

Python 3.10+, stdlib, `bash`. `jq` / `cargo` only for examples. v0.2.

```bash
chmod +x ./facet ./demo.sh
./facet --selftest
./demo.sh
./facet --help
```

Exit 0 found, 1 no field cover, 2 usage.

```bash
cargo metadata --format-version 1 --offline | ./facet -n 'kizu@0.7.0'
./facet -n 'kizu@0.7.0' --doc meta.json
./facet -n 'kizu@0.7.0' --sh 'cargo metadata --offline --format-version 1 | jq -r "…"'
./facet --json -n NEEDLE --doc FILE
```

## Examples

### 1. Same-object siblings, greedy coincidence

Two packages. The composite identity of the first; the second's `id` contains `@0.7.0`.

```bash
printf '%s' '{"packages":[{"name":"kizu","version":"0.7.0","id":"path+kizu#0.7.0"},{"name":"notify-debouncer-full","version":"0.7.0","id":"reg#notify-debouncer-full@0.7.0"}]}' \
  | ./facet -n 'kizu@0.7.0'
```

```
FACET  siblings  $.packages[0]  name=kizu
       pieces    .name 'kizu'  +  glue '@'  +  .version '0.7.0'
       greedy    COINCIDENCE
                 'kizu'     $.packages[0].name
                 '@0.7.0'   $.packages[1].id  name=notify-debouncer-full
```

`grep` / greedy longest-match is already the wrong object.

### 2. Real cargo metadata (kizu)

```bash
cargo metadata --format-version 1 --offline --manifest-path ~/ghq/github.com/annenpolka/kizu/Cargo.toml \
  | ./facet -n 'kizu@0.7.0'
```

`$.packages[103]` is kizu. Greedy still takes `@0.7.0` from `$.packages[128].id` (notify-debouncer-full). Nested `.targets[].name` is a different object and does not steal the cover.

### 3. Pipeline wrap: jq assembles the spelling, cargo held the fields

```bash
./facet --quiet -n 'kizu@0.7.0' --cwd ~/ghq/github.com/annenpolka/kizu \
  --sh 'cargo metadata --format-version 1 --offline | jq -r ".packages[] | select(.name==\"kizu\") | .name + \"@\" + .version"'
```

`wrap stage 1 jq` is the first exact spelling. Substance is `.name` + `.version` of the same cargo package, not the foreign pkgid substring.

`--json` / `--tsv` compose. `--keys name,version` restricts the cover. `--line 1` takes the final stdout line as the needle.

A single-field needle (`0.7.0`) is occupancy: every object that holds that field is listed as `also`. A derived `.id` that *contains* `name@version` is `ECHO`, not the sibling identity.
