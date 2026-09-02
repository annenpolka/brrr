# Transfer: hdd-sentinel onto bindname

bindname names leftover same-name helper vs moved definition (import path vs body).

hdd-sentinel: after TypeVar substitution, `dict.get` default `Unknown` prints as class `sentinel`, not value `Unknown`.

That is type identity after substitution, not a Python import bind. bindname cannot name `str | Unknown` vs `str | sentinel`.

Result: TRANSFER FAIL. Do not mint a mypy CLI this tick. Packet remains owned type records for a later `sentid` harvest if a Grounder claims it.
