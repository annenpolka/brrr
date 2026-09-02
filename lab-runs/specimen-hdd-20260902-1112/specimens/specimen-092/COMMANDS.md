# COMMANDS

```
# failing_ref d5eda907ef98fb9a0304c323a8f8a5fb99c94c35
# (not executed on this lab host)

# in-tree repro shape (test file appears on PR head; knobs match the failing world)
# tests/functional/flakes/cache-poisoning.sh

export GIT_COMMITTER_DATE="2000-01-01T00:00:00+0000"
export GIT_AUTHOR_DATE="2000-01-01T00:00:00+0000"

# dep flake: outputs.expr = "rev1" then later "rev2"
# consumer: inputs.dep.url = git+file://$depDir

# case A — consistent lock
nix flake lock "$consumerDir"
nix eval "$consumerDir#expr"     # "rev1"
# flake.lock nodes.dep.locked.narHash = H_nar1
# fetchToStore cache key uses getFingerprint = dep rev1

# case B — lock rev := rev2, narHash still H_nar1
jq --arg rev "$rev2" '.nodes.dep.locked.rev = $rev' flake.lock
nix eval "$consumerDir#expr" || true
# substitution: computeStorePath(H_nar1) still in store
# fingerprint is now rev2

# case C — lock rev := rev2, narHash := H_nar2
# H_nar2 from: git archive HEAD | tar xf; nix hash path --type sha256 --sri
nix eval "$consumerDir#expr"
# failing_ref: NAR hash mismatch / mismatch in field 'narHash'
# public CI: expected H_nar_live, got H_nar_stale (or field-mismatch of those two)

# case D — same corrected lock, empty ~/.cache/nix/fetcher-cache-v4.sqlite
# eval "rev2"; no mismatch
```

Not executed on this lab host.
