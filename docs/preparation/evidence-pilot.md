# 実資料1事例の審査・出力まで完了

2026-09-09。以前のPR 30998由来の資料は、失敗入力が不足するため品質HOLDを維持した。新たに原文の入力ファイル・版・連続実行の結果が揃う [Deno Issue 32113](https://github.com/denoland/deno/issues/32113) を取得し、ユーザーから委任されたCodexが品質・内容漏洩を審査した。**報告資料から調査する小規模なdiscovery用途で両方PASS、1事例のsnapshotを確定・出力済み。**

## 次回の入口

取得と審査をやり直さず、次で確定済み入力を再出力できる。

```sh
python3 scripts/corpus.py --root .brrr-corpus/mini-followup export \
  bd49baaa36b6999fdf9e44cf38da470c57c5f9daa6ce291e89c9084c3cce5a81 \
  --output .brrr-corpus/mini-followup/exports/reported-discovery-v1
```

同じディレクトリへの再出力はファイル集合とバイト列の一致を確認して再利用する。実体は `discovery/input-001/` 配下の `TASK.md, OBSERVED.md, COMMANDS.md, seed.md, files/package.json, files/a.js`。コードファイルは原文からの引用で、実行していない。

機械可読のID・hash・集計は [evidence-pilot-receipt.json](evidence-pilot-receipt.json)。詳細な委任審査はGit管理外の `.brrr-corpus/mini-followup/approved-review/review-audit.json` と同ディレクトリの品質・漏洩reviewに保存した。審査前パッケージは `pilot/review/` に保全している。

## 追加収集と選定

3件のGitHub検索を行い、16件の候補を取得した。元の `Invalid jsr dependency` に一致するIssueはこの検索では0件。検索条件外も含めた不存在は主張しない。原文・検索応答・候補判断は `.brrr-corpus/discovery-20260909` に保存した。

候補32113にはDeno 2.6.8、package.jsonとa.js、同じコマンドの初回出力と2回目のエラーが本文に揃う。候補35901も取得したが、今回の1事例試行では未選定・未審査として保存している。他の検索候補も資源配分上の保留であり、品質不合格とはしていない。

`recipes/collection/mini-evidence-v1.json` で2 Issueと関連する4 PRを取得。64リクエスト、46 SourceRevision、82 SourceObservation、6 rootが取得方針内で完了し、collectionは `COMPLETE_FOR_POLICY`、未完了job 0。検索期間外でも明示seedと関連資料は対象になる。相対的なIssue番号だけの参照や方針外の深さを含む全リンクの取得を意味しない。

新規rootで再取得する場合の入口は次のとおり。準備スクリプトは今回確認した原文構造を前提とする具体例で、原文や版数が変われば自動的に旧審査を適用せず停止する。

```sh
python3 scripts/corpus.py --root NEW_CORPUS collect \
  --recipe recipes/collection/mini-evidence-v1.json --max-requests 80 --max-seconds 120
python3 scripts/prepare_evidence_pilot.py --root NEW_CORPUS --output NEW_PRIVATE_PACKAGE
```

このスクリプトは原文からClaim/Viewを作ってPENDINGで止まり、PASSを自動登録しない。

## 品質・漏洩の判断

| 観点 | 結果と限界 |
| --- | --- |
| 入力の根拠 | 原文の2ファイルをバイト範囲でそのまま抽出。修正後テストを入力にしていない |
| 実行条件 | 報告されたDeno版、同じコマンドの連続実行、出力差がある |
| 残る不足 | 生成されたlockfile、未固定のJSR importの解決版、作業ディレクトリ全体、cache、OS/build詳細は未提供と明示 |
| 品質PASSの範囲 | 具体的な報告入力を検討するdiscovery用途。完全な再現benchmarkの認定ではない |
| 漏洩レビュー | 公開6ファイル、関連45原文、patch・レビュー・修正説明を読んで照合。修正方法・原因断定・修正識別子・追加テストの混入なし |
| 個人の環境情報 | 原文の絶対パスは明示したplaceholderへ置換し、元のパスは非公開の保存原文に残す |
| 独立性 | 作成と審査は同じCodexタスク。独立した第二審査や人間の審査とは記録しない |

PR 33243の2表現には元Issueと同じ診断文が引用されていた。修正説明の前後をrestricted Claimにし、その間の原文と一致する症状範囲を別分類として記録した。公開は元Issueの範囲だけを参照する。全PRを無条件に公開したり、完全一致scanを解除したりしていない。PRに再掲されたという理由だけで、元の観測ログを削除することも避けている。

旧資料のHOLDは維持し、新Caseを同一障害として統合しない。今回のPASSは、具体的な入力の有無による判断であり、審査者の条件を変えて旧HOLDを通したものではない。

## 委任審査の契約

ユーザーの「品質・漏洩審査も任せる」に対応し、新recipeのView policyに `delegated_review: {reviewer, authorization}` を明記した。指定された名前のエージェントだけがそのViewへPASSを記録でき、reviewer_typeは常にagent。委任を持たない既存recipeは従来の条件を保つ。

品質・漏洩の両方のPASS、3つのattestation、本文・根拠・policyのhash、系列・公開履歴の検証は必要。委任自体をPASSとは扱わない。これは委任を記録する運用契約であり、CLI操作者を認証する機構ではない。

公開境界コードの変更で、以前のexporterに結び付いたViewは旧版となる。保存済み本文や審査を書き換えず、新しい合成demoは以下に用意した。旧demoの出力はそのまま残る。

```sh
python3 scripts/corpus.py mini-demo --output .brrr-corpus/mini-demo-v2
```

## 検証と次の範囲

72テスト成功。委任なし・別名エージェントのPASS拒否、片方の審査だけでは確定できないこと、attestation欠落、委任変更による再審査、HOLDへの変更後の出力停止を検証した。実snapshotはネットワーク禁止下の再出力と、別rootへ復元した後の6ファイルのhashが一致した。

バックアップは `.brrr-corpus-backups/mini-followup-20260909`、復元は `.brrr-corpus-restored/mini-followup-20260909`。原資料・DB・公開bundleの全文はGit管理外。これらを別環境へ移す場合はバックアップを用いる。

次に試せるのは確定済み入力を用いる1事例のHDD。実験開始時にモデル・費用・新run ID・consumerに見せる範囲を決める。`static_bundle_only` はOS/ネットワーク隔離を保証せず、特徴的な原文からの外部検索も防がない。Deno障害のローカル再現、外部モデル呼び出し、24事例の本番実験は今回開始していない。
