# HDD Ledger

Iteration: 1

## Preserve

- A file-backed template can expand {posargs} while a CLI override of the same spelling does not
- Process exit 0 does not say which tests the override ran
- A template token can expand from a file and stay literal under a CLI override while leftover args remain

## Established

- Host fixture: file_argv pytest tests src; override_argv last token {posargs}; override_exit 0; override_ran_against {posargs}
- Owned fixture: file-backed expands; CLI override keeps {posargs} literal; leftover ['tests','src']

## Rejected

- sdg / env-inq / SUBST_DEBUGGER output is not installed evidence
- A physical directory named {posargs} was not observed on this host
- Invented workspace listing is not needed

## Constraints

- Owned override_subst.py is the world
- Ground on override_subst.py

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- Ask which layer expanded the token and which tests the override actually ran
- Which layer expanded the token vs which left it literal

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: show which layer expanded a template token and which leftover args never entered it
Nearest existing operation: print argv and the template file
Observable delta: names expansion layer vs leftover args
Reason: exit 0 on literal {posargs} hides the missed substitution
Assessed at iteration: 1

## Latest Red Pen Pressure

- (none)

## Pending

(none)
