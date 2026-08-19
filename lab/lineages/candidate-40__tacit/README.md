# tacit

Call-site relation to a default.

Two calls that both result in `0.45` are not the same object: one **omitted** the argument (it will move when the default moves) and one **restated** `0.45` (it will not follow).

```
TACIT     omitted; inherits the current default
SHADOW    passed a literal equal to the default
OVERRIDE  passed a literal different from the default
BOUND     passed a non-literal (name, expression, collection)
```

A default change is a blast radius:

```
BLAST   TACIT on a slot whose default moved (or was born)
FOSSIL  still passes the old default
PRE     already restates the new default
LOCK    passes some other literal
```

Not leftover-name search. Not inverse-printf. Not a lockset. The object is **omission**.

## Run

Python 3.10+, stdlib, `git` for `--git`. No install.

```bash
chmod +x ./tacit
./tacit --selftest
./demo.sh
./tacit --help
```

## Examples

### 1. Who rides `presentThreshold`?

```bash
./tacit -C ~/ghq/github.com/annenpolka/sitbone presentThreshold
```

sitbone: **27 TACIT, 0 SHADOW**. Production `SitboneCore.swift:68` and every hysteresis test omit the threshold they document. Changing the default moves them all.

### 2. Who restates a default (will not follow)?

```bash
./tacit -C ~/ghq/github.com/annenpolka/sitbone --only shadow SessionProfile colorHue
```

`SessionProfile.makeDefault()` passes `colorHue: 0.45`, which **equals** the slot default. If mint stops being `0.45`, `makeDefault` stays put.

### 3. Blast of a default-changing commit

```bash
./tacit -C ~/ghq/github.com/annenpolka/sitbone --git e9b0f75^ e9b0f75 --check
```

`threshold = 0.4` renamed and moved to `presentThreshold = 0.45` (and `absentThreshold = 0.35` was born). **54 BLAST** rows: every caller rides the new defaults. Exit 1.

```bash
./tacit -C repo --git HEAD^ HEAD --summary
./tacit -C repo --summary PresenceArbiter
./tacit -C repo --all --header     # include OVERRIDE + BOUND
git diff main | true               # stdin is not the object; --git is
```

TSV on stdout. `--json` / `--summary` / `--check` (exit 1 if TACIT or BLAST).

Languages: Swift labeled inits, Python def/dataclass, TypeScript `function`, Rust clap `default_value`.
