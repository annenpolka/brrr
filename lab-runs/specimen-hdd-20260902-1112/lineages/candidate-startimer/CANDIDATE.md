# startimer

origin.method: hdd
origin.trial: hdd-s066
specimens: [specimen-066]

classification: USEFUL_COMPOSITION

## Primitive

Name the timer armed while status was starting, remaining time when the
start period ended, and when the first counted failure fires.

## Why this might not exist

The four duration fields are all in the config. Printing them still leaves
“the monitor armed start-interval at t=0 and did not reset at period end”
as a hand join.

## Core operation

Replay failing `getInterval`: while t < StartPeriod and status=starting,
return StartInterval. Arm that timer at t=0. Print remaining at period end,
first probe, unhealthy_at vs expected (period + interval).

## Observable delta

One query names armed 30s vs remaining 28s at period end vs unhealthy at
30s not 4s. The four numbers do not.

## Reality mapping

Owned numbers from specimen-066. No dockerd.

## Removed

Invented dockersim.

## Smallest artifact

Python 3 stdlib CLI `startimer`.
