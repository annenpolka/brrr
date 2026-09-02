# COMMANDS

```
# test file is on the PR; not present on failing_ref
# compiletest incremental: cfail1 then cfail2, -Znext-solver
# ./x.py test tests/incremental/track-deps-in-new-solver.rs

# equivalent shape:
rustc track-deps-in-new-solver.rs --cfg cfail1 -Znext-solver -C incremental=incr --crate-type lib
rustc track-deps-in-new-solver.rs --cfg cfail2 -Znext-solver -C incremental=incr --crate-type lib
# second session: typeck of fn poll stays green; decode of removed Error field DefId
```

Not executed on this lab host.
