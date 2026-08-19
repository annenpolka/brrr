# nagori (名残)

Print leftover claims a diff just made false.

A *fact* is a bound name/value, rename, or polarity flip in a unified diff. An *afterimage* is a comment, doc, test, string, or config line in the destination tree that still asserts the old fact.

This is a from-behavior reimplementation of `zanei` (candidate-07). The original Python file was never opened.

## Install / run

Requires Python 3.10+ and `git` on `PATH`. No other dependencies.

```bash
chmod +x ./nagori ./demo.sh
./nagori --help
./nagori self-test
./demo.sh          # fixture tests; exits 0 on success
```

Exit codes: `0` none found, `1` afterimages found, `2` usage/error.

Default comparison is `HEAD` → working tree (staged + unstaged), like `git diff HEAD`. Output is human text; `--tsv` and `--json` are pipeable.

## Examples

**1. What did this edit make untrue?**

```bash
# change a default in code, forget the README / tests
./nagori
```

```
nagori: 6 afterimages  HEAD → worktree  (/path/to/repo)

FACT timeout: 10 → 30   src/init.rs:208
   92 comment src/init.rs:15          // hook timeout is 10 seconds
   84 test    src/init/tests.rs:18    timeout: Some(10)
   80 docs    README.md:240           timeout: 10
```

**2. Afterimages of a historical range (linter-composable).**

```bash
./nagori v0.3.0 v0.7.0
./nagori HEAD~1 HEAD --tsv | awk -F'\t' '$2=="docs"'
test -z "$(./nagori --json HEAD~1 HEAD | python3 -c 'import json,sys; print(json.load(sys.stdin)["findings"] and "x")')"
```

**3. Feed someone else's patch.**

```bash
git show HEAD | ./nagori --diff -
curl -sL https://example/patch.diff | ./nagori --diff - -C /path/to/repo
```
