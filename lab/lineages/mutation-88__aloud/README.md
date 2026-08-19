# aloud

BLAST survivors that were then spoken.

tacit classifies a call as TACIT (omitted) or SHADOW (literal equal to the
default). A default-moving diff is a BLAST of tacit riders plus FOSSIL
restatements of the *old* literal.

That two-point picture cannot tell:

- a site that **stayed omitted** after the blast
- a BLAST survivor that later **said the new default** (FOSSIL of 0.45, not 0.4)
- a site that already wrote 0.45 *at* the blast (PRE)
- a site born later already speaking 0.45 (LATE — never a survivor)

Those four later look like "the world is 0.45". Only one of them rode the
blast silently and then pinned it. That one is **ALOUD**.

```
MUTE    TACIT at BLAST, still TACIT later
ALOUD   TACIT at BLAST, later SHADOW of the *new* default
FOSSIL  restates the *old* default
PRE     already restated the new default at the BLAST
LATE    not a survivor; later already SHADOW of the new default
```

Not leftover-name search. Not a lockset. Not a clock-cut. Not inverse-printf.
The object is **omitted-then-spoken**.

## Run

Python 3.10+, stdlib, `git`. No install.

```bash
chmod +x ./aloud
./aloud --selftest
./demo.sh
./aloud --help
```

## Examples

### 1. sitbone `presentThreshold` 0.4 → 0.45 (e9b0f75)

```bash
./aloud -C ~/ghq/github.com/annenpolka/sitbone --blast e9b0f75 --summary presentThreshold
```

**ALOUD 0, MUTE 27, FOSSIL 0, PRE 0.** Every hysteresis test still omits the
threshold it documents in comments. The blast is still silent. `--check`
exits 0.

`--until e9b0f75` is the control: ALOUD is impossible at the blast itself.

### 2. Who spoke the new default after riding the blast?

```bash
./aloud -C <repo> --blast HEAD~1 --until HEAD --header
```

Synthetic three-commit fixture (`./demo.sh`):

| site   | at BLAST | later                         | fate   |
| ------ | -------- | ----------------------------- | ------ |
| camera | omitted  | omitted                       | MUTE   |
| mic    | omitted  | `presentThreshold: 0.45`      | ALOUD  |
| radar  | `0.4`    | `0.4`                         | FOSSIL |
| lidar  | `0.45`   | `0.45`                        | PRE    |
| new    | (absent) | `presentThreshold: 0.45`      | LATE   |

ALOUD is not MUTE, not FOSSIL-of-old, not PRE, not LATE.

### 3. kizu `--agent claude-code` (born at 3d4b543)

```bash
./aloud -C ~/ghq/github.com/annenpolka/kizu --blast 3d4b543 --summary agent
```

**ALOUD 0, LATE 18.** Tests that restated `--agent claude-code` were *born
speaking*. They never rode a blast as tacit callers. A `rg --agent claude-code`
cannot tell LATE from ALOUD.

```bash
./aloud -C repo --blast REV --until HEAD --only aloud
./aloud -C repo --blast OLD NEW --all --summary
./aloud -C repo --blast REV --check          # exit 1 if ALOUD remains
```

TSV on stdout. `--json` / `--summary` / `--check` (exit 1 if ALOUD).

Languages: Swift labeled inits, Python def/dataclass, TypeScript `function`,
Rust clap `default_value`.
