# falseomit

origin.method: hdd
origin.trial: hdd-omitfalse
specimens: [owned-encodings, specimen-077]

classification: USEFUL_COMPOSITION

## Primitive

Name keys present as false in one JSON encoding and absent in the other.

## Why this might not exist

`json.dumps` and `"flag" in obj` both hit. The miss is the join: this key
was false in one encoding and missing in the other, and missing is decoded
as true.

## Core operation

Read two JSON objects. Print dropped_false = keys in B whose value is false
and which are absent in A.

## Observable delta

Owned: dropped_false flag; a_has flag no; b_has flag yes; b_value false.

## Removed

Invented inspect/diff/probe CLI.

## Smallest artifact

Python 3 stdlib CLI `falseomit`.
