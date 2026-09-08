# 次回実行に渡すプロンプト

`docs/preparation/README.md` と `docs/execplans/issue-collection-preparation.md` を読み、Issue収集基盤の次段階を進めてください。設計の正本は `brrr-issue-collection-redesign.md` です。

P0/P1の初回実装と旧151標本の保全移行は済んでいます。旧runを新しい発明実験へ直結せず、まず `python3 scripts/check_corpus.py`、`python3 scripts/corpus.py audit`、READMEにある `verify-baseline` を実行してください。設計書のT01〜T26すべてが実装済みという意味ではありません。READMEの範囲表と現行コードから続きを開始し、完了済みの保全をやり直して別コーパスを作らないでください。

次の実装対象はP2のGitHub読み取り専用収集です。固定repository一覧、独立した3検索レーン、Issue/PR別クエリ、期間区画、API version、件数・bytes・retry上限をrecipeに固定してください。既存のsource_candidates 220件は未検証の参照であり、220の独立した障害やprovider IDではありません。旧SOURCE.mdや旧TASKを原文として再登録しないでください。

実装ではT01〜T10の固定HTTP応答と故障注入を先に追加し、object保存→DB transaction→checkpointの順、再試行、lease/fencing、304キャッシュ欠損、403/404/429/timeout/不正JSON、検索打切りとライブ再走査、コメント取得不足を検証してください。未実装コマンドを成功するstubで埋めないでください。GitHub API仕様を実装する段階で公式仕様と利用可能なversionを確認し、通常テストにはネットワークを使わないでください。新規の大量収集はこれらの検証後です。

続いてP3のCase/Claim/実行証拠/関係/Exposureを実装してください。P0の手動view・原文範囲連結を、意味的な漏洩を自動で防げるシステムとは扱わないでください。修正SHAだけでローカル再現済みにしない、未知をunknownのまま残す、旧審査ラベルを新PASSにしない規則を維持してください。

P4で候補母集団と採否理由を固定し、目標24の独立Case、同一機構最大8、同一repository最大6、holdout目標6を満たす集合を作ってください。系列の連結成分で分割し、公開履歴が不明またはdiscoveryへ公開済みの系列をholdoutに入れないでください。条件不足は不足のまま記録し、上限緩和や審査の捏造で埋めないでください。

pilotの品質と意味的漏洩のPASSは、対象hashに結び付いた実際の人間の内容審査を受けて記録してください。人間の審査に出す前に、全バンドル、出典との対応、非公開の照合資料、判断に必要な不足を `inspect-view` の私的パッケージとして用意してください。審査を依頼している間も、審査結果に依存しない取得・検証・移行の作業は続けてください。

全必須検査を通過したsnapshotだけをseal/exportし、ネットワークなしの再出力とバックアップ復元後のhash一致を確認してください。Dreamerへ渡すものは公開バンドルのみです。raw corpus・旧packet・正解・収集ログ・.gitが読めない実行環境を確認できなければ `static_bundle_only` のまま記録してください。旧プロンプトのthroughput優先やFIRST_SELECTIONは、新しい公開条件や正解ポリシーを緩めません。

ここまでの準備完了とHDDの本番開始を区別してください。このプロンプト単独では夜間実験、OpenRouter課金、継続実行automationを開始しません。本番を別途指示された際は、新run ID、終了時刻、費用上限、snapshot ID、isolation levelを記録してから開始します。発明指示・R1モデル・Reality Gateの内容を収集基盤の変更と同時に再設計しないでください。

各段階の実装・検証結果と未完了事項をExecPlanに追記し、ユーザーへ「保全済み」「審査済み」「本番投入可能」を分けて報告してください。
