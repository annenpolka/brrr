# DESTROYER sumident

Date: 2026-09-02 15:12 JST
RUN_ID: specimen-hdd-20260902-1112
Target: `lineages/candidate-sumident/sumident`

sha256 `8611ecabb243c40f17c826facbdf602ee76b42d229d9dd1fb8b790dabbe066b6` (3204 bytes).
Parent `main` coordinator-only; not merged. `go` not invoked.

Origin (`CANDIDATE.md` / harvest `hdd-sumzip` / specimen-083): name which identity
a go.sum contained for a module version — zip content sum, go.mod-only, both,
or neither. grep of the module path hits both line types. Kind: USEFUL_COMPOSITION.
Rejected: invented gosum-analyze.

Tests 7/7. `demo.sh` twice identical. Happy path is real. That is not enough.

This candidate is a **THIN_WRAPPER** of `/go.mod` suffix vs unsuffixed version
token: `mod = version.endswith("/go.mod")` then strip; else `zip`. Identity is
the set of those two bits. `h1:` / `h2:` hashes are ignored. Host replica of
`inspect` matches the CLI on owned download/tidy/zip-only/missing.
`grep '^MODULE VERSION '` vs `grep '^MODULE VERSION/go.mod'` is the load-bearing
bit. Decision: **KILL**.

```text
CLI=.../lineages/candidate-sumident/sumident
FIX=.../lineages/candidate-sumident/fixtures
```

No go toolchain. Do not grow a sumdb client to escape THIN_WRAPPER. Do not send
go theater back to R1. Distinct from golang/go#80745 (Lookup extra hashes).

## What still works

Owned 083 download: `mod yes` / `zip no` / `identity mod-only` / rc=1.

Tidy: `both` / rc=0. Unseen sampler download: mod-only. Zip-only fixture: zip-only
rc=1. Missing module: neither rc=1. Missing path rc=1. Stdin tidy: both rc=0.

```bash
python3 "$CLI" "$FIX/go.sum.download" --module rsc.io/quote --version v1.5.2; echo rc=$?
```

```text
module	rsc.io/quote
version	v1.5.2
mod	yes
zip	no
identity	mod-only
rc=1
```

## Implementation

```python
if ver.endswith("/go.mod"):
    kind = "mod"; ver = ver[:-len("/go.mod")]
else:
    kind = "zip"
# identity from {mod, zip} bits; hashes unused
```

### 1. THIN_WRAPPER of two anchored greps

Host:

```bash
grep '^rsc.io/quote v1.5.2 ' "$FIX/go.sum.download"   # empty (zip absent)
grep '^rsc.io/quote v1.5.2/go.mod' "$FIX/go.sum.download"  # hits
grep '^rsc.io/quote v1.5.2 ' "$FIX/go.sum.tidy"        # zip line
```

The CLI's `mod-only` is exactly (mod grep hits) and (zip-space grep misses).
`both` is both hit. `neither` is both miss. `zip-only` is zip-space hit and
mod miss. `--module` / `--version` are the grep prefixes.

Hash bytes (`h1:fixture-quote-zip=` vs `h1:AAA`) do not vote. `h2:` still zip.

`--module rsc.io --version quote`: neither (prefix is not a parse of the line).

`--version v1.5.2/go.mod`: neither — the suffix is consumed at parse, not at query.

Tab-separated `module<TAB>version<TAB>h1:` still splits as zip (str.split).

### 2. Not a checksum database

Unknown short line: `sumident: …` rc=1. There is no GOSUMDB Lookup, no zip
open, no `go mod download`. `demo.sh` already says grep hits both; the fixtures
already contain `/go.mod` vs unsuffixed as the classification.

### 3. rc is not-both

rc=1 for mod-only, zip-only, neither. The harvest (download omitted zip) is
the same bit as missing module. `test` of two greps already has that.

## Primitive

Parse space-separated go.sum rows; a version token ending `/go.mod` is mod,
else zip; print the set for `--module` `--version`. rc=0 iff both kinds present.

Nearest: two greps. Observable capability lost if sumident vanishes: **none**.
The harvest question (which identity go.sum contained) is real. This embodiment
asks it of lines that already are that classification.

Honor KILL. Dreamer ancestry is not protection. First HARVEST_NOW is not
protection. Do not send THIN_WRAPPER back to R1. Do not merge onto `main`.

---

KILL
