# Corpus v1 の契約

初版はPython標準ライブラリのみで動作する。ここで示すJSONの必須キー・列挙値・不明キー拒否は `src/brrr_corpus/boundary.py` 、`cli.py`、`cases.py`、`selection.py` が実行時に検証する。JSON Schemaライブラリには依存しない。

保存用recordは `serialization_version: 1, kind, payload, blobs, records` のenvelope。UTF-8、JSON key順序固定、空白なし、末尾LFで直列化し、SHA-256をIDにする。`blobs` と `records` は重複を除いて整列する。snapshot IDもこのcanonical manifest envelopeのhash。可変のSEALED/REVOKEDイベントはhash外。原文は直列化せず、受け取ったバイト列のまま別objectに保存する。

## 公開するviewの入力

`stage-view --spec` の必須キーは `schema_version, origin, case_id, lineage_group, repository, primary_mechanism, split, exposure, mode, artifacts, restricted_blobs, forbidden_identifiers`。`origin` は `real|synthetic`、`split` は `discovery|holdout`、`exposure` は `unknown|unexposed|discovery`、`mode` は `blind_problem` のみ。`reprocess` は任意キー `derivation` を追加し、Case/Claim/config/pipeline hashへの不変参照を保存する。手動stageで借用したderivationと内容が異なる場合は拒否する。未知の由来、旧要約、縮約fixtureの格上げはP0で拒否する。`unexposed` は内容審査が確認する運用上の申告であり、収集器が未知性を証明した値ではない。

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

`reviewer_type: fixture` のPASSはView・原文がすべてsyntheticであり、View recipeがsyntheticを許可する場合に限り有効。合成demo専用で、real資料には使えない。`agent` のPASSは認めない。

これは人間の実審査を記録する契約であり、操作者の認証機構ではない。エージェントが人間になりすましてPASSを作らない。review IDはviewのhashに結合され、viewには本文、ファイル名、根拠、正解照合対象、recipe、adapter/store実装hashが含まれる。後続のFAILやINDETERMINATEで再出力を停止する。

## 選別・公開

recipeは `recipes/experiments/hdd-blind-pilot-v1.json` が実行可能な例。初版は操作者が明示したview一覧をsealし、別recipeの混在、未審査、同一Case/系列の重複、repository/機構の上限、件数不足、holdoutへのunknown/discovery exposureを拒否する。記録済みのdiscovery公開はscopeにかかわらず保守的にholdoutから除外する。Case/Claim経由の新しいViewには下記のSelectionRunを必須とし、同障害groupとscopeを検証する。6/24のholdout自動配分は未対応で、設計全体のpilot完了とはしない。

`export` はSEALED manifestからだけ出力し、取得・LLM呼び出しを行わない。追跡メタデータはバンドル外。artifact名とseedを審査した後、opaqueなinput番号で出力する。既存の出力はファイル集合とバイト列が完全一致する場合だけ再利用する。公開ディレクトリとその祖先にsymlinkを許さない。macOSの `/tmp`・`/var` もsymlinkなので、出力には実体パスを使う。

OS権限によるconsumer隔離、敵対する同一ユーザーの同時ファイル置換、ネットワーク経由の解アクセスは保証しない。`isolation_level: static_bundle_only` を常に記録する。


## 小規模Case/Claim/reprocess

`save-case --file` の必須キーは `key, title, repository, origin, sources, primary_mechanism, exposure, legacy_revisions, forbidden_identifiers`。sourcesは `[{"revision":"SOURCE_REVISION","classification":"unreviewed"}]`。分類は `candidate_public|unreviewed|restricted_solution|restricted_evaluation|restricted_prior_ideas`。候補分類はPASSを意味しない。同じkeyは同じUUID、変更は新revision。元Caseのoriginは変更できない。

`legacy_revisions` は保全済みlegacy_case_revisionのID一覧。同じ旧Caseの版に限定し、そのUUIDを新Caseでも使用する。複数の旧Caseを同障害と考える場合も別Caseとして登録して関係を結ぶ。旧要約をSourceRevisionとしてClaimへ流すことはできない。

`add-claim --file` は `case_revision, classification, segment, rationale` が必須。segmentは前述の原文UTF-8範囲または生成した問い。Sourceは指定Case版に所属し、制限資料をpublicへ格下げできない。混在したunreviewed原文から明示的な候補範囲を取り出せるが、Viewは未審査になる。

`relate-case --file` は `left, right, kind, active, rationale, reviewer` が必須。left/rightはCase UUID、activeはbool。kindは `same_incident|derived_from|possible_duplicate|same_mechanism`。最初の3種類の有効な関係の連結成分をgroupとし、same_mechanismは統合しない。変更はイベント追記し、同じ組・種類の最新判断が有効。derived_fromは方向も保存する。

`reprocess --config --recipe` のconfigは次の形。recipeは既存のView recipe。

```json
{
  "case_revision": "CASE_REVISION",
  "pipeline_id": "trial-v1",
  "split": "discovery",
  "sections": {
    "TASK.md": ["QUESTION_CLAIM"],
    "OBSERVED.md": ["OBSERVATION_CLAIM"],
    "COMMANDS.md": ["COMMAND_QUESTION_CLAIM"]
  }
}
```

公開できる候補Claimだけを連結し、Caseに登録された制限Sourceと制限Claimを必ず照合対象へ継承する。同じ入力・コードは同じView。問い・根拠・pipeline hash変更は別Viewとなる。後から制限Claimを追加した場合も旧Viewの再利用を止める。生成した問いを事実として装っていないかは人間の審査に残る。

## SelectionRun

実行可能な例は `recipes/selection/mini-{one,two}-v1.json` と `mini-real-{v1,v2}.json`。必須キーは `schema_version, recipe_id, view_recipe, pipeline_id, case_key_prefix, target_cases, max_cases_per_repository, max_cases_per_primary_mechanism, seed, exposure_scope, allow_shortfall`。選別条件でView recipeの件数・上限・shortfall条件を緩めることはできない。

`select --recipe` は条件に一致する全保存Viewを母集団として固定し、現Case版、関係、現在の品質・漏洩review、scope内のexposure、各候補の順位・採否・理由を参照とともに保存する。順位はseed/Case key/View IDのhash。旧版も母集団から隠さず除外理由を残す。splitはView configで指定し、同じgroupからは最大1件。選別結果はREADYまたはHOLDで、HOLDはexit 3。

`seal-selection ID` は確定した選別リストを厳密に使用する。新しいViewが追加されても古い母集団を黙って選び直さない。Case/関係graph、selector/pipeline/exporterコード、選んだViewの審査が変われば再選別・必要な再審査を要求する。export時も検証する。新しいdiscovery exposureが同じscope内でholdoutと重なれば停止する。`record-exposure --split discovery|holdout|all` で実際に渡した側を記録する（省略はall）。

Case/関係の索引テーブルは既存DBに追加し、過去recordを変更しない。全情報はバックアップ・復元対象。現在はschema v1と現在のpipeline/selector/exporterの組で動作し、古い実装の自動再起動は提供しない。


## 明示された委任レビュー

View recipeには任意の `delegated_review` を指定できる。厳密なキーは `reviewer, authorization` で、どちらも空でない文字列。ユーザーの委任に基づいて設定し、view hashへ結合する。この条件があるViewでは、その名前と一致する `reviewer_type: agent` のPASSを受け付ける。指定なしでは従来のhuman/合成fixture契約を維持する。両種類の審査、全attestation、後続HOLD/FAIL、変更による失効は従来どおり。現行例は `recipes/selection/mini-evidence-v1.json`。

委任を変更しても旧ViewのPASSを新しいViewへ流用できない。審査前テンプレートは、委任があれば指定agent、なければhumanで生成し、どちらもPENDINGとfalseのattestationを初期値にする。
