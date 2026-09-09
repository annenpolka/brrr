# Destroyer notes for runpair (host 実機, not Dreamer text)

Attacks run against the isolated worktree CLI.

1. `true` twice: no added files. Held.
2. Writer script then same command: first adds `out.bin`, second no new names. Held.
3. `false` first: second still runs (rc 1, 1). Held — tool does not stop after first failure.
4. Nested file under subdir: snapshot ignores it (non-recursive). Documented limit, not a silent miss of cwd files.
5. Deno public-bundle copy: first adds `deno.lock`, second fails with `@.` — this is the motivating case, not an attack.
6. cwd and created file with spaces: HOLD (`x y.txt` size 1).
7. FIFO in cwd: ignored by snapshot (not a regular file). HOLD as a documented limit.
8. Second run grows sidecar size: changed before/after recorded. HOLD.
9. First run deletes existing file: removed recorded. HOLD.
10. Unicode filename + NUL binary: listed by name/size, contents not opened. HOLD.
11. stamp.py transfer (not issue 32113): first rc 0 adds `stamp.dat` size 5; second rc 2. HOLD as tool-contract transfer.

Not yet run: symlink-as-sidecar, FIFO, concurrent writers, very large cwd.

runpair does not open sidecar bytes, so lockfile-corruption interpretation is out of scope. A destroyer that expects the tool to explain `@.` should fail the *expectation*, not the tool.
