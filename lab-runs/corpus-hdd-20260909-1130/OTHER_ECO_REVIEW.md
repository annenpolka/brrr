# Other-ecosystems collect (host; not Dreamer-facing)

Recipe `github-other-ecosystems-v1` (cargo, uv, npm/cli, TypeScript). pytest excluded on purpose.
Collection `1c7ed67bec41fe0cfda7b7a66731f3d363055ea23809b61fc9875f35618e066d`
Root `.brrr-corpus/pilot-other-20260909`

Finished this recipe's runnable jobs: `NO_RUNNABLE_JOB`, complete 16, unfinished 0, reserved 225. All 16 complete roots are `rust-lang/cargo` (resource cap 16 filled before uv/npm/TS). No further resume on this collection.

Issue bodies read (not PRs):

| Issue | Quality | Why |
| --- | --- | --- |
| 16119 docs chapter | HOLD | Feature/docs checklist, no failing input. |
| 17375 patch.unused lockfile order | HOLD | Two-run cache story, but reporter cannot provide a public repro; proprietary crate. |
| 15932 lockfile features | HOLD | Feature request, example lockfile snippet is a proposal not a failure. |
| 17045 doc tests vs RUSTFLAGS | HOLD | Command + error log, but the crate sources are not in the issue. |
| 17079 miriflags | HOLD | Config feature request. |

None exported. No quality PASS. Bounded: do not raise the 16-resource cap to chase uv in this recipe.

Resume:

```
python3 scripts/corpus.py --root .brrr-corpus/pilot-other-20260909 resume \
  --collection 1c7ed67bec41fe0cfda7b7a66731f3d363055ea23809b61fc9875f35618e066d \
  --max-requests 200 --max-seconds 600
```

Selection recipe `github-other-ecosystems-v1` allows shortfall (target 3, 1 per repo, 1 per mechanism, delegated Codex). Empty corpus shortfall=3 HOLD — covered by `tests/test_other_ecosystems_recipe.py`.
