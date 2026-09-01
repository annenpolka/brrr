# capdiff

Named captures of a directory's `.env` plus a sha256 file manifest. Diff two captures. Replay by overlaying captured env vars and exec'ing a command.

```text
origin:
  method: hdd
  trial: hdd-ci
```

This is not `diff -ru`, `env`, or `direnv`. Those compare or load ad-hoc dumps. capdiff compares **labeled captures**.

## Commands

```bash
./capdiff capture NAME DIR
./capdiff diff A B
./capdiff replay NAME -- DIR CMD...
./capdiff replay NAME --files -- DIR CMD...
```

- **capture** stores `.capdiff/NAME/.env` (copy if present) and `.capdiff/NAME/manifest.json` (parsed env + relative path → sha256). Missing `.env` is an empty env map, not an error. It does not dump the tree.
- **diff** prints ENV modified/extra/missing and FILES modified/extra/missing. Exit `2` on any delta, `0` if identical.
- **replay** overlays captured env onto the current environment and execs `CMD` in `DIR`. `--files` writes the captured `.env` into `DIR`; other file bodies are not restored.

Python 3 stdlib only. No daemons, vaults, or tarball import.

## Run

```bash
./demo.sh
python3 -m unittest discover -s tests -v
```

Fixtures: `fixtures/env-a` and `fixtures/env-b` differ only in `.env` `API_KEY` and one extra file (`extra.txt` on b).
