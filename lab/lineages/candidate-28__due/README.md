# due

The environment a program is owed. `ldd` for env vars.

Harvest the names a binary, script, or source tree actually consults (`getenv`, `os.environ`, `env::var`, `process.env`, `$FOO`, …). Join that ABI against one or two environments. Pack the env you can ship. Diff local vs CI on *just the names that matter*.

## Install / run

```bash
chmod +x ./due
./due --help
./due --selftest
./demo.sh
```

Python 3.10+, stdlib only.

## Interaction

```
due PROGRAM                    # owed names ⋈ current env
due PROGRAM --vs other.env     # DIFF / MISSING / UNSET_* on the owed set
due --left a.env --right b.env --example .env.example PROGRAM
due SRC_DIR                    # directories are walked (skips node_modules/target/…)
due PROGRAM --emit             # packed KEY=VAL (owed ∩ left)
due PROGRAM --dump-abi         # name, evidence, source as a Unix table
due --abi names.tsv --vs ci.env
due SRC --vs-program IMAGE     # source ABI ⋈ shipped image
```

Exit 0 when the left env pays every owed name (and matches the right, if given). Exit 1 on `MISSING` / `DIFF` / `UNSET_*` / `UNDOCUMENTED`. Exit 2 on usage errors. `--report-only` always 0. `--check` is the same as the default env-join; for `--vs-program` it fails only on `LEFT_ONLY` (source name absent from the image).

`--app` hides well-known libc/runtime names (`PATH`, `HOME`, `XDG_*`, …). Secrets in `*KEY*`, `*TOKEN*`, `*SECRET*` are redacted unless `--show-values`.

## Examples

Local `.env` vs CI, only the names the tree actually reads:

```bash
./due --left fixtures/envs/local.env --right fixtures/envs/ci.env \
      --example fixtures/envs/example.env --spare --app fixtures/ugly
# DIFF          DUE_PORT     3000          8080
# UNSET_RIGHT   DUE_HOME     /tmp/due-local -
# UNSET_LEFT    DUE_TOKEN    -             ci-token
# STALE_EXAMPLE DUE_UNUSED   -             -        (documented, unread)
# UNDOCUMENTED  DUE_CONST    …                      (code reads it, example doesn't)
```

What kizu actually consults, and whether this shell pays it:

```bash
./due --app --min-evidence call ~/src/kizu/src --report-only
# MISSING  KIZU_CONFIG
# MISSING  KIZU_STATE_DIR
# DUE      TMUX            /private/tmp/tmux-501/…
```

Did the shipped binary keep the source env ABI? Rust packs literals (`KIZU_CONFIGXDG_CONFIG_HOME…`); `due` still confirms them:

```bash
./due --app --min-evidence call ~/src/kizu/src --vs-program ~/src/kizu/target/release/kizu
# BOTH        KIZU_CONFIG
# BOTH        ZELLIJ
# RIGHT_ONLY  RUST_BACKTRACE     # std, not your code
```
