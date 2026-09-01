# Harvest: hdd-ident

origin:
  method: hdd
  trial: hdd-ident

## Core Affordance

Compare two local names under exactly one explicit identity kind (inode, bytes, or canonical JSON) and refuse if the kind is omitted or mixed.

## Affordance Classification

USEFUL_COMPOSITION

## Nearest Existing Operation

stat; cmp; jq -S.

## Observable Delta

The identity kind is a required argument; the tool will not silently pick inode vs bytes vs JSON.

## Surviving Abstractions

- Identity kind
- Identical vs distinct under that kind
- Type mismatch (symlink vs file) as distinct under inode

## Removed Magic

- HTTP ETags, docker digests, database schemas

## Reality Mapping

os.stat st_ino; file bytes comparison or hashlib; json.dumps(sort_keys=True) after json.load.

## Smallest Useful Artifact

CLI `same --inode|--bytes|--json A B`

## Why Existing Tools Are Not Enough

stat/cmp/jq exist separately and do not force the caller to name the identity kind.
