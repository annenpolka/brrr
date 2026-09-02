# DESTROYER lockident

Candidate: `~/.grok/worktrees/annenpolka-brrr/lockident-lockident/lockident`
Attacked: 2026-09-02 12:29 JST

## Attacks

- no `--blob` → exit 2
- identity that matches none of the blobs → `in_identity none`, `live_lock_in_identity false`
- empty lock blob `lock_new=` vs nonempty src
- transfer: specimen-011 extra-output identity (`json.dumps({"src":"hello"})` key) vs blobs src / extra=out.sbom — extra omitted, src in if identity is src hash; using the fixture key `9280cc7e16e9` (input-hash) src membership depends on encoding

## Result

Happy path (specimen-016 lock omitted) holds. Missing blobs fail cleanly. Extra-output transfer correctly reports extra omitted when identity is the input hash.

Limitation: `--blob name=bytes` cannot express a JSON object identity without the caller computing `--identity`. That is acceptable for the harvest.

## Decision

KEEP
