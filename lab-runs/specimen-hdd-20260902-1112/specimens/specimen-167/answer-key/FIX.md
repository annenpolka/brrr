KNOWN FIX (sealed): swc-project/swc PR 12166 squash c0b6f12fe4c3b1d0235a64496560941751e21bd8.

failing_ref is parent c5235516340959f703c02d91a79ba40df897eb9c.

GlobalPassOption::build Map arm keyed the process-wide DashMap by self.vars and omitted the configured envs map. Second compile with different envs HIT leftover replacements.

PR repair: build the cache key from the configured environment map and sort entries.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
