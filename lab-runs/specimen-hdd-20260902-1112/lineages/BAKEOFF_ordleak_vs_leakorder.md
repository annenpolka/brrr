# Bakeoff: ordleak vs leakorder (competing reimpl)

Adversarial specimen-060: class attribute `Box.bucket`, not a module global.

| tool | PASS/FAIL split | leaked name |
| --- | --- | --- |
| ordleak | yes, exposing_order test_a test_b | `Box.bucket` into test_b `[]` vs `['a']` |
| leakorder | yes, sufficient_exposing_order test_a,test_b | **none** (module snapshot only) |

leakorder reports `leaked=none` while the status split is on the next line. Destroyer: MUTATE leakorder isolation to class attributes, or keep ordleak as the primitive.

Host capture: scratch `adversarial-ordleak-class.log`, `adversarial-leakorder-class.log`.
