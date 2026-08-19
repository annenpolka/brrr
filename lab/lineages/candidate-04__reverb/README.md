# reverb

**The old side of your diff is a search query: find the copies you did not change.**

## Install / run

Requires Python 3.9+ and `git`. From this directory:

```bash
chmod +x reverb demo.sh
./reverb -h
./demo.sh
```

Put `reverb` on your `PATH`, or run it as `python3 ./reverb`.

Exit codes (grep-like): **0** no lingering preimages, **1** copies found, **2** error.

## Examples

Working tree vs `HEAD` — you fixed a nil check in one file; what still has the old block?

```bash
./reverb
```

JSON for tools; grep-like lines for `cut` / `awk`:

```bash
./reverb --json | jq '.matches[].match.path'
./reverb --grep | cut -d: -f1 | sort -u
```

Pipe any unified diff. `-C` is the tree to search (defaults to cwd / git toplevel). Token clones catch the same shape with different names (`user` vs `account`):

```bash
git diff main...HEAD | ./reverb --stdin -C . --grep
git show --format= 9aaabbb | ./reverb --stdin
./reverb --json   # "kind": "exact" | "indent" | "token" | "string"
```

## Interaction model

1. Take a unified diff (`git diff HEAD` by default, or stdin).
2. Reconstruct each hunk's *preimage* (deleted lines, widened with nearby context when the deletion is too short to be a useful query). Also lift distinctive string literals out of the deletion.
3. Search the worktree — including nested git repos — for remaining copies: exact, indent-normalized, then identifier/string-normalized token clones.
4. Print those sites. The file you already edited no longer contains the preimage, so it drops out; the copies you forgot do not.

This is not `rg` of a string you remembered, and not clone detection of the whole repo. The *change itself* selects the query.
