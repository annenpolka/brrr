# Issue収集基盤の初回実装と旧run移行

このExecPlanは実装に合わせて Progress、Surprises & Discoveries、Decision Log、Outcomes & Retrospective を更新する。

## Purpose / Big Picture

旧実験を変更せず保存し、新しい品質・漏洩審査を通った入力だけを次回HDDへ渡せるようにする。今回の準備はP0の公開境界とP1の保全移行を完成させ、オフラインのsnapshot・復元経路を検証する。GitHub収集ジョブ、Claimの自動生成、実際の24事例の内容審査は後続工程であり、未完了のまま実験を開始しない。

## Progress

- [x] (2026-09-08 23:16:19Z) 設計書と参照コミットを確認。実装と移行確認まで行うことをユーザーが指定。
- [x] (2026-09-08 23:16:19Z) 151 packet、124 REAL_SOURCE_BACKEDを再集計。specimens直下の他2項目はSKIP文書。
- [x] (2026-09-08 23:36:46Z) 変更前hashの固定、P0負例テストを先に実行し未実装による失敗を確認。
- [x] (2026-09-08 23:36:46Z) 不変オブジェクト・SQLite・保全importを実装。
- [x] (2026-09-08 23:36:46Z) 審査hashと許可リストに基づくadapter、手動選別snapshot、バックアップを実装。
- [x] (2026-09-08 23:36:46Z) 151標本と旧HDD rootを保全。再importの追加0件、整合性・復元成功。
- [x] (2026-09-08 23:36:46Z) 次回手順、実行プロンプト、準備状況を記録。
- [x] (2026-09-09 00:14:10Z) 後続P2を実装。GitHub収集・HTTPページ再開・lease/fencing・エラーと上限処理。詳細はgithub-collection.md。
- [ ] 後続P3/P4: Case関係・証拠契約・母集団固定・24事例の実内容審査とpilot。

## Surprises & Discoveries

- Observation: packetのkindはトップレベルではなくmanifest文字列の中にある。
  Evidence: 全151 packetのkeyを列挙。manifest中のkindは旧報告の124件と一致。
- Observation: 旧runにはsymlinkがある。
  Evidence: lab側17件、HDD側currentが1件。保全ではリンク文字列を記録し、リンク先を辿らない。公開ではsymlinkを拒否する。
- Observation: 旧DestroyerのfixtureにFIFOが7件あった。
  Evidence: 初回棚卸しが未対応種別として停止した。FIFOのmodeと種別を保存する処理を追加し、読んで待ち続けることを避けた。過去の通信内容の保全は主張しない。
- Observation: macOSの一時ディレクトリ名には `/var` symlinkが含まれる。
  Evidence: symlink拒否テストが初期化時に失敗した。テスト用にOSから取得した一時rootは実体パスへ解決し、公開先のsymlink拒否は維持した。

## Decision Log

- Decision: 今回の作業はP0/P1とオフライン検証・運用準備に限定する。
  Rationale: 設計13章の順序を守り、大量取得や審査前のHDD実行を先行させない。ユーザーの「準備」と「実装と移行確認」に対応する。
  Date/Author: 2026-09-08 23:16:19Z / Codex
- Decision: Python標準ライブラリとSQLiteで開始する。
  Rationale: 既存スクリプトがPythonであり、移行を追加のサービスやパッケージ導入に依存させない。
  Date/Author: 2026-09-08 23:16:19Z / Codex

## Outcomes & Retrospective

準備のP0/P1を完了。151 alias・153 record・7,536 objectを保存し、復元先でも一致した。全11,931項目の元ファイルhash/種別/modeは不変。再取り込みは新alias 0、新revision 0。31テストが成功した。公開適格は0件で、実pilotの内容審査と収集器は未完了。全P0〜P4が完成したとは報告しない。

## Context and Orientation

作業rootは `/Users/annenpolka/ghq/github.com/annenpolka/brrr`。設計は同rootの `brrr-issue-collection-redesign.md`。HEADは `caabebcc37a699388a8a7691c055bb323916ed48`。
`lab-runs/specimen-hdd-20260902-1112` と `.hdd-runs/specimen-hdd-20260902-1112` は旧実験の不変履歴。新コードは `src/brrr_corpus`、ローカルデータは `.brrr-corpus`。オブジェクトとはSHA-256で名前を固定したバイト列、snapshotとは出力ファイルと審査対象を固定したmanifestである。

## Plan of Work

最初に旧root全体のファイル・ディレクトリ・リンク・hashを固定する。P0の負例を `tests/test_boundary.py` に置き、未審査、旧ACCEPT_R1、変更された本文・exporter、漏洩、パス脱出が出力を作れないことを確認する。

`src/brrr_corpus/store.py` に原子的オブジェクト保存とSQLiteの版付きrecordを実装する。`legacy.py` は原ファイルを解釈で置き換えず全バイト列を保全し、runと旧番号のaliasに一意制約を置く。資料候補URLと未検証の旧主張を区別し、全標本の審査をPENDING、公開履歴をunknownとする。

`boundary.py` は本文とファイル名とrecipeとexporterを同じhashへ結び、品質・意味的漏洩レビューの両PASSを必要にする。許可リストから完成させた一時ディレクトリだけを原子的に公開し、既存出力との差は拒否する。審査対象に正解識別子の照合結果を含める。これは静的バンドル境界でありconsumerのOS隔離を保証しない。

旧標本を一部、全件、再実行の順にimportし、DBとobjectの一貫したバックアップを別rootへ復元する。移行前後のhash一致、alias二重登録なし、PENDINGのまま公開0件であることを結果として保存する。

## Concrete Steps

rootで次を実行する。下のCLIはこの実装で追加するものであり、実装前は動作しない。

    python3 scripts/check_corpus.py
    python3 scripts/corpus.py verify-baseline --run lab-runs/specimen-hdd-20260902-1112 --companion .hdd-runs/specimen-hdd-20260902-1112 --baseline docs/preparation/legacy-baseline.json
    python3 scripts/corpus.py import-legacy --run lab-runs/specimen-hdd-20260902-1112 --companion .hdd-runs/specimen-hdd-20260902-1112 --dry-run
    python3 scripts/corpus.py import-legacy --run lab-runs/specimen-hdd-20260902-1112 --companion .hdd-runs/specimen-hdd-20260902-1112
    python3 scripts/corpus.py audit

再実行の `new_aliases` は0、auditの未解決参照は0。旧151件はPENDINGであり、公開可能151件とは表示しない。

## Validation and Acceptance

T14〜T19に対応した失敗系と、明示的な人間審査を持つsynthetic入力の成功系を検証する。合成データは `origin: synthetic` とテスト専用rootに限る。ファイル・名前・recipe・exporter変更時には旧PASSが使えないこと、FIRST_SELECTIONの追加が漏洩検査を無効化しないことを検査する。T16は既知の言い換えfixtureを意味的レビューがFAILと判定した場合に停止するテストであり、未知の漏洩を自動判定できるという意味ではない。

保全については同じrunを2回取り込んでもalias/同一revisionが増えず、オブジェクト確定後DB確定前の故障から再試行できることを検証する。旧runは全内容hashが一致し、バックアップから全参照を解決できることを確認する。確定した合成snapshotはネットワークなしで同一のファイル名・バイト列へ再出力する。

## Idempotence and Recovery

不変オブジェクト保存後にDBをtransactionで更新する。DB確定に失敗した孤立objectは残して再利用する。旧ファイルやobjectを削除してやり直さない。新しい旧run内容は別revisionにする。審査とsnapshotは追記し、確定manifestを変更しない。公開先が異なる内容なら上書きしない。バックアップはSQLite backup APIと参照objectを一つのディレクトリに完成させてから公開する。

## Artifacts and Notes

変更前の棚卸し、移行receipt、準備reportを `docs/preparation` に置く。第三者の全文・旧生成物・DB・バックアップはGit管理外の `.brrr-corpus` に置く。設計書自体はユーザー作成の未追跡ファイルなので編集しない。

    audit: ok=true, objects=7536, records=153, aliases=151, errors=[]
    import-repeat: new_aliases=0, new_revisions=0, publication_eligible=0
    verify-baseline: ok=true, packet_count=151
    restore: ok=true, objects=7536, records=153, aliases=151
    readiness: shortfall=24, ready_for_hdd=false, exit=3

この計画は2026-09-09 JSTに、実際の保全と検証結果、FIFO対応、後続実装の範囲を反映して更新した。

## Interfaces and Dependencies

CLI入口は `python3 scripts/corpus.py`。成功はJSONとexit 0、失敗は理由付きJSONと非0。標準ライブラリの `sqlite3`、`hashlib`、`json`、`pathlib`、`tempfile` を使用する。スキーマは版番号、許可キー、列挙値、hash、パス制約をコードで厳密に検証する。collect/resume/refresh等の未実装コマンドは存在すると称さない。
