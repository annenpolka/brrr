# nook

A protocol token is the **key path** through a serialized object — `pagination.has_more`, not the bare leaf `has_more`. Two `has_more` in different objects are different identities. They are not one leftover.

`sic` asked whether the exact bytes `has_more` still live in N files. `nook` asks whether the *same slot* still lives in N files. `pagination.has_more` vs `pagination.hasMore` is still a **fork**. `pagination.has_more` vs `meta.has_more` is a **homonym**.

## Install / run

Python 3.10+, no third-party packages. From this directory:

```bash
chmod +x ./nook
./nook --help
./demo.sh
```

`nook` scans the current git repo (or `-C PATH`). It reads tracked and untracked non-ignored files (`git ls-files -co --exclude-standard`).

## Examples

List key paths that bind two or more files:

```bash
./nook -C ~/src/tenaoshi --limit 8
# mock_plan.has_more  files: 8  kinds: json
#   contracts/testcases/EPF-001.json:10  json
```

Look up one path. A miss that shares a leaf is a homonym hint, not a synonym:

```bash
./nook -C ~/src/tenaoshi pagination.has_more
# nook: no key path 'pagination.has_more'
#   leaf homonyms: has_more, mock_plan.has_more, units[].has_more

./nook -C ~/src/tenaoshi --homonyms --leaf has_more
# HOMONYM  has_more
#   has_more              parent: ∅           # CodingKeys / plan root
#   mock_plan.has_more    parent: mock_plan   # EPF fixture wrapper
```

Ask whether this patch updated a *path* on only some of its files. A leftover `meta.has_more` does not fail a `pagination.has_more` rename:

```bash
git diff | ./nook --check
./nook --check
```

Porcelain / JSON for pipelines:

```bash
./nook --porcelain pagination.has_more | cut -f3 | sort -u
./nook --json --homonyms --leaf has_more
```

## How it works

Identity is the dotted path. Arrays collapse to `[]` (`units[].source_text`). HTTP header names fold case (RFC 9110); JSON/YAML/TOML path segments do not. Identifiers such as Swift `hasMore` are ignored. CodingKeys / serde `rename` take the enclosing type as the parent (`WirePlan.has_more` vs `Batch.has_more`). `--forks` lists distinct spellings of the *same path*. `--homonyms` lists the same leaf under different parents.

Exit codes: `0` ok / clean check, `1` lookup miss or one-sided check, `2` usage, `130` interrupt.
