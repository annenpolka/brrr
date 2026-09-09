# コーパス再利用を小さく一巡できるようにする

このExecPlanは進捗・判断・検証結果を継続して更新する。

## Purpose / Big Picture

保存資料をCLIで検索し、Caseにまとめ、根拠付きClaimからViewを作り、別recipeで選び直し、審査済みsnapshotを出力・復元できるようにする。合成3事例では全工程を自動実行でき、実資料では人間が審査するための具体的なパッケージを用意する。人間の実審査を捏造して実資料を公開しない。

## Progress

- [x] (2026-09-09 00:47:30Z) goalを設定し、既存のCLI・公開境界・実資料を確認。
- [x] (2026-09-09 01:14:50Z) 資料検索と表示、Case/Claim/関係の登録と版管理。
- [x] (2026-09-09 01:14:50Z) 根拠からの再加工、審査待ちパッケージの作成。
- [x] (2026-09-09 01:14:50Z) 母集団と採否理由を固定する選別、系列分割、snapshotへの接続。
- [x] (2026-09-09 01:14:50Z) 合成3事例で2種類のrecipe、再出力、バックアップ復元を検証。
- [x] (2026-09-09 01:14:50Z) 実資料の小規模パイロットと操作手順を作成。

- [x] (2026-09-09 01:33:43Z) 追加収集で具体的な報告入力を持つ別事例を選定し、明示的な委任審査から実snapshotの出力・復元まで検証。72テスト成功。

## Surprises & Discoveries

既存のdeno_lockfile PR 62は本文が空。取得済みの非空本文は原因・修正説明とpatchなので、盲検の症状入力として無条件に流用できない。関連するconsumer PR 30998を追加取得し、元本文からエラーブロックのUTF-8範囲 [81,304) を確認した。

35実HTTPリクエストで2 PRは方針内の取得完了。検索2jobは資源上限でPARTIALなのでcollection全体のINCOMPLETEを維持した。PR変更ファイルにはURLがなく、最初のreview候補から漏れていた。保存済みPRのprovider IDで関連を解決し、4 patchを審査対象に含め、repository検索の回帰テストを追加した。

## Decision Log

- Decision: 再加工は保存済み原文範囲と明示的な問いの決定的な組み立てから始める。
  Rationale: LLM料金や再現性に依存せず、同じ原文の別表示を試せる。生成器・入力版・出力hashを残す。
  Date/Author: 2026-09-09 00:47:30Z / Codex
- Decision: 合成demoの審査はfixtureとして記録し、humanとは記録しない。
  Rationale: 全工程の試行を可能にしつつ、実資料の人間審査を迂回しない。fixture PASSは合成由来かつsyntheticを許可したrecipeだけで有効。
  Date/Author: 2026-09-09 00:47:30Z / Codex
- Decision: 表示recipeと選別recipeを分ける。
  Rationale: 既存の内容審査は表示・公開条件へ結合したまま、同じ審査済みViewを別の選別条件で使える。選別条件と採否理由は別recordへ固定する。
  Date/Author: 2026-09-09 00:47:30Z / Codex

- Decision: 新しいderivation付きViewにはseal-selectionを必須とする。
  Rationale: Case関係による同障害groupやscopeを、従来の手動sealで迂回しないため。
  Date/Author: 2026-09-09 01:14:50Z / Codex
- Decision: splitは再加工configで明示し、連結groupから最大1件を選ぶ。
  Rationale: 小規模試行でdiscovery/holdoutの分離を検証し、6/24件の自動配分とは区別する。
  Date/Author: 2026-09-09 01:14:50Z / Codex

- Decision: ユーザーが内容審査を委任したため、新recipeで名前を指定したagentの実審査を受け付ける。
  Rationale: humanへのなりすましを避け、品質・漏洩・hashの条件を維持して委任を実行する。委任なしの旧recipeは変更しない。
  Date/Author: 2026-09-09 01:33:43Z / Codex
- Decision: 原文を再掲するPRの症状範囲と、その前後の修正説明をClaimで分ける。
  Rationale: 元Issueに根拠を持つエラーの過剰削除を避け、修正説明は制限対象のまま保つ。公開原文は元Issueのみ。
  Date/Author: 2026-09-09 01:33:43Z / Codex

## Outcomes & Retrospective

最新の追加実行では6 root・46 SourceRevision・82 SourceObservationを取得し、具体的な2入力ファイルを持つ別Caseを委任審査した。品質・漏洩ともagent PASS、discovery 1事例のsnapshotを確定。6ファイルの再出力・別root復元をネットワーク禁止下で確認した。詳細は `docs/preparation/evidence-pilot.md` とreceipt。以前の原資料不足HOLDは保全している。

初回の結果: 少数で一巡できる操作経路を実装・検証済み。68テスト成功。合成3事例から2種類の選別とsnapshotを作成し、ネットワーク禁止下の再実行・復元・同一バイト列再出力を確認した。実APIでは2 PR / 14 SourceRevision / 24 SourceObservationを保存し、1事例の2 ViewをPENDINGで用意した。修正情報も含む各48ファイルの審査パッケージは、別rootへの復元から同じ内容で再生成できた。未審査のSelectionRunはHOLDで公開を拒否する。旧151標本のtrees_hashは基準と一致し、既存コーパスはobjects 7,536 / records 155 / aliases 151、audit成功。24事例の本番審査、増分収集の最適化、再現ランナー、全旧版の互換実行環境は完了条件に含めない。

## Context and Orientation

rootは `/Users/annenpolka/ghq/github.com/annenpolka/brrr`。`src/brrr_corpus/store.py` は不変objectとrecord、`boundary.py` は審査済みViewの出力、`collection.py` はGitHub収集を担う。Caseは一つの調査事例、Claimは原文範囲へ結び付いた発言、Viewはその組み合わせを表示した入力、SelectionRunは候補全体と採否理由の固定記録。

## Plan of Work

`catalog.py` に保存原文の検索と内容・取得根拠表示を実装する。`cases.py` にstable keyでのCase更新、Claim、版付き関係、View再加工を置く。原文の修正、原因説明、審査状態を混同せず、制限されたClaimは盲検Viewへ流さない。

`selection.py` に候補母集団の固定、品質・漏洩審査、分類上限、系列の連結、公開履歴、採否理由を実装する。同機構だけの関係は別事例として保ち、同一障害・派生・重複疑いは保守的に同じgroupへ束ねる。古いCase版や審査変更、関係変更で選別結果を流用しない。

CLIをつなぎ、`mini-demo` が合成3事例から2つのsnapshotと復元検証まで進むようにする。実資料には別の小さなrecipeを使い、生成済みViewと審査ファイルを用意する。実資料の公開はrecipeで許可した審査者の実際の品質・漏洩PASSを必要とする。ユーザーの後続委任に対応し、指定agentの審査を新recipeで明示できる。

## Concrete Steps

rootで次を実行する。新コマンドはこの実装で追加する。

    python3 scripts/check_corpus.py
    python3 scripts/corpus.py mini-demo --output .brrr-corpus/mini-demo-v2
    python3 scripts/corpus.py --root .brrr-corpus/mini-real sources --query lockfile

成功するdemoは合成資料だけを使い、2つの採否記録とsnapshot、同一バイト列の再出力、復元後のaudit成功を報告する。

## Validation and Acceptance

Case再登録の一意性、旧版の不変性、ClaimのUTF-8範囲、別Caseの根拠流用拒否、制限されたClaimの拒否、再加工による旧PASS失効、全候補の採否理由、関係の連結成分、同機構の非統合、review/exposure変更後の停止を検証する。ネットワークを無効にしてdemoの再出力と復元を確認する。

実資料では原文・引用範囲・非公開の修正情報・具体的な問いを人間が確認でき、PENDINGのままsealが拒否されることを確認する。人間の操作後に続けるコマンドを明記する。

## Idempotence and Recovery

Case keyはUUIDへ一意に対応し、変更は新revisionとなる。Claim・再加工・選別は内容hashで再利用する。Caseや関係の更新は追記し、確定snapshotを上書きしない。既存のバックアップ・復元を使い、試行用rootを明示する。合成demoは実コーパスへ混ぜない。

## Artifacts and Notes

ユーザー向け手順は `docs/preparation/mini-loop.md`、集計receiptは `docs/preparation/mini-loop-receipt.json`。実行用合成demoは `.brrr-corpus/mini-demo-v2`、実資料の審査パッケージは `.brrr-corpus/mini-real/pilot`。実資料の全文・審査待ち成果はGit管理外の `.brrr-corpus/mini-real`。コード・recipe・合成fixture・集計のみをGit管理する。

## Interfaces and Dependencies

Python標準ライブラリのみ。既存のSQLiteへ追加テーブルを作り、既存recordを変更しない。新CLIはsources/show-source/save-case/list-cases/show-case/relate-case/add-claim/reprocess/select/inspect-selection/seal-selection/mini-demo。検索・再加工・選別・出力はオフラインで動作する。
