# 次回実行プロンプト — 実資料snapshotの小規模試行

2026-09-09の11:30〜翌00:00の実行は [当日の計画](../execplans/20260909-1130-hdd.md) と [開始用プロンプト](../execution/20260909-1130-start.md) を使用する。現在は計画保存済みで、自動起動は未設定。

最新の状態は `docs/preparation/evidence-pilot.md`。入力不足だった旧PR由来CaseのHOLDは維持し、原文に入力ファイルがある別Issueから1事例の品質・漏洩審査とsnapshot出力が完了しています。小さく試す場合は、そのsnapshotを再出力するところから始めてください。ユーザーはCodexへの内容審査を委任済みで、新recipeは指定エージェントの実際のPASSを受け付けます。人間の審査として記録しないでください。

以下は追加収集を行う場合の指示です。

`docs/preparation/collection-readiness.md` の収集準備が済んでいます。収集器の実装をやり直さず、既存の `.brrr-corpus` を使ってGitHub収集から開始してください。設計の正本は `docs/archive/issue-collection-redesign.md` です。

開始時に `python3 scripts/corpus.py audit` を確認し、次を実行してください。

    python3 scripts/corpus.py collect --recipe recipes/collection/github-pilot-v1.json --max-requests 200 --max-seconds 600

collection IDを記録してください。同じrecipeのcollectは既存の初回collectionを再利用します。`python3 scripts/corpus.py collection-status latest` で確認し、未完了jobがあれば `python3 scripts/corpus.py resume --collection COLLECTION_ID --max-requests 200 --max-seconds 600` で続けてください。複数collectionがある場合はlatestではなく明示IDを使ってください。

レート制限やRETRY_WAITでは `next_retry_at` を守って再開してください。FAILED_FINAL/BLOCKEDは理由を確認し、解消後にだけ `--retry-failed` を使ってください。呼び出し単位の上限と、recipeに固定した総予算を区別し、総予算は自動で増やさないでください。`FINISHED_WITH_LIMITS` で未完了jobが0なら不足を報告し、resumeを繰り返さないでください。Ctrl-C後は生存leaseを奪わず、期限後に同じIDで再開してください。

旧151標本は保全済みです。旧出典候補220 URLから今回48候補を固定し、機構・症状・対照の3レーンで公開IssueとPRを探索します。検索語、repository、期間、上限はrecipeのまま使ってください。旧SOURCE.mdやTASKを原文として格上げせず、collectorが保存したSourceRevisionとHTTP記録を使ってください。未取得や打切りを結果0件に変換しないでください。

終了時に、完了・不足・失敗・SourceObservation件数・原文の由来をreportに記録してください。`python3 scripts/corpus.py audit` を通し、新しい名前でDBとobjectをバックアップしてください。出典URLや修正SHAがあるだけでローカル再現済みとしないでください。

旧PR由来の実資料ミニパイロットは、ユーザーから委任されたCodexの内容審査で品質HOLDになっています。新しいIssue由来の確定済みsnapshotとは別です。`docs/preparation/mini-content-review.md` の不足条件を確認し、実際の失敗入力と設定・実行環境が確認できる原資料の追加収集、または別の十分な事例の選定から進めてください。修正後テストを報告時の入力とみなさないでください。内容審査はエージェントとして実施・記録でき、人間になりすましてPASSを登録しません。

少数で試す場合は `docs/preparation/mini-loop.md` を使ってください。`mini-demo` は収集から復元まで合成資料で動きます。実資料には `.brrr-corpus/mini-real/pilot` の審査パッケージがあり、Case/Claim/reprocess/selectは実装済みです。

以降は保存原文から既存のCLIでCase/Claim/Viewを整理します。品質と意味的漏洩の審査は対象hashに結び付け、実際の人間の内容審査を受ける前にhuman PASSを作らないでください。pilotの目標24事例、同一機構最大8、同一repository最大6、holdout目標6を守り、不足は不足として残してください。同じ障害・派生系列や公開履歴不明の資料を未知事例用holdoutへ流さないでください。

HDDへ渡すのは審査済みsnapshotからexportしたバンドルだけです。旧packet・正解・raw corpus・.gitをconsumerへ渡さず、OS隔離を確認できない場合はstatic_bundle_onlyと記録してください。発明指示・R1モデル・Reality Gateを収集変更と同時に再設計しないでください。

このプロンプトはGitHubの読み取り専用収集を開始する指示です。HDD本番、OpenRouter課金、継続automationは別の開始指示があるまで起動しません。追加実装が必要になった場合は `docs/execplans/github-collection.md` に進捗と理由を追記してください。
