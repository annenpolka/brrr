# TASK

A flake.lock node names two identities for one input: git `rev` and `narHash`. After a manual `rev` edit that leaves `narHash` behind, then a later correction of `narHash`, evaluation still fails as if the old NAR were the live tree for that `rev`.

Public CI (NixOS/nix#15198), self-hosted GitHub Actions runner with a Nix daemon. Input `github:blockfrost/blockfrost-tests`. Both records share:

```
rev: 5297592395d1dbd46e88247e459896838c854340
lastModified: 1770733010
type: github
```

They disagree on `narHash`:

```
H_nar_stale = sha256-4cKMeE/8GptnxWnB6LliJy3gCvjVI34TXTwQHEsHcUA=
H_nar_live  = sha256-YR+cemfm4AMEJcUEr/tm0cis3rWKQ0dPFbjwhEVrV94=
```

Case A — lock is consistent (`rev` R1 with matching `narHash` H_nar1). `nix flake lock` then `nix eval`. Store path is `computeStorePath` from H_nar1. Cache upsert uses fingerprint `getFingerprint(store)` (GitHub scheme: the git rev string). Eval of the consumer's `expr` is `"rev1"`.

Case B — same consumer, lock `rev` rewritten to R2, `narHash` still H_nar1, `lastModified` unchanged (in-tree repro forces `GIT_COMMITTER_DATE`/`GIT_AUTHOR_DATE` so a lastModified mismatch does not fire first). `nix eval` on this lock. H_nar1's store path still exists from case A. Substitution fast path can serve that path while the fingerprint is now R2.

Case C — lock corrected to `rev` R2 with `narHash` H_nar2 (H_nar2 from `git archive` + `nix hash path` of R2, not from a Nix fetch of R2). Same runner / same `~/.cache/nix/fetcher-cache-v4.sqlite`. `nix eval` fails. Public log shape:

```
error: NAR hash mismatch in input 'github:blockfrost/blockfrost-tests/5297592395d1dbd46e88247e459896838c854340?narHash=sha256-4cKMeE/8GptnxWnB6LliJy3gCvjVI34TXTwQHEsHcUA%3D', expected 'sha256-YR+cemfm4AMEJcUEr/tm0cis3rWKQ0dPFbjwhEVrV94=' but got 'sha256-4cKMeE/8GptnxWnB6LliJy3gCvjVI34TXTwQHEsHcUA='
```

Issue body also records `mismatch in field 'narHash'` of two `__final` github inputs that share `rev` and `lastModified` and disagree only on `narHash`. Workaround on the runner: delete `~/.cache/nix/fetcher-cache-v4.sqlite` or reboot. `nix flake update` after the poison still fails.

Case D — correct lock (`rev` R2, `narHash` H_nar2) on a **fresh** fetcher cache that never saw case B. Eval is `"rev2"`. No mismatch.

The developer wants to know which identity the substitution cache actually keyed for that input — lock `rev` fingerprint or lock `narHash` — and which NAR store path that key mapped to after case B.
