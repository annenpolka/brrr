# clink

Show **compiled callers** that last saw a different **signature** than HEAD.

Default is source-extension files only (`.py`, `.rs`, `.ts`, …). Plan and markdown mentions stay behind `--docs`. Comments and string literals inside source files are not compiled callers. `--check` is the CI verb: exit 1 if any compiled caller last saw a different signature than HEAD. Body-only diffs sit behind `--body`. Last-saw vs HEAD headers are whitespace-collapsed, so a multiline reflow is not a contract change.

Ancestor `doze` gated on every use-site, including `plans/*.md`. `clink` is the compiled-caller gate.

## Install / run

```bash
chmod +x clink demo.sh
./clink --help
./demo.sh
```

Requires Python 3.9+ and `git`. No other dependencies. Point `--repo` at any git checkout, or run from inside one.

```bash
./clink [--repo PATH] [--check] [--docs] [--body] [--diff] [--ghosts] [--format human|json|tsv] [symbol|path|path:line]
```

Exit 0 on a successful query with no signature lag. `--check` exits 1 if any compiled caller last saw a different signature than HEAD.

## Examples

**1. Which compiled callers missed the new signature?**

```bash
./clink --repo ./fixtures/lagrepo greet
```

Prints `src/app.py` and `tests/test_greet.py` as callers that last moved before `greet` gained `excited` and `prefix`, plus the last-saw vs HEAD signatures. `docs/api.md` and `plans/v0.md` stay hidden. Body-only `trim` is hidden.

**2. CI gate (compiled callers only).**

```bash
./clink --check --repo . insert_scar
```

Exit 1 and print `path:line: insert_scar: signature changed` with last-saw / HEAD headers if any compiled caller still sees the old contract. Plan-file mentions do not fail the build. Silent exit 0 if every compiled caller last saw the HEAD signature.

**3. Include docs, or pin one line.**

```bash
./clink --repo ./fixtures/lagrepo --docs greet
./clink --repo ./fixtures/lagrepo src/app.py:6
```
