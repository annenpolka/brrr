# Transfer: hdd-gitinc onto silentadd

silentadd: insert returned ok while a file/dir collision remained.

hdd-gitinc: `git config --unset` treats the value as a regex, Windows path `\` is an invalid pattern, leftover `includeIf` remains, workflow still concludes successfully.

Exit 0 hiding a leftover is adjacent, but the object is regex-unset vs collision-insert. silentadd has no config-key leftover.

Result: TRANSFER FAIL. No git. Later harvest: leftover key after failed value-pattern unset.
