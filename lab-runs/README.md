# lab-runs

各HDD実験は `lab-runs/<run-id>/` に置く。`current` は最新の初期化済みrunへのsymlink。

過去run（読み取り専用アーカイブ）:

- `specimen-hdd-20260902-1112` — 9月2日の標本HDD
- `corpus-hdd-20260909-1130` — 9月9日11:30の実資料HDD（HARD_STOP済み）

候補の実装は隔離git worktreeで行い、収穫後はrun配下にworktreeを残さない。製品として残すものは `runpair/` のようにcoordinatorへ載せる。対応するDream状態は `.hdd-runs/<run-id>/`。
