# stubextra

origin.method: hdd
origin.trial: hdd-s071
specimens: [specimen-071]
classification: USEFUL_COMPOSITION

## Primitive

Name leftover extra stub on a FRESH hit versus extra produced for this request.

## Core operation

Two cache events: extra_requested, extra_bytes, key, status.
leftover_stub when same key, first wrote empty extra without request, second FRESH with request and still 0 bytes.

## Removed

Invented cachetool.

## Smallest artifact

Python 3 stdlib CLI `stubextra`.
