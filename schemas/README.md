# Corpus v1 の契約

初版はPython標準ライブラリのみで動作する。ここで示すJSONの必須キー・列挙値・不明キー拒否は `src/brrr_corpus/boundary.py` と `cli.py` が実行時に検証する。JSON Schemaライブラリによる検証や未実装のP2/P3 schemaが存在するとは扱わない。

保存用recordは `serialization_version: 1, kind, payload, blobs, records` のenvelope。UTF-8、JSON key順序固定、空白なし、末尾LFで直列化し、SHA-256をIDにする。`blobs` と `records` は重複を除いて整列する。snapshot IDもこのcanonical manifest envelopeのhash。可変のSEALED/REVOKEDイベントはhash外。原文は直列化せず、受け取ったバイト列のまま別objectに保存する。

## 公開するviewの入力

`stage-view --spec` の必須キーは `schema_version, origin, case_id, lineage_group, repository, primary_mechanism, split, exposure, mode, artifacts, restricted_blobs, forbidden_identifiers`。`origin` は `real|synthetic`、`split` は `discovery|holdout`、`exposure` は `unknown|unexposed|discovery`、`mode` は `blind_problem` のみ。未知の由来、旧要約、縮約fixtureの格上げはP0で拒否する。`unexposed` は内容審査が確認する運用上の申告であり、収集器が未知性を証明した値ではない。

artifactは `path, segments` を持つ。pathは `TASK.md, OBSERVED.md, COMMANDS.md, TREE.txt` または `files/` 以下の許可名。最初の3ファイルは必須。segmentsは次のどちらか。

    {"kind":"reporter_observation","source_revision":"<ID>","start":0,"end":42}
    {"kind":"generated_prompt","text":"調査で何を観測したいかという問い"}

範囲はSourceRevisionの `body_blob` に対するUTF-8バイト範囲 `[start,end)`。元資料のバイト列をそのまま連結するので、根拠のない言い換えを観測として追加できない。UTF-8の文字途中の切断を拒否する。`generated_prompt` に事実や答えを紛れ込ませていないかは人間が審査する。P0は `local_observation` や `source_fact`、実行済み表示をまだ受け付けない。

`restricted_blobs` は照合対象の正解・評価資料objectのhash一覧。`forbidden_identifiers` は修正SHA・URL・テスト名などの非公開識別子。空の一覧で十分かも人間の内容審査対象であり、空なら正解が存在しないという意味ではない。初版の照合は40文字以上の行、SHA、URL、`test_` 識別子、明示識別子。未知の意味的漏洩の自動検出器ではない。

## 原文の手動取り込み

`import-source --file --metadata` は、操作者が別途取得した原文テキストを保全する。HTTP取得・完全取得・過去版の検証を行ったとは記録しない。metadataの必須キーは `schema_version, provider, resource_kind, provider_id, url, observed_at, provider_created_at, provider_updated_at, content_available_at, origin`。日時はタイムゾーン付きISO-8601、未確認のprovider日時・過去時点はnull。provider IDは実際のIDを指定し、URLから捏造しない。

Sourceはprovider/資料種別/provider IDの組を一意キーとしてUUIDで登録する。原文やproviderメタデータが変われば別SourceRevision、取得時刻だけが変われば同じrevisionに別観測を追加する。全て `acquisition: operator_supplied`。旧packetと旧SOURCE.mdはこの経路へ自動投入しない。

追加したGitHub collectorは `acquisition: github_http` を記録する。生HTTP応答はFetchAttemptのraw_blob、資料単体のcanonical JSONはresource_blob、APIのbody文字列をUTF-8抽出したものはbody_blobとして別々に保全する。SourceObservationは原文応答内のJSON Pointer、抽出フィールド、取得時刻を結ぶ。コメント編集は新revision、同内容の再取得は別観測。PR変更ファイルには独立の数値IDがないため、provider IDはGitHubのPR IDとファイル名からなる複合キーを使う。

収集recipeは `collection_plan.py` が必須キー・値域・不明キーを検証する。planにはrecipe、API version、実装hash、旧候補の固定リスト、検索区画を保存する。job、lease/fencing、キャッシュ、checkpointはSQLiteで管理し、確定ページからのみ子jobを登録する。取得の成否と品質・漏洩は別状態。操作契約は `docs/preparation/collection-readiness.md` を参照。

## 審査

`record-review --file` の必須キーは `view_id, kind, verdict, reviewer, reviewer_type, rationale, attestations`。kindはquality/leakage。qualityは `PENDING|PASS|HOLD|REJECT`、leakageは `PENDING|PASS|FAIL|INDETERMINATE`。pilotのPASSには `reviewer_type: human` と、以下すべての明示的なtrueが必要。

    {"full_bundle_read":true,"provenance_checked":true,"solution_context_checked":true}

これは人間の実審査を記録する契約であり、操作者の認証機構ではない。エージェントが人間になりすましてPASSを作らない。review IDはviewのhashに結合され、viewには本文、ファイル名、根拠、正解照合対象、recipe、adapter/store実装hashが含まれる。後続のFAILやINDETERMINATEで再出力を停止する。

## 選別・公開

recipeは `recipes/experiments/hdd-blind-pilot-v1.json` が実行可能な例。初版は操作者が明示したview一覧をsealし、別recipeの混在、未審査、同一Case/系列の重複、repository/機構の上限、件数不足、holdoutへのunknown/discovery exposureを拒否する。記録済みのdiscovery公開はscopeにかかわらず保守的にholdoutから除外する。自動的な系列の連結判定・候補母集団の固定・6/24のholdout配分・scopeごとの未知性はP3/P4で追加するため、本機能だけで設計全体のpilot完了とはしない。

`export` はSEALED manifestからだけ出力し、取得・LLM呼び出しを行わない。追跡メタデータはバンドル外。artifact名とseedを審査した後、opaqueなinput番号で出力する。既存の出力はファイル集合とバイト列が完全一致する場合だけ再利用する。公開ディレクトリとその祖先にsymlinkを許さない。macOSの `/tmp`・`/var` もsymlinkなので、出力には実体パスを使う。

OS権限によるconsumer隔離、敵対する同一ユーザーの同時ファイル置換、ネットワーク経由の解アクセスは保証しない。`isolation_level: static_bundle_only` を常に記録する。
