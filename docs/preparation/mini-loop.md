# 小さく一巡する収集・再利用の手順

2026-09-09。合成3事例なら、収集の中断・再開→保存原文の検索→Case/Claim→View→fixture審査→2種類の選別→snapshot→オフライン再出力→バックアップ復元まで、1コマンドで試せる。実資料は2件のPRから1事例・2種類のViewを準備済みで、人間の審査から続けられる。

追加の委任レビューを [内容審査結果](mini-content-review.md) に記録した。実資料v1/v2は内容漏洩の混入を認めなかったが、失敗入力・環境が不足して品質HOLD。次回は原資料の補完から進める。

## まず合成3事例で試す

repository rootで実行する。Python標準ライブラリのみを使い、ネットワークもモデル呼び出しも発生しない。

```sh
python3 scripts/corpus.py mini-demo --output .brrr-corpus/mini-demo
```

出力の `collection_state: COMPLETE_FOR_POLICY`、`searchable_sources: 3`、`human_reviews: 0`、`offline_restore_and_export_verified: true` を確認する。同じコマンドの2回目は保存済みsnapshotを再出力し、同一ファイル集合・hashを検証して `reused: true` を返す。コードやrecipeが変わった後は別のoutput名を指定する。

`mini-demo/` の中身は次のとおり。

| 場所 | 内容 |
| --- | --- |
| `report.json` | collection、Case、View、selection、snapshotのIDと検証結果 |
| `corpus/` | 合成原文・取得応答・中断再開履歴・Case・Claim・審査・選別 |
| `review-1/`〜`review-3/` | 審査前のプレビューと根拠、PENDINGテンプレート |
| `selection-two.json`, `selection-one.json` | 全候補・採否理由・レビューID・選別recipe |
| `export-two/`, `export-one/` | 2事例と1事例の確定bundle |
| `backup/`, `restored/` | DBとobjectのバックアップ・復元 |
| `export-two-restored/`, `export-one-restored/` | 復元からの同一バイト列の出力 |

3事例のうちB/Cは同じ障害として束ね、A/Bの「同機構」関係だけでは束ねない。2事例の選別はdiscoveryとholdoutを各1件選ぶ。別の問いへ再加工したViewは旧PASSを継承せずPENDINGに戻る。審査者は明示的な `fixture` で、人間の審査と記録しない。

## 保存済み資料を操作する

合成demoを使って、IDを読みながら各コマンドを試せる。

```sh
python3 scripts/corpus.py --root .brrr-corpus/mini-demo/corpus sources --query 'SYNTHETIC REPORT'
python3 scripts/corpus.py --root .brrr-corpus/mini-demo/corpus list-cases
python3 scripts/corpus.py --root .brrr-corpus/mini-demo/corpus select --recipe recipes/selection/mini-one-v1.json
```

`show-source SOURCE_REVISION` は原文全文、providerメタデータ、取得時刻、生HTTPのobject hashとJSON Pointerを表示する。`sources` は `--repository owner/repo --kind issue --origin real --limit 50` で絞れる。保存済みの全revisionが対象で、最新や網羅性を推測しない。URLのないPR patchも保存されたPRのprovider IDからrepository検索に含める。

以下は新しい事例を作る操作経路。JSONの契約は [schemas/README.md](../../schemas/README.md) を参照する。Case keyは同じUUIDへ対応し、内容変更は新revisionになる。

```sh
python3 scripts/corpus.py --root CORPUS save-case --file case.json
python3 scripts/corpus.py --root CORPUS add-claim --file claim.json
python3 scripts/corpus.py --root CORPUS relate-case --file relation.json
python3 scripts/corpus.py --root CORPUS reprocess --config reprocess.json --recipe view-recipe.json
python3 scripts/corpus.py --root CORPUS inspect-view VIEW_ID --output PRIVATE_REVIEW_DIRECTORY
python3 scripts/corpus.py --root CORPUS select --recipe selection-recipe.json
python3 scripts/corpus.py --root CORPUS inspect-selection SELECTION_ID
```

選別recipeとView recipeを分けている。同じView recipeの範囲で候補数・上限・seedを変える選別は、同じ審査済み本文を使える。本文・Case・Claim・pipelineを変えた場合は別Viewになり、再審査が必要。

選別は一致するView候補すべてを固定し、旧Case版・審査待ち・同障害group・件数上限・公開履歴などの除外理由を保存する。`select` が `HOLD` を返すとexit 3。人間の審査後にもう一度selectし、新しい選別IDを確定する。旧PENDING選別の記録は変えない。

## 実資料1事例を審査して試す

取得済みのrootは `.brrr-corpus/mini-real`。PR 2件とも取得方針内で完了し、14 SourceRevision・24 SourceObservationを保存した。35 HTTPリクエストを使用。検索は資源数上限で2jobがPARTIALであり、collection全体は `INCOMPLETE / FINISHED_WITH_LIMITS`。全検索が完了したとは扱わない。

collection ID: `57484923f00d8b277b89f6319010a7cb28c2c657318244f2823f2035efce9405`

```sh
python3 scripts/corpus.py --root .brrr-corpus/mini-real collection-status 57484923f00d8b277b89f6319010a7cb28c2c657318244f2823f2035efce9405
python3 scripts/corpus.py --root .brrr-corpus/mini-real sources --query lockfile
```

次のパッケージを用意してある。`public/` は未審査プレビューで、consumer用の出力ではない。

- `.brrr-corpus/mini-real/pilot/review-v1/`: エラー中の依存項目を絞り込む問い。
- `.brrr-corpus/mini-real/pilot/review-v2/`: コマンド実行前後で比較すべき情報を尋ねる問い。
- `.brrr-corpus/mini-real/pilot/inputs/`: 再加工config、recipe、選別理由、結果ID。

同じ原文のエラーブロック `[81,304)` バイトを引用し、修正PRへのリンクと効果の説明は除外した。2つのViewは同じCaseであり、独立した2事例とは数えない。実行環境・再現手順の不足も審査対象。ローカル再現済みとは記録していない。

審査者が全文・原文の引用範囲・修正情報を読んだ後、`review-quality.PENDING.json` と `review-leakage.PENDING.json` をパッケージ外へコピーする。自身の名前、判断、理由、実際に確認した項目を記録する。PASSは3つのattestationがすべてtrueの場合のみ。HOLDやFAILを選ぶ場合も、その理由を記録できる。元パッケージは変更せず保存する。

```sh
python3 scripts/corpus.py --root .brrr-corpus/mini-real record-review --file QUALITY_REVIEW_COPY.json
python3 scripts/corpus.py --root .brrr-corpus/mini-real record-review --file LEAKAGE_REVIEW_COPY.json
python3 scripts/corpus.py --root .brrr-corpus/mini-real select --recipe recipes/selection/mini-real-v1.json
python3 scripts/corpus.py --root .brrr-corpus/mini-real seal-selection NEW_SELECTION_ID
python3 scripts/corpus.py --root .brrr-corpus/mini-real export SNAPSHOT_ID --output .brrr-corpus/mini-real/exports/trial-v1
```

v2を選ぶ場合はそのViewを個別に審査し、`mini-real-v2.json` を使う。公開履歴は実際にconsumerへ渡した時に記録する。

```sh
python3 scripts/corpus.py --root .brrr-corpus/mini-real record-exposure SNAPSHOT_ID --consumer ACTUAL_RUN_ID --scope mini-real-trial --split discovery
```

新しいチェックアウトでは全文はGitに含まれないため、まず小規模recipeで取得し、準備スクリプトを実行する。このスクリプトは既知のPR例専用で、原文やrevision数が変われば止まる。

```sh
python3 scripts/corpus.py --root .brrr-corpus/mini-real collect --recipe recipes/collection/mini-reuse-sources-v1.json --max-requests 55 --max-seconds 120
python3 scripts/prepare_mini_real.py --root .brrr-corpus/mini-real --output .brrr-corpus/mini-real/pilot
```

新しい条件での収集は [collection-readiness.md](collection-readiness.md) を使う。総予算は自動で増やさず、範囲の不足はreportへ残す。

## この試行の範囲

新しいCase/Claim経由のViewは `seal-selection` を必須にし、関係判定を手動sealで飛ばせない。人間の関係登録に基づく連結成分を使い、意味から自動で同障害を推定する機能はない。splitは再加工configで明示し、同groupを重複選別しない。6/24件のholdout自動配分は未対応。

新しい選別ではexperiment scopeごとに、記録済みdiscovery exposureをholdoutから除外する。unknownはholdoutに入れない。旧manual viewの公開履歴判定は従来の保守的な全scope判定を維持する。Caseまたは関係の更新は、現在はコーパス全体のgraph比較により既存選別の再作成を要求する。

検索は全revisionの逐次走査で、小規模な利用を対象とする。DB追加テーブルの旧rootへの導入と現行コードでの復元を検証した。古いpipeline/exporterの自動実行環境、実コード再現runner、意味的漏洩の自動審査、24事例の本番pilot、OSによるconsumer隔離は今回のgoalに含めていない。原文コマンド・外部モデル・HDD本番は起動しない。
