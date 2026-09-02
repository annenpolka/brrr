# envhop

origin.method: hdd
origin.trial: hdd-envdrop
specimens: [specimen-068]
classification: USEFUL_COMPOSITION

## Primitive

Name env keys dropped because they are not POSIX identifiers.

## Transfer attempt

envlayers inspects one key across dotenv loader layers. It does not model
a hop that drops invalid identifiers. Transfer FAIL.

## Smallest artifact

Python 3 stdlib CLI `envhop`.
