# freshmiss

Given two builds, say whether freshness used an identity that omitted a
requested extra output.

A cache hit looks like success. `ls` of the extra path only shows the file is
gone. This query joins status, identity, requested outputs, and present
outputs, and names **FRESH-but-missing** as an identity miss.

## Usage

```
freshmiss FIRST SECOND [--dir DIR] [--first-dir DIR]
```

Each argument is a build record (tab-separated fields):

```
status	BUILT
identity	9280cc7e16e9
requested	out.bin
present	out.bin
```

| field | meaning |
| --- | --- |
| `status` | `BUILT` or `FRESH` (other strings pass through; only `FRESH` is a hit) |
| `identity` | freshness key the cache used |
| `requested` | output paths this build asked for (repeatable) |
| `present` | output paths that exist after the build (repeatable) |
| `dir` | if set, `present` is which `requested` paths exist in that directory |

`--dir` observes the second build's present files from `DIR` (the `ls` after a
hit). It overrides a `dir` field on that record. Declared `present` is ignored
when a directory is used.

## Output

```
verdict	FRESH-but-missing
identity	9280cc7e16e9
same_identity	true
first_status	BUILT
second_status	FRESH
requested_extra	out.sbom
missing	out.sbom
omitted_from_identity	out.sbom
```

| row | meaning |
| --- | --- |
| `verdict` | `FRESH-but-missing`, `FRESH-complete`, `rebuilt`, or `identity-changed` |
| `requested_extra` | requested on the second build but not the first |
| `missing` | requested on the second build and not present |
| `omitted_from_identity` | `missing` when verdict is `FRESH-but-missing`; else `none` |

`omitted_from_identity` is an inference from same key + FRESH + absent
requested extra. The tool does not dump fingerprint bytes.

## Examples

Specimen-011: first writes `out.bin` under an input-hash identity; second asks
for `out.sbom` too; cache reports FRESH; extra file absent.

```
freshmiss first.rec second.rec
# verdict	FRESH-but-missing
# omitted_from_identity	out.sbom
```

Same identity, FRESH, extra actually present:

```
# second present includes out.sbom
# verdict	FRESH-complete
# omitted_from_identity	none
```

Same identity, second `BUILT`, extra still absent — a write miss, not this
identity miss:

```
# verdict	rebuilt
# missing	out.sbom
# omitted_from_identity	none
```

## Boundary

Does not reconstruct cargo fingerprints, run a build engine, or guess extra
output names that were not requested in the records.
