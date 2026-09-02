# Transfer: hdd-envdrop onto envlayers

envlayers: one key across inherited / file / skip-empty / assign / process.

hdd-envdrop: POSIX shim drops `TEST-VAR` (not a valid identifier); the real
binary keeps it.

envlayers `--inherited` requires NAME=VALUE and inspects dotenv layers, not
two hop maps. Hyphen names are not that object.

Result: TRANSFER FAIL. Harvest is `envhop`.
