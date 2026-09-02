# freshmiss

origin.method: specimen-hdd
origin.trial: hdd-fingerprint
specimens: [specimen-005, specimen-011]

classification: USEFUL_COMPOSITION

## Primitive

Given two builds, say whether freshness identity omitted a requested extra
output (FRESH-but-missing).

## Why this might not exist

A cache hit is reported as success. The miss is an absent extra file. Verbose
logs plus `ls` still leave the join — same identity, FRESH, requested extra
outside that identity — as a hand comparison.

## Core operation

Compare two build records (status, identity, requested outputs, present
outputs). If the second is FRESH on the same identity while a requested
output is absent, name that output as omitted from the identity.

## Observable delta

One query states FRESH-but-missing as an identity miss rather than a
successful cache hit, and names the missing requested extra (`out.sbom` on
the owned fixture).

## Reality mapping

Owned fixture `specimen-011/files/cache_build.py`: input-hash key, first
build without extra, second with `out.sbom` requested, FRESH, extra missing.
specimen-005 is the cargo SBOM origin of that fixture; cargo is not executed
here.

## Research boundary

Does not reconstruct cargo's real fingerprint. Does not invent extra output
names. Does not fix the cache.

## Removed

cargo-inspect, `-Zsbom`, fingerprint component listings, rustc version
precision.

## Smallest artifact

Python 3 stdlib CLI `freshmiss`.

## Pre-implementation Reality assessment

- Classification: USEFUL_COMPOSITION
- Nearest existing operation: verbose build logs plus `ls` of the extra path
- Observable delta: one query that states FRESH-but-missing-output as an
  identity miss rather than a successful cache hit
- Constraint: observable evidence is build status text and whether named
  output files exist
- Established on the fixture: first BUILT extra_exists False; second FRESH
  extra_exists False; same key `9280cc7e16e9`

## How to run

From this directory:

```
python3 tests/test_freshmiss.py
./demo.sh
```

## Empirical transcript

Host-executed 2026-09-02. `./demo.sh` (after dir-observation dogfood):

```
== fixture .../specimen-011/files/cache_build.py ==
first BUILT extra_exists False key 9280cc7e16e9
second FRESH extra_exists False key 9280cc7e16e9
same_key True

replay_first	BUILT	9280cc7e16e9
replay_second	FRESH	9280cc7e16e9

== ls of replay outdir (nearest existing operation) ==
out.bin
missing_check out.sbom: absent

== freshmiss first second (present observed from outdir) ==
verdict	FRESH-but-missing
identity	9280cc7e16e9
same_identity	true
first_status	BUILT
second_status	FRESH
requested_extra	out.sbom
missing	out.sbom
omitted_from_identity	out.sbom
```

`ls` shows `out.bin` and that `out.sbom` is absent. It does not say the
identity that printed FRESH omitted that extra. `freshmiss` does.

Tests: 13 OK (`python3 tests/test_freshmiss.py`).

## Dogfood targets

- specimen-011 `cache_build.py` (owned, executed). First commit trusted
  declared `present` lists. After replaying `build()` into a kept outdir,
  `present` is observed from the directory so a lying `present	out.sbom`
  cannot hide the miss.
- specimen-005 cargo SBOM story (origin only; not executed).

## Surprises

The fixture's `extra_exists` boolean never names `out.sbom`. The extra path
still has to be supplied as a requested output; the tool will not guess it.
The tempfile outdir in `main()` is gone before a later `ls`, so replay with
a kept directory is required to compose with the filesystem.

## Failures

Does not know cargo unit keys or SBOM precursor filenames. Does not treat a
rebuild that forgot to write the extra as an identity miss (`rebuilt` plus
`missing`, `omitted_from_identity	none`). Requested names are caller-supplied.

## Suggested mutations

- `--check` exit 1 on FRESH-but-missing
- Parse the fixture's `first BUILT extra_exists ...` log lines
- Multiple extras, mixed present/missing
- Identity that includes the output set (should become `rebuilt` or
  `identity-changed` when extra is newly requested)

## Kill / keep

Keep: specimen-011 pair names `out.sbom` as `omitted_from_identity` under
verdict `FRESH-but-missing`. FRESH with the extra present is
`FRESH-complete`. Missing extra after `BUILT` is not this verdict.
