# Operator schedule (deadlines, not wait-to-start)

Experiment window: **2026-09-09 17:30 JST → 2026-09-10 09:00 JST**
Start is a not-before gate. Hard end is not extended if start is late.
Actual start: **2026-09-09 17:30:01 JST**

| Time (JST) | Target | Main activity |
| --- | --- | --- |
| 19:49 | First packet + first Dream | Public bundle → trial → Dream → Red Pen |
| 22:09 | Persistent Red Pen + harvest | Same world, not a reset |
| 00:28 | First selection | KEEP/MUTATE/KILL when materials exist; may be earlier |
| 04:21 | Counterexample | Mature candidates get a 反証 pass |
| 06:40 | Broad exploration ends | No new 広い探索 after this deadline |
| 07:27 | Final jury materials | 0–2 items allowed |
| 08:00 | 保全 | No new wide exploration. Save 採否/費用/hash/再実行 |
| 09:00 | HARD STOP | This run's hdd.py/dream.sh only. Not 9/2, not lab-hdd/, not 1130 |

Preservation start: **2026-09-10 08:00:00 JST**. Hard end: **2026-09-10 09:00:00 JST**. hard_end_extended: no.

Vacant inference slots take the next ready collect/review/reconstitute/refute/implement job. Do not sleep on a clock milestone after 17:30.
