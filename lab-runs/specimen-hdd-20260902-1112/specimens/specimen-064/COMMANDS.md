# COMMANDS

```
nix eval --raw --expr '(builtins.fetchGit { url = $TEST_ROOT/minimal; rev = "<rev2>"; }).outPath'
# failing revision also emits:
#   could not read HEAD ref from repo at '...', using 'master'
```

Not executed on this lab host.
