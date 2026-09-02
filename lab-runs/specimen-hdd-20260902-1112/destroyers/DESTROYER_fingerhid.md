# DESTROYER fingerhid

Date: 2026-09-02 15:29 JST
RUN_ID: specimen-hdd-20260902-1112
Target: `lineages/candidate-fingerhid/fingerhid`

Worktree `specimen-hdd/candidate-fingerhid-fingerhid` HEAD `50a760f`. Parent `main`. cargo/rustc not invoked.

Origin: harvest `hdd-rustcfinger` / specimen-086. hidden_by_fingerprint when path and mtime match and -vV strings differ. size/birth spectators.

Tests 3/3. Demos identical. Owned fc42 vs fc40: same_path yes, same_mtime yes, vv_mismatch yes, same_size no, hidden yes, rc=1. Same vv: hidden no, rc=0.

Holes: size/birth never enter the verdict; the join is three equalities on caller-written fields. Later destroyer may KILL as THIN_WRAPPER of `path_a==path_b and mtime_a==mtime_b and vv_a!=vv_b`. This pass **KEEP** the named join on owned 086. Do not add cargo. Do not merge onto `main`.

KEEP
