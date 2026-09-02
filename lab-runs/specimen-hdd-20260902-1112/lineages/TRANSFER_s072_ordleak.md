# Transfer: hdd-s072 onto ordleak / leakorder

Date: 2026-09-02

`run_orders_extra.py` nests `test_a` / `test_b` inside `run()`. leakorder
discovery looks for module-level tests:

```
order test_a,test_b  test_a=MISSING test_b=MISSING  leaked=none
leaked_names  none
```

ordleak wants `FILE LEFT RIGHT` of importable test objects. Nested functions
are not that.

The extra leaked object is module-global `flag` plus `acc`. First-selection
ordleak already names class/module leaks on importable tests. This packet is
a pairing runner, not that shape.

Result: TRANSFER FAIL on these CLIs as-is. Keep as R1 seed `hdd-s072` rather
than a third leak binary.
