# unsay

Unspeak ALOUD.

aloud *names* a BLAST survivor that later restated the new default.
unsay emits the unified diff that **deletes that argument**, so the site
rides again (ALOUD → TACIT). Optionally `--pin` writes the inherited
world at MUTE sites (MUTE → SHADOW).

```
ALOUD  omitted at BLAST, later said 0.45     — --emit deletes it
MUTE   omitted at BLAST, still omitted       — --pin inserts 0.45
PRE    already said 0.45 *at* the BLAST      — not unsaid
LATE   born later already saying 0.45        — not unsaid
FOSSIL still says 0.4                        — not unsaid
```

`rg presentThreshold: 0.45` sees ALOUD, PRE, and LATE as the same token.
The patch is the witness that only ALOUD was a survivor who spoke.

Not leftover-name search. Not a lockset. Not inverse-printf.

## Run

Python 3.10+, stdlib, `git`. No install.

```bash
chmod +x ./unsay ./demo.sh
./unsay --selftest
./demo.sh
./unsay --help
```

Exit: 0 ok, 1 `--check` found ALOUD, 2 error. `--emit` writes a unified
diff to stdout (`git apply` consumes it). Empty emit is not a hunk.

## Examples

### 1. sitbone `presentThreshold` — nothing to unspeak

```bash
./unsay -C ~/ghq/github.com/annenpolka/sitbone --blast e9b0f75 --emit presentThreshold
# stderr: unsay: 0 ALOUD (27 MUTE still ride); nothing to unspeak
```

e9b0f75 moved `threshold=0.4 → presentThreshold=0.45`. Every caller still
omits it. The blast is still silent. `--emit` is empty because ALOUD is 0.

### 2. Unspeak a survivor who spoke, then apply

```bash
./unsay -C <repo> --blast REV --emit | git -C <repo> apply
```

Synthetic three-commit fixture (`./demo.sh`):

| site   | at BLAST | later                    | --emit              |
| ------ | -------- | ------------------------ | ------------------- |
| camera | omitted  | omitted (MUTE)           | untouched           |
| mic    | omitted  | `presentThreshold: 0.45` | **deleted** → TACIT |
| radar  | `0.4`    | `0.4` (FOSSIL)           | untouched           |
| lidar  | `0.45`   | `0.45` (PRE)             | untouched           |
| new    | (absent) | `0.45` (LATE)            | untouched           |

After apply, mic rides again. A comma-regex for `, presentThreshold: 0.45`
would also have unsaid PRE and LATE.

### 3. Pin MUTE, or refuse LATE

```bash
# sitbone: 27 MUTE riders. --pin writes presentThreshold: 0.45 at each.
./unsay -C ~/ghq/github.com/annenpolka/sitbone --blast e9b0f75 --emit --pin presentThreshold | git apply

# kizu: tests born speaking --agent claude-code are LATE, not ALOUD.
./unsay -C ~/ghq/github.com/annenpolka/kizu --blast 3d4b543 --emit agent
# empty — stderr: 0 ALOUD (18 LATE born-speaking, never rode); nothing to unspeak
```

```bash
./unsay -C repo --blast REV --until HEAD --only aloud
./unsay -C repo --blast REV --check          # exit 1 if ALOUD remains
./unsay -C repo --blast REV --summary
```

Languages: Swift labeled inits, Python def/dataclass, TypeScript
`function`, Rust clap `default_value` (clap ALOUD unsays `--flag value`).
