# Harvest: hdd-env

origin:
  method: hdd
  trial: hdd-env

## Core Affordance

Show where effective environment variables come from (file:line override, inherited, unset), especially those implicated in a command.

## Affordance Classification

USEFUL_COMPOSITION

## Nearest Existing Operation

env; bash -x; direnv status.

## Observable Delta

Per-variable source, not only the value.

## Surviving Abstractions

- Override source (path:line)
- Inherited vs explicit empty vs unset
- Precedence among process env, .env, defaults

## Removed Magic

- Editing to fix
- Invented checksums
- Live runtime metrics

## Reality Mapping

Read process env and dotenv-like files. For each requested key, report value and source. Optionally wrap a command (print provenance then exec).

## Smallest Useful Artifact

CLI `envfrom [KEY...]` and `envfrom --run CMD`.

## Why Existing Tools Are Not Enough

`env` prints values, not which file emptied them.
