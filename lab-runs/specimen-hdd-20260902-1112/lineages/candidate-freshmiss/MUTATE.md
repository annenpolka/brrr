# MUTATE freshmiss (queued from hdd-uv022 / hdd-cargo024)

Keep the object: FRESH on an identity that omitted a requested component.

Add, do not replace extra-output:

1. **Env omitted from key** (specimen-022). Recorded key fields vs payload fields.
   PYTHONEXECUTABLE changes interpreter metadata; path-only key still hits.
   Verdict: FRESH-but-env-omitted. Name the env component.

2. **Flag omitted from key** (specimen-024). `-Zpublic-dependency` toggled, identity
   unchanged, warning presence follows previous flag. Verdict: FRESH-but-flag-changed.

3. **Stub leftover** (specimen-071 / hdd-s071 transfer). Extra exists as an empty
   file written as a hashing side effect. `freshmiss` used to call this
   `FRESH-complete` because present includes the name. Record `bytes NAME 0`.
   Verdict: `FRESH-but-stub`. Missing still wins over stub.

Do not implement uv or cargo. Owned records only.

Do not merge onto main.
