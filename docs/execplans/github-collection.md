# 次回をGitHub収集から開始できるようにする

このExecPlanは進捗・判断・検証結果を追記する。

## Purpose / Big Picture

次回は収集器の実装を挟まず、固定recipeからGitHubの原文を収集できる。途中終了後はcollection IDを使って再開し、取得失敗や検索打切りを空結果と混同しない。今回、小さな実API契約確認まで済ませ、大量収集とHDDは次回に残す。

## Progress

- [x] (2026-09-08 23:48:38Z) 既存P0/P1とGitHub認証状態・公式API version仕様を確認。
- [x] (2026-09-09 00:14:10Z) recipeとplan、原文取得、HTTP記録、再開可能jobを実装。
- [x] (2026-09-09 00:14:10Z) 固定HTTP応答でT01〜T10、取得境界、復元後の再開を検証。全52テスト成功。
- [x] (2026-09-09 00:14:10Z) 実APIで1 PRを18要求で取得、refreshの18要求中14件で304を確認。両コーパスaudit成功。
- [x] (2026-09-09 00:14:10Z) 次回プロンプトをcollect開始へ更新。旧48候補と112検索区画を固定したplanを保存。

## Surprises & Discoveries

実装開始時点のCLIはオフラインのみだった。GitHub CLIは認証済みで、現在はcollect/resume/refreshだけがGETを行う。資格情報は保存しない。PR変更ファイルには独立したprovider数値IDがないため、PR IDとファイル名の複合キーを用いた。304の本文は空でも保存済み原文から取得観測を追加できることを実確認した。

GitHubのLinkは `/repos/owner/name` から `/repositories/<数値ID>` に変わる。実APIの1件/page取得で確認し、公開メタデータで確認済みのIDに限りaliasを許可した。別IDや異なるendpointは拒否する。修正後は実際の数値IDページを3要求辿り、22要求の契約確認が不足なく完了した。

## Decision Log

- Decision: HTTPは標準ライブラリ、直列GETのみ。GH_TOKEN/GITHUB_TOKEN、なければ既存gh認証をメモリ内で使う。
  Rationale: 現在の依存なしCLIを保ち、資料中の命令を実行する経路を追加しない。
  Date/Author: 2026-09-08 23:48:38Z / Codex
- Decision: refreshは全固定区画と既知資料を再走査する。
  Rationale: 初版では部分watermarkの欠落を避ける。増分最適化は後回しにし、検索に厳密な網羅性を主張しない。
  Date/Author: 2026-09-08 23:48:38Z / Codex

## Outcomes & Retrospective

今回の目的を達成。既存コーパスへ次回collectから収集を開始できる。原文取得と公開審査は別状態を維持し、HDD本番や大量取得はまだ開始していない。実APIの初回・refreshともCOMPLETE_FOR_POLICY。52テスト成功。全期間の再走査を採用し、ライブ検索の網羅、過去編集履歴、OS電源断耐久性は保証していない。

## Context and Orientation

rootは `/Users/annenpolka/ghq/github.com/annenpolka/brrr`。既存の `src/brrr_corpus/store.py` は不変objectとSQLite、`boundary.py` は未審査公開を拒否する。`.brrr-corpus` に旧151 aliasを保全済み。Sourceはprovider IDで同一資料を識別し、Revisionは保存した内容の版、Jobは一つのHTTP取得を指す。Leaseは期限付きの処理権、fencing tokenは遅れた結果の確定を拒否する世代番号。

## Plan of Work

`collection_plan.py` に収集recipe検証と固定planを置く。公開repository一覧・期間・機構/症状/対照のレーンを固定し、既存の旧URL候補もplanへ複写する。`github_http.py` はGET、ホスト検査、バイト上限、ヘッダー許可リスト、認証を担当する。

`collection.py` でjob、lease、retry時刻、キャッシュ、checkpointをSQLiteに追加する。ページの原文object保存後、一つのtransactionで資料版、取得記録、子job、ページ状態を確定する。HTTP失敗・304欠損・期間分割・取得上限・中断を明示する。CLIにplan/collect/resume/refresh/collection-statusを追加し、既存コーパスへ原文を追加できるようにする。

## Concrete Steps

rootで `python3 scripts/check_corpus.py` を実行する。実装後に次のコマンドを使う。

    python3 scripts/corpus.py plan --recipe recipes/collection/github-pilot-v1.json
    python3 scripts/corpus.py collect --recipe recipes/collection/github-pilot-v1.json
    python3 scripts/corpus.py collection-status latest
    python3 scripts/corpus.py resume --collection latest

小さな別コーパスへ実APIを数要求だけ行い、recipeのAPI versionが受理されること、原文と取得範囲が保存されることを確認する。通常テストは固定HTTP応答のみ。

## Validation and Acceptance

既存31テストを維持する。重複ページ、object後/DB後の停止、古いfencing token、編集されたコメント、304キャッシュ欠損、403/404/429/timeout/不正JSON、1000件到達/incomplete_results、ライブ再走査、コメント上限に対する結果を検証する。HTTP失敗を成功や結果0件へ変換しない。API本文の命令は保存データに留め、認証ヘッダーを保存しない。収集の再開にコード編集や新しい依存導入が不要なら今回の完了。

## Idempotence and Recovery

同じplanの初回collectは同じcollectionへ接続し、二重作成しない。resumeは生存leaseを奪わず、期限切れのleaseだけを更新する。refreshは新epochを追加し、旧revision/snapshotを変更しない。予算は要求単位で先に予約し、応答喪失後の再試行も数える。停止理由とnext_retry_atを返し、長い待機を隠してsleepしない。

## Artifacts and Notes

新しいreportは `docs/preparation/collection-readiness.md`。旧移行receiptは履歴として保持。未審査の原文やHTTP全文はGit管理外のコーパスにのみ保存する。

    initial live check: 18 requests, 1 complete resource, 16 observations, no acquisition problems
    refresh live check: 18 requests, 14 x HTTP 304, no acquisition problems
    pagination live check: 22 requests, 3 numeric repository pages, no acquisition problems
    fixed plan: 112 queries, 48 legacy seeds, 172 deferred legacy candidates
    tests: 52 passed

2026-09-09に実装結果と次回開始手順を追記した。実取得の詳細はcollection-contract-check.json、現在の検証結果はcollection-test-results.txtを参照する。

## Interfaces and Dependencies

Python標準ライブラリと既存SQLiteを使用。HTTP transportはテストで差し替え可能にする。plan/statusはネットワークへ接続せず、collect/resume/refreshのみが明示的なGETを行う。成功0、処理失敗1、取得継続・不足あり3を返す。公開は引き続き別の審査済みsnapshotからだけ行う。
