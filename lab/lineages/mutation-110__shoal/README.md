# shoal

Mint a durable locus token from a `file:line` once; resolve it onto a later tree **without** re-supplying `path:line`.

**Origin is signed remotes at mint time plus required witnesses, not live `git remote` config.** The token binds the project's remotes to the locus with a mint-time signature. Dest remotes are config: `git remote add extra git@github.com:victim.git` is not the project. A fetched SHA is occupancy, not identity. A true `file:// --depth 1` clone of the signed project still resolves. Missing origin fail-closes unless `--any-repo`.

## Install / run

```bash
chmod +x ./shoal
./shoal --help
./shoal --selftest
./demo.sh
```

Requires Python 3.9+ and `git`.

## Interaction

```
shoal mint    [--from <ref> | --from-dir DIR] path:line     # once
shoal resolve [--to <ref>   | --to-dir DIR]   shoal1.…      # later tree
shoal show shoal1.…
shoal id --repo /path
```

`shoal resolve` refuses `path:line`. That is the point.

`--to` must name an object that exists. Truncated `shoal1.…` tokens exit 1. Origin mismatch exits 1 unless `--any-repo`. Extra remotes on dest never participate. `shoal id` prints **origin** (plus clone-parent hops of origin), not `git remote add` extras. `www.github.com` / `ssh.github.com` of the signed path are one project; a gitlab URL of the same path is not. A 3-hop `file://` chain of the signed project still resolves.

## Examples

Mint the line a review comment would have cited. Remotes are signed now:

```bash
./shoal mint --repo ~/src/kizu --from b4e6a5d src/app.rs:529
# shoal1.eJyt…
```

Later, on today's tree — or a `file:// --depth 1` checkout of the same project — no path, no line:

```bash
./shoal resolve --repo ~/src/kizu --to HEAD shoal1.eJyt…
# src/app.rs:529  →  src/app/layout.rs:17   moved
```

A stranger who adds the victim remote, or fetches one witness SHA, is still foreign:

```bash
git -C ~/src/other remote add extra git@github.com:annenpolka/kizu.git
git -C ~/src/other fetch ~/src/kizu HEAD
./shoal resolve --repo ~/src/other --to HEAD shoal1.eJyt…
# shoal resolve: token belongs to a different repository
# exit 1
```

`--any-repo` is the documented override. Missing `o` on the token is no longer a silent one.
