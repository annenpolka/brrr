# OBSERVED

Public gruntwork-io/terragrunt#764 (closed 2019-07-31). PR 774 merge `85f63b2bbde2fc8d9b207799e6891c171e6527ee` (first parent `17004093f058bfe45c59ab6e34fe3c46da86dbf8`). Local terragrunt was not performed on this lab host.

Issue body: changing `...?ref=` keeps the same `.terragrunt-cache` hash subdirs; leftover dest; `git pull` fails after cleanup deleted `.git`; deleting the cache folder pulls the new commit.

On failing_ref, encodeSourceName omits query/ref from the cache path. CopyFolderContents has no list of previously copied files, so leftover `stale.tf` survives a source update. PR 774 tests `test-stale-file-doesnt-exist-after-source-update`.

Not this packet: specimen-118 terraform leftover identity omitted from apply state. terragrunt#6468 leftover deleted git-module files still OPEN (not this merged pair). PR 4781 catalog `ref != ""` one-line flip is THIN_WRAPPER, not packed.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
