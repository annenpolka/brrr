# sic

A protocol token is the **serialized wire key as written** — a JSON / YAML / TOML key, an HTTP header name, or a quoted protocol string. Not a code identifier. Not an inflection class.

`has_more` and `hasMore` are different tokens. If both appear on the wire, that is a **fork**.

## Install / run

Python 3.10+, no third-party packages. From this directory:

```bash
chmod +x ./sic
./sic --help
./demo.sh
```

`sic` scans the current git repo (or `-C PATH`). It reads tracked and untracked non-ignored files (`git ls-files -co --exclude-standard`).

## Examples

List exact wire keys that bind two or more files:

```bash
./sic -C ~/src/tenaoshi --limit 8
# has_more  files: 22  kinds: json,quoted  layers: code,config,doc,test
#   Engine/Sources/TenaoshiEngine/EditPlan.swift:103  quoted
#   contracts/testcases/EPF-001.json:10               json
```

Look up one spelling. A miss that has an inflection neighbor is a fork hint, not a synonym:

```bash
./sic -C ~/src/kizu hook_event_name
# hook_event_name  files: 6  kinds: json  ~forks: hookEventName

./sic -C ~/src/kizu --forks hook_event_name
# FORK  hook.event.name
#   hook_event_name   files: 6   kinds: json     # stdin payload
#   hookEventName     files: 2   kinds: json     # stdout payload
```

Ask whether this patch updated an exact key on only some of its files (exit 1 = leftovers still speak the old bytes):

```bash
git diff | ./sic --check
./sic --check                 # working tree + index
git diff origin/main | ./sic  # stdin that looks like a diff auto-checks
```

Porcelain / JSON for pipelines:

```bash
./sic --porcelain has_more | cut -f3 | sort -u
./sic --json --limit 20
```

## How it works

Identity is the exact key text. HTTP header names fold case (RFC 9110); JSON/YAML/TOML keys do not. Identifiers such as Swift `hasMore` or Pkl `hasMore = false` are ignored. `--forks` lists distinct serialized spellings that *would* have been one `aka` cognate.

Exit codes: `0` ok / clean check, `1` lookup miss or one-sided check, `2` usage, `130` interrupt.
