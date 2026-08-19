# preen

Call-site relation to a default. Unfold reads the **constructed** nested default, not the type's init signature. Clap TACIT is an **invocation that omitted `--flag`**, not a command-shaped line.

Two calls that both result in `0.45` are not the same object: one **omitted** the argument (it will move when the default moves) and one **restated** `0.45` (it will not follow). Nested `Thresholds = Thresholds(driftDelay: 20)` inhabits **20**, not the type default **15**.

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

Not leftover-name search. Not a lockset. The object is **omission of a constructed world**.

## Run

Python 3.10+, stdlib, `git` for `--git`. No install.

```bash
chmod +x ./preen
./preen --selftest
./demo.sh
./preen --help
```

## Examples

### 1. Who rides `presentThreshold`?

```bash
./preen -C ~/ghq/github.com/annenpolka/sitbone presentThreshold
```

sitbone: **27 TACIT, 0 SHADOW**. Production and every hysteresis test omit the threshold they document.

### 2. Constructed nested default ≠ type signature

```bash
./preen -C ./fixtures --all PinProfile driftDelay
./preen -C ./fixtures --all SessionProfile driftDelay
```

`PinProfile(..., thresholds: Thresholds = Thresholds(driftDelay: 20))` omitted is **OVERRIDE 20**. `SessionProfile(..., thresholds: Thresholds = Thresholds())` omitted is **TACIT 15**. Passing `Thresholds(driftDelay: 15)` is nested **SHADOW** of `SessionProfile.thresholds.driftDelay`.

### 3. Clap `--agent` on an invoked command

```bash
./preen -C ~/ghq/github.com/annenpolka/kizu --all --summary agent
```

`--agent claude-code` in an installed hook string is SHADOW. `{agent_arg}` is BOUND. `cline` / `cursor` are OVERRIDE. kizu **TACIT=0**: a comment or `.contains("kizu hook-post-tool")` is not an omitted flag.

```bash
./preen -C repo --git HEAD^ HEAD --summary
./preen -C repo --summary PresenceArbiter
./preen -C repo --all --header
```

TSV on stdout. `--json` / `--summary` / `--check` (exit 1 if TACIT or BLAST).

Languages: Swift labeled inits (constructed unfold, `.init()`), Python def/dataclass, TypeScript `function`, Rust clap `default_value` (invocations, `long =`).
