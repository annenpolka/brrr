# yoke

Join spec clauses to generated witnesses and print the slack.

`just spec-check` answers a boolean: *if I regenerated right now, would committed artifacts move?* That is file-level, expensive, and silent about *which clause* drifted. yoke answers the missing question-word:

> for each stable clause id, is the generated projection taut, slack, hand, split, or riven?

It does **not** run Pkl or the generator. The join key is the clause id (`EPF-001`, `FLT-001`, `BEM-001`).

## Install / run

Python 3.10+, `git` on `PATH`. No other dependencies.

```bash
chmod +x ./yoke
./yoke --help
./demo.sh
```

Exit `0` if every clause is taut, `1` if any slack/hand/split/riven remains, `2` on tool error.

## Examples

**1. Is this worktree's generated tree still heeling to specs/ ?**

```bash
./yoke -C ~/src/tenaoshi
# yoke  spec=:  gen=:  clauses=74  taut=74 slack=0 hand=0 split=0 riven=0
```

**2. Spec moved. Generated did not. (or the other way.)**

```bash
# committed spec vs dirty generated
./yoke -C ~/src/tenaoshi --spec HEAD --gen :
# slack CTR-001  … spec clause has no generated witness
# hand  EPF-001  … generated id has no spec parent

# which clauses the spec edit actually moved, and which generated files cite them
./yoke -C ~/src/tenaoshi --punch HEAD
# removed   CTR-001   …  gen contracts/testcases/CTR-001.json:1, docs/SPEC.md:17
# added     EPF-001   …  gen docs/SPEC.md:19, contracts/testcases/EPF-001.json:1
```

**3. Pipe it.**

```bash
./yoke -C ~/src/voidtrace HEAD --json | jq '.counts'
./yoke -C ~/src/relico --only slack,hand,split,riven --tsv
./yoke -C ~/src/voidtrace --files   # file-level leash from @generated banners
```

`--spec` / `--gen` take a git ref or `:` (worktree, including untracked). `yoke HEAD` means both sides at HEAD.

## Verdicts

| verdict | meaning |
| --- | --- |
| taut | spec and generated witnesses agree (narrower projections allowed) |
| slack | spec is ahead: generated missing or older body |
| hand | generated has no live spec parent |
| split | some witnesses match spec, others drifted (partial regen) |
| riven | conflict markers on a spec or generated witness |
