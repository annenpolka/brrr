# TASK

A Hypothesis checkout sits at a11ec6f2ba4c1d08df6e355730d2a25d317492db (hypothesis 6.47.0 class).

A `@given` test fails on a dict whose iteration order is not sorted by key. The pytest assertion shows one order. The Hypothesis “Falsifying example” block prints another. Copying that printed example into `@example()` makes the test pass.

Python 3.7+ dicts preserve insertion order. The test under study depends on that order.

Outcome sought: why the printed failing input is not the input that failed, and what would make a reported example a faithful reproduction.
