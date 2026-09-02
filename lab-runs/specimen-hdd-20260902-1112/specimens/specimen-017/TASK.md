# TASK

Paired completions of the same extra request `A[foo]`. Extra map is identical: `foo → B`. Pair A’s package object still lists `B` in `requires`. Pair B’s package object has an empty `requires` list. One pair’s extra dependency is in the resolved set; the other pair’s is not.

The developer wants one question that names that difference without reading both traces by hand.
