# TASK

Paired runs of the same two tests. Besides the leaked `acc` list from specimen-009,
test_a also sets an extra module global `flag = True`. test_b asserts `acc == []`
and `flag is False`. Pair A (`test_b` then `test_a`) PASS. Pair B (`test_a` then
`test_b`) FAIL. Same files. Only order changes.

The developer wants one question that names both leaked objects without reading
both traces by hand.
