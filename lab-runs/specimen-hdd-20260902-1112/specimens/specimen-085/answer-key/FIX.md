KNOWN FIX (sealed): pnpm/pnpm#10911 stores selector → hash string in the lockfile. Readers must treat a string entry as the hash, not `entry.hash` on an object. isolate-package#202 reads string-or-object. Empty hash is a third identity (mismatch), omitted is a fourth.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
