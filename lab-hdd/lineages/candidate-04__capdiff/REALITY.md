# Pre-implementation Reality assessment

Copied unchanged from the harvest, before any code was written.

Serialize cwd env files (.env) and a file list/hashes. Diff two captures. For replay: export captured env and exec a command in a directory.

origin:
  method: hdd
  trial: hdd-ci

Classification: USEFUL_COMPOSITION

Nearest existing operations: diff -ru; env; direnv.

Observable delta: the compared object is a labeled environment capture, not an ad-hoc pair of dumps the user has to remember.

Removed magic: tarball import, vaults, auto-started daemons.
