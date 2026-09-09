# 次回は収集から開始できる

2026-09-09 JST。GitHub収集器、再開、refresh、固定recipeを実装した。旧151標本を保全した既存の `.brrr-corpus` へ、そのまま原文を追加できる。

リポジトリrootで次を実行する。

```sh
python3 scripts/corpus.py collect \
  --recipe recipes/collection/github-pilot-v1.json \
  --max-requests 200 --max-seconds 600
```

recipeと旧出典候補をplanに固定してから収集する。collection IDは開始時にstderrへ表示する。同じplanのcollectを再実行しても同じcollectionへ接続し、確定済みページを再取得しない。

途中で要求数・時間の上限に達したら、次で状況を確認して続ける。

```sh
python3 scripts/corpus.py collection-status latest
python3 scripts/corpus.py resume --collection latest --max-requests 200 --max-seconds 600
```

`latest` はこのコーパス内の直近collection。複数の収集を扱うときは開始時のIDを指定する。`--root` はサブコマンドの前に置く。

## 最初の収集条件

| 項目 | 固定値 |
| --- | --- |
| 検索先 | pytest、cargo、uv、npm、Gradle、TypeScript、Nix、BuildKitの8 repository |
| 作成期間 | 2025-09-01以上、2026-09-09未満 |
| 検索レーン | 機構3語、症状3語、対照1語。IssueとPRを別検索、OPEN/CLOSEDとも対象 |
| 初期検索区画 | 112。各区画は終了時にもう一度走査 |
| 旧出典 | 220 URL候補からrepositoryごとの順送りで48候補を固定。残り172候補は予算による保留 |
| 採取上限 | 各レーン24 resource。旧出典・関連先を含む総上限144 |
| ページ上限 | 検索2ページ、コメント等5ページ。到達は不足として記録 |
| 要求と容量 | 全epochで最大2,000要求・256 MiB。応答単位で最大2 MiB |
| HTTP | 同時1、検索間隔2.1秒、通常間隔0.2秒、timeout30秒、lease120秒、retry最大5回 |
| 関連資料 | コメント、PRメタデータ、レビュー、行コメント、変更ファイル、timeline。固定repository集合内の明示関連を深さ1まで |
| 添付とコード | 添付リンクは記録のみ。資料内のコマンド・コードは実行しない |

対照枠はGitHub全体の無作為標本ではない。列挙したページ内を固定seedで並べ替えて上限まで採取する。pilotの採用上限は収集後の別recipeで扱う。

`collection-plan.json` は準備時に保存したplanの写し。DBのrecordが正本。API version `2026-03-10` は[公式version仕様](https://docs.github.com/en/rest/about-the-rest-api/api-versions)を確認し、実APIでも受理された。実行開始時にも `/versions` で確認する。

## 認証

`GH_TOKEN`、`GITHUB_TOKEN`、既存の `gh auth token --hostname github.com` の順に認証を選ぶ。この環境ではgh認証を使った実取得を確認済みで、追加設定なしに開始できる。トークンはメモリ内だけで使用し、DB・出力・取得ヘッダーへ保存しない。HTTPはGETのみ。公開repositoryのメタデータを確認してから資料を取得する。

別環境で認証がなければ `gh auth login` または環境変数を設定する。

## 停止理由と再開

| 状況 | 次の操作 |
| --- | --- |
| `INVOCATION_REQUEST_LIMIT` / `INVOCATION_TIME_LIMIT` | 同じcollectionをresume。呼び出し単位の上限 |
| `RATE_WAIT` / `RETRY_WAIT` | `next_retry_at` 以降にresume。早く再実行しても要求しない |
| Ctrl-C・プロセス停止 | IDでstatus確認。生存leaseを奪わず、期限後にresume |
| `FAILED_FINAL` / `BLOCKED` | 403・404・認証・不正JSON等の理由を確認。解消後だけ `resume --retry-failed` |
| `TOTAL_BUDGET_EXHAUSTED` | 総予算を自動で増やさない。必要なら新recipe・新planで別収集 |
| `FINISHED_WITH_LIMITS` / `unfinished_jobs: 0` | 処理済みだが上限による不足がある。resumeを繰り返さずreportを残す |
| `COMPLETE_FOR_POLICY` | 宣言した取得範囲の処理が終了。網羅や品質合格を意味しない |

成功はexit 0、入力エラー等は1、未完了・不足ありは3、Ctrl-Cは130。statusも不足時は3。JSONにはjob状態、要求数、resourceの不足、理由、再試行時刻が含まれる。

元資料の現在版を取り直すときだけrefreshする。

```sh
python3 scripts/corpus.py refresh --collection COLLECTION_ID --max-requests 200 --max-seconds 600
```

refreshは新epochを作り、固定期間全体と既知資料を再走査する。最大updated_atでwatermarkを進める増分方式は導入していない。検索と一覧を2回走査しprovider IDで重複排除するが、ライブ更新下の完全性は保証しない。

collectorのコードが変わったら、古いplanのjobを同じ実装としてresumeせず、新planまたはrefreshへ進む。recipe変更で既存collectionを上書きすることもない。

## 検証結果

`python3 scripts/check_corpus.py` の52テストが通過。T01〜T10の重複、停止、fencing token、コメント編集、304欠損、HTTPエラー、検索分割、再走査、コメント上限を固定HTTP応答で検証した。PR資料の分離、private repository拒否、外部ホストへのredirect拒否、ヘッダー許可リスト、予算制約も検証した。

実API確認は `github-smoke-v1.json` で公開PR `denoland/deno_lockfile#62` の1件を取得した。初回18要求で `COMPLETE_FOR_POLICY`、16 SourceObservation、取得問題0。refreshも18要求で完了し、14要求が304だった。原文revisionと取得観測を分け、キャッシュを再利用できることを確認した。[条件付き要求とレート制限の公式手順](https://docs.github.com/en/rest/using-the-rest-api/best-practices-for-using-the-rest-api)

追加のページ送り確認は22要求で完了。1件/pageの変更ファイルを使い、GitHubが返す `/repositories/<数値ID>` のページを3要求取得した。名前形式から数値ID形式へ変わるLinkは、確認済みのrepository IDに一致する場合だけ辿る。別IDや別endpointへは移動しない。

実確認データは `.brrr-corpus/contract-smoke/`。合成fixtureは一時コーパスに限定した。証跡は `collection-contract-check.json` と `collection-test-results.txt`。通常テストはネットワーク不要。大量収集のcollectionはまだ開始していない。

収集後も品質・漏洩はPENDING。次はCase/Claimの整理と表示審査であり、原文をそのままHDDへ渡さない。24事例のsnapshotとHDD本番はまだ確定・開始していない。
