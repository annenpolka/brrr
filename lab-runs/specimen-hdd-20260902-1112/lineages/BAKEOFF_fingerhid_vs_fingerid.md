# Bakeoff: fingerhid vs fingerid

Both ground hdd-rustcfinger / specimen-086 (path+mtime fingerprint vs -vV mismatch).

| | fingerhid | fingerid |
| --- | --- | --- |
| records | two files path/mtime/vv | same |
| hidden_by_fingerprint | path== and mtime== and vv!= | same |
| first destroyer | KEEP | Honor-KILL |
| second | Honor-KILL (`DESTROYER_fingerhid_2.md`) | Honor-KILL |

Prefer neither. Same primitive. Do not merge. Do not resurrect via a third CLI.
