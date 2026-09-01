# stated

Given a configuration key, show **where it is declared** and **where the tree assigns or implies a different value**.

This is not `rg KEY`. The observable is the disagreement pair (declaration site vs contradicting site), or a confirmation that comparable scalars agree / that only one side exists.

## Run

```bash
python3 stated KEY [DIR]
python3 stated --json KEY [DIR]
```

Exit codes:

| code | meaning |
|------|---------|
| 0 | comparable values agree, only one side exists, nothing found, or values are not statically comparable |
| 1 | usage error |
| 2 | comparable values disagree |

Config-like files scanned: `*.yml`, `*.yaml`, `*.toml`, `*.cfg`, `*.ini`, `*.json`, `.env`.

Source files scanned: `*.py`, `*.js`, `*.ts`, `*.go`, `*.rs`, `*.c`.

Literal scalars (`5`, `"5"`, `true`) are compared. Interpolations, calls, and identifiers are reported as unknown rather than forced equal/unequal. Whole-line `#` / `//` comments, `/* */` blocks, and Python docstrings are labeled separately and ignored for comparison.

## Demo

```bash
./demo.sh
python3 -m unittest tests.test_stated
```

Fixtures:

- `fixtures/disagree` — `config.yaml` says `timeout: 5`, `app.py` says `timeout = 10`
- `fixtures/agree` — both say `5`
- `fixtures/config_only` — declaration, no assignment
- `fixtures/unknown` — `${WAIT}` vs `os.getenv("WAIT")`
- `fixtures/comments` — real values agree at `5`; `#` / docstring / `/* */` mentions of `99` are labeled comments, not contradictions

## Limits

Partial format coverage. No runtime evaluation. Nested structure is only seen insofar as a `KEY:` / `KEY=` line is visible. Does not invent deploy, hotfix, or live metric systems.
