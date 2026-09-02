# TASK

A unified-diff hunk `@@ -2,0 +3 @@` plus `+inserted` is applied to `first\nsecond\nthird\n`. The applier reports success (exit 0), including a frozen-lockfile-style install path. The resulting bytes are not the file the hunk coordinates name.

The developer wants to know which original line the empty old-range was treated as, and why success did not mean the recorded gap.
