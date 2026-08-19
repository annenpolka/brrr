# noun (mutation-105)

v0.2. CI gate on leftovers of a change's **(package, noun)** natal.

lien treated every `version` as one noun. Two workspace crates collapsed; a kizu *release* that left `plugin.json` at 0.3.0 was a green CI because the stale manifest was a homonym of Cargo.toml's version. noun's identity is **(package, noun)** not bare `version`. A plugin.json leftover is not cleared by Cargo.toml 0.3.0→0.3.1.

Default input is a **unified diff on stdin**. Default output is **`--check`**: one dest-line lien (`path:line: via: …`), silent on success, exit 1 if the dest still speaks that record. `--explain` is the human natal dump.

Not leftover-name search. Dest scan still starts from the change's natals. Package identity *splits* workspace homonyms (`cli.version` ≠ `core.version`) and *keeps* same advertised name across sibling manifests (`crate:kizu` and `plugin:kizu` are one product noun). Binding leftovers (`t1`, `threshold`) are not package-gated, so sitbone `CLAUDE.md` both-rows still fail.

## Install / run

Python 3.10+, `git` on `PATH`. No other deps.

```bash
chmod +x ./noun ./demo.sh
./noun self-test
./demo.sh                 # exits 0; workspace split + kizu plugin.json + sitbone both-rows
./noun --help
```

Exit `0` if the dest has no leftovers, `1` if any remain, `2` on usage/error.

```
git diff | ./noun                     # CI check (default): current liens
git diff origin/main...HEAD | ./noun  # PR gate
git diff | ./noun --facts-only        # natal records, including package
git diff | ./noun --explain           # human natal dump (union)
git diff | ./noun --all               # CI-print kin + migration docs too
./noun --explain -C <repo> e9b0f75    # opt-in SHA dump
git diff | ./noun --json
git diff | ./noun -q                  # exit code only
```

`FILE:LINE` exits 2. Garbage stdin that is not a unified diff exits 2.

## Examples

**1. Two packages named `version` are two nouns.**

Bump `crates/cli` `0.3.0 → 0.7.0`. Independent crate `core` stays `0.3.0`.

```bash
git diff HEAD^ HEAD | ./noun --facts-only
# noun: 1 natal record(s)
#   value    crate:cli VERSION  0.3.0 → 0.7.0  (crates/cli/Cargo.toml:3)

git diff HEAD^ HEAD | ./noun
# README.md:1: claim: crate:cli VERSION  0.3.0 → 0.7.0: cli 0.3.0 and core 0.3.0 ship together.
# crates/core/Cargo.toml is quiet — different package.
```

Bump both in one commit (`cli 0.3.0→0.7.0` and `core 1.2.0→1.3.0`): two natal records. lien merged them into one and dropped the core bump.

**2. kizu plugin.json leftover is not a homonym of the crate bump.**

```bash
git -C kizu diff 9349dc5^ 9349dc5 | ./noun -C kizu
# plugin/plugin.json:4: claim: crate:kizu VERSION  0.6.0 → 0.7.0: "version": "0.3.0",
echo $?   # 1
```

lien was silent (rc=0): bound `0.3.0 ≠ 0.6.0` was `is_homonym`. Same advertised name `kizu` on a sibling manifest is this noun. `clap = { version = "4.6.0" }` is not. Default check is one dest-line, not 28 kin of the word `version`.

`53cbd1a` (`Cargo.toml 0.3.0→0.3.1`) still unpaid at `plugin/plugin.json:4`. The crate bump does not clear the plugin noun.

**3. sitbone hysteresis — both-rows still fail the gate.**

```bash
git -C sitbone diff e9b0f75^ e9b0f75 | ./noun -C sitbone
# CLAUDE.md:329: both: threshold↔presentThreshold  0.4 → 0.45: @Test("… threshold 0.4")
# CLAUDE.md:332: both: threshold↔presentThreshold  0.4 → 0.45: @Test("… threshold 0.4")
```

12 current liens, 4 `via=both`. `SPEC.md` `v0.4` is not leftover float `0.4`. Kin-only ADR quotes are `--explain`, not a CI fail. Package-scoping does not apply to this binding.
