# aka

Find protocol tokens that live under several names (`has_more` / `hasMore` / `HAS_MORE`) and catch patches that update only one of them.

## Install / run

Python 3.10+, no third-party packages. From this directory:

```bash
chmod +x ./aka
./aka --help
./demo.sh
```

`aka` scans the current git repo (or `-C PATH`). It reads git-tracked files by default. Listing keeps tokens with **two or more surface forms** (`--min-forms 1` to include exact clones).

## Examples

List implicit wire identities in a repo — one token, many surface forms, many files:

```bash
./aka -C ~/src/tenaoshi --limit 8
# has.more  forms: hasMore, has_more  files: 11  layers: code,doc,test
#   Engine/.../EditPlan.swift:70   ident  hasMore
#   specs/tenaoshi.pkl:33          key    hasMore
#   docs/SPEC.md:88                ident  has_more
```

Look up any surface form and see the others:

```bash
./aka -C ~/src/kizu hook_event_name
# hook.event.name  forms: hookEventName, hook_event_name
```

Ask whether this patch split a protocol (exit 1 = leftover files still speak the old name):

```bash
git diff | ./aka --check
./aka --check                 # working tree + index
git diff origin/main | ./aka  # stdin that looks like a diff auto-checks
```

Porcelain / JSON for pipelines:

```bash
./aka --porcelain has_more | cut -f4 | sort -u
./aka --json --limit 20
```

## How it works

Quoted strings, YAML/JSON keys, and `--flags` define the wire vocabulary. Identifiers that inflect to the same canonical parts are treated as the same token. A *pact* is a token that appears in two or more files. `--check` is the verb: if a patch removes a token from some of those files and others still have it, that is a split brain.

Exit codes: `0` ok / clean check, `1` lookup miss or one-sided check, `2` usage.
