# FIX

Both `acc` and `flag` are module globals mutated by test_a. Order B sees them.
A leak query that only snapshots `acc` misses `flag`.
