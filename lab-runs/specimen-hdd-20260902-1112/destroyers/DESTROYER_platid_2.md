# DESTROYER platid 2

Date: 2026-09-02 15:06 JST
RUN_ID: specimen-hdd-20260902-1112
Target: `lineages/candidate-platid/platid`

sha256 `a2e6b00da79a66c1780b0a8f0abd4b5169eca57e157d2241b1ea402881d46588` (4671 bytes).
No platid worktree pointer required. Parent `main` coordinator-only; not merged.
`bundle` / `ruby` not invoked.

Origin (`CANDIDATE.md` / harvest `hdd-s074` / specimen-074): name the gem
identity install materialized versus the identity setup searched for, when
name+version match and platform does not. Kind: USEFUL_COMPOSITION.

First destroyer (`DESTROYER_platid.md`) required: rc=1 on mismatch; name
whether install_ok hid lookup_miss. Those landed. Tests 3/3. `demo.sh` twice
identical. Happy path is real. That is not enough.

This cut is the same primitive that Honor-KILLed sibling `platident`
(`DESTROYER_platident_2.md`): `hidden_by_exit0` is string inequality plus two
default-true flags. First MUTATE is not protection. Decision: **KILL**.

```text
CLI=.../lineages/candidate-platid/platid
FIX=.../lineages/candidate-platid/fixtures
```

No bundler. Do not grow a lockfile / gem-index parser to escape THIN_WRAPPER.
Do not send frozenplat theater back to R1.

## What still works

Owned 074: installed `nokogiri-1.18.10` vs lookup `nokogiri-1.18.10-x86_64-linux`.
`mismatch yes` / `install_ok yes` / `lookup_miss yes` / `hidden_by_exit0 yes` / rc=1.

Unseen darwin vs ruby same shape. Missing path rc=1. Same file twice: mismatch
no, hidden no, rc=0.

```bash
python3 "$CLI" "$FIX/074-installed.rec" "$FIX/074-lookup.rec"; echo rc=$?
```

```text
installed	nokogiri-1.18.10
lookup	nokogiri-1.18.10-x86_64-linux
mismatch	yes
install_ok	yes
lookup_miss	yes
hidden_by_exit0	yes
rc=1
```

## Implementation

```python
mismatch = installed.full != lookup.full
install_ok = True if install_exit is None else install_exit in {"0","ok","success"}
lookup_miss = mismatch if lookup_status is None else lookup_status in {"miss","missing","fail","1"}
hidden = mismatch and install_ok and lookup_miss
rc = 1 if mismatch else 0
```

Host replica of `inspect` + `format_report` matches the CLI on owned, unseen,
same-file, hyphen names, and `full` override. `test "$full_a" != "$full_b"` is
the load-bearing bit. The flags only relabel that bit.

### 1. THIN_WRAPPER of full-name inequality

Missing `install_exit` defaults `install_ok yes`. Missing `lookup_status`
defaults `lookup_miss` to `mismatch`. Owned fixtures omit both flags, so
`hidden_by_exit0` is `full_a != full_b`.

`install_exit 1` with the owned lookup: `install_ok no`, `hidden_by_exit0 no`,
**rc still 1** because mismatch. The harvest bit (exit 0 hid the miss) is not
the exit code. rc follows `mismatch`, not `hidden_by_exit0`.

`lookup_status ok` with the owned pair: `lookup_miss no`, `hidden_by_exit0 no`,
**rc still 1**. A successful setup lookup of a different full name is still
the harvest exit.

`full` override vs platform: installed `platform x86_64-linux` but
`full nokogiri-1.18.10` vs lookup linux full → `same_platform yes`,
`mismatch yes`, `hidden_by_exit0 yes`. Platform fields are spectators.
Identity is the `full` string the caller already typed.

Hyphenated `foo-bar` 1.0.0 ruby vs linux: compose does not split the name.
That is better than platident's `split_id`. It does not create a new
observation: the two `full` strings still differ.

Swapped argv (lookup, installed): mismatch yes, hidden yes, rc=1. Order of
files is not install-vs-setup.

### 2. Not a lockfile, not bundler

Unknown field / no tabs / missing name: `platid: …` rc=1. There is no GEM
specs parser, no `PLATFORMS` walk, no `required_ruby_version`. `demo.sh`
already prints both full names before invoking the CLI. The `.rec` files
already contain the answer as `full` / `platform` keys.

### 3. Defaults are the specimen

The harvest is: frozen install exit 0 materialized ruby; setup searched linux.
The CLI treats absent exits as that story. A record that only names two
fulls is a hidden_by_exit0 harvest. That is not evidence of exit 0.

## Primitive

Parse two TSV tables of name/version/platform/full plus optional exit flags;
hidden iff the two `full` strings differ and the flags (defaulting to the
specimen) say install ok and lookup miss; rc=1 iff the strings differ.

Nearest: `test` of two caller-typed names, or `printf` of both. Observable
capability lost if platid vanishes: **none**. The harvest question (which
identity install materialized vs which setup searched) is real. This
embodiment asks it of strings that already are those identities.

Sibling platident Honor-KILL: same `hidden_by_exit0` ↔ inequality + two
default-true flags. platid's mutate added rc=1 and structured fields. The
fields are still caller-typed. Bakeoff preferred platident until its second
destroyer; both are now fossils.

Honor KILL. Dreamer ancestry is not protection. First MUTATE is not
protection. Do not send THIN_WRAPPER back to R1. Do not merge onto `main`.
Do not launch `hdd-frozenplat` as a second spend on this question.

---

KILL
