# Host 実機 index (not Dreamer-facing)

| Case | Result | Consumer |
| --- | --- | --- |
| Deno 32113 public files | Deno 2.8.1: run1 foo+deno.lock rc0; run2 '@.' rc1 | discovery only; not 未知holdout |
| pytest#14011 | 9.0.1 both tests fail (variable None) | HOLD no View |
| pytest#14591 | 9.0.3 4 pass; 9.1.0 duplicate parametrization | HOLD no View |
| pytest#13479 | 8.4.1+freezegun: fixture ff not found | HOLD no View |
| pytest#13885 | 8.4.1 and 9.0.1: autouse assert 0 under skipIf | HOLD no View |

HOLD is not converted to PASS. These bytes stay off the Dreamer channel.
