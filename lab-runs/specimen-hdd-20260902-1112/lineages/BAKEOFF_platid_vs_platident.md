# Bakeoff: platid vs platident

Both ground hdd-s074 (materialized install identity vs setup lookup).

| | platid | platident |
| --- | --- | --- |
| records | two files name/version/platform | one file install_id/lookup_id/exits |
| hidden_by_exit0 | yes (after mutate) | yes (KEEP) |
| rc on miss | 1 | (KEEP record) |
| destroyer | MUTATE then fields added | KEEP |

Keep both disagreement on disk. Prefer platident for the harvest object
(`hidden_by_exit0`) until a later destroyer of platident. Do not merge.

Update 2026-09-02 15:06 JST: DESTROYER_platident_2 Honor-KILL; DESTROYER_platid_2
Honor-KILL. Both fossils. Same primitive (string inequality + default-true
flags). Do not resurrect via frozenplat R1.
