# HDD v2 — 入力化、発見、実証を接続する

2026-09-09 17:30 runを受けた、次回以降の運用契約。過去runのプロンプト・判定・ログは改変しない。
入口は [次回実行プロンプト](../preparation/next-run-prompt.md)。この変更だけでは新run・課金・automationを開始しない。

## 観測と診断

事実: 1730 runは1 discovery、3 Dreams、採用0。17:54の選考後、追加事例を翌朝まで再構成したがViewが増えなかった。
最終停止は2026-09-10 08:30:13 JST。R1実測 $0.028512 はホスト/Codexの計算費用を含まない。
出典: `lab-runs/specimen-hdd-20260909-1730/{FINAL_JURY,R1_BUDGET,HARD_STOP,SNIPPET_PENDING}.md`。

診断: 「空き枠を埋める」が進捗の代理となった可能性がある。
「No View」は未完了の工程であって、単独では品質HOLDの解除条件にならない。
また、発見段階で実在CLIの実行証明を要求すると、HDDの架空の操作探索と衝突する。
これらは運用上の仮説であり、次回の適格入力増加・有意味な操作の発見・実装結果で再評価する。

## 1. 三種類の記録を分離する

| 記録 | 許容するもの | 許容しないもの |
| --- | --- | --- |
| 報告原文・公開入力 | SourceRevisionの引用、明示した欠落、原因を決めない質問 | 修正PRやホスト再構成を報告時の入力へ格上げ |
| 架空の使用記録 | 未知CLI名、架空の出力、失敗、継続した世界の操作 | 原文の書換え、架空の出力を実行証拠・再現成功・修正成功として採用 |
| 実装・実証 | 実ファイル、実argv、stdout/stderr、終了コード、反例 | Dreamの自己申告だけによる成功判定 |

Dreamerへは新exportの`seed.md`と公開bundleのみ。HDD、Red Pen、評価尺度、旧候補名、原文全文、解答、実証結果は送らない。
未知CLIが存在する前提は世界内の前提であり、ホスト実機の事実ではない。
ホストは架空の使用記録から操作を抽出する。**架空CLIが実在しないことだけで棄却しない**。

### Red Penの必須順序

1. Preserve: 残すべき具体的操作を一つ挙げる。
2. 原文との矛盾、世界内の矛盾、既存操作との差分を別々に評価する。
3. `NOVEL_OPERATION` / `THIN_WRAPPER` / `INCOHERENT` / `NEEDS_PRESSURE`を選ぶ。
4. 新しい名前の禁止や実機実行証明へ逃げず、能力除去・矛盾注入など1〜3個の圧力を返す。
5. 安定した操作が現れたら実装・実証へ移す。実証後の成功判定は別の記録にする。

`THIN_WRAPPER`には「最も近い既存操作」「それを差し引いて残る操作」を記述する。
「HTTP成功」「出力が長い」「CLI名が新しい」は採用理由にならない。
`javix`の旧出力なら、架空名そのものより、既知のrun/lock操作の再演と内部状態の矛盾を批判する。

`record-discovery --file assessment.json --trace original-dream.md`で構造化判定と元のtraceを保存する。
JSON例は [discovery.example.json](../../recipes/experiments/discovery.example.json)。
このコマンドは常に`evidence_class=speculative_design`、`runtime_verified=false`を記録する。
新規性や意味的整合性はホストの判断であり、スキーマ検査で証明したとは言わない。

実証の採否記録にはcore operation、現実への対応、残る制約、実argv/出力/終了コード、反例、既存操作との比較を残す。
過去の`tool_success=false`は書き換えない。今後も実証されるまでは成功件数に数えない。

## 2. HOLDを解除可能な仕事にする

収集済みSourceRevisionからCase/Claimを作り、`save-recovery --file recovery.json`で担当者と不足を記録する。
例: [recovery.example.json](../../recipes/experiments/recovery.example.json)。

各blockerには、安定したid、不足物、次の作業、解除判定、resolved、immutable evidence record IDsが必要。
resolved=trueには実在するrecord参照が必要。既存blockerの削除による解除はできない。
根拠が解除条件を満たすかは担当者が読み、責任を持って判断する。recordの存在だけでは内容の正しさを証明しない。

| 状態 | 次の作業 |
| --- | --- |
| 原文に入力があるが未抽出 | 保存原文からbyte rangeを確定しClaimを作る |
| 原文に必要なファイルがない | 具体的ファイルを追加取得するか、parkして別事例へ |
| 解答混入 | 症状の引用元と修正情報を分離し、新しいClaim/Viewを審査 |
| ホスト再構成だけがある | host-onlyのまま保存。原文引用を揃えるかpark |
| 公開引用が揃い、Viewがない | `prepare-review`を実行し審査パッケージを作る |
| quality/leakageがPENDINGまたはHOLD | 対象hashに対して実際の審査を行う |
| 両方PASS | select → seal-selection → export → 新しいtrial |

```bash
python3 scripts/corpus.py --root CORPUS save-recovery --file recovery.json
python3 scripts/corpus.py --root CORPUS recovery-status CASE_ID
python3 scripts/corpus.py --root CORPUS prepare-review RECOVERY_ID \
  --config reprocess.json --recipe view-recipe.json --output PRIVATE_REVIEW_DIR
```

`prepare-review`は既存のCase/Claim/reprocessと漏洩検査を再利用する。
古いCase/recovery revision、未解除のblocker、park中のCaseは拒否する。
生成物は**審査用preview**で、公開許可ではない。quality/leakageのPASSやViewのexportを自動では作らない。
既存ViewにHOLDがあればその履歴を保持し、根拠を読んだ再審査を追記する。

現行コーパスの公開経路は報告原文の引用に限定される。
`generated_prompt`や`operator_supplied`への付替えでホスト再構成を原文に見せかけない。
再構成結果そのものを次の探索入力にしたい場合には、別のlocal-evidence契約の設計が必要。
今回はその契約を暗黙に追加せず、既存の報告原文経路を最後まで通す。

同一事例の再構成は既定で最大3試行。各試行の前に「どの不足物を埋め、どの結果なら次工程へ進むか」を宣言する。
同じ結果を別バージョン・別フラグで増やすだけなら試行しない。
失敗しても消えないよう、打切り理由と残る不足物を残してparkする。

## 3. 稼働ではなく進捗で継続を決める

新runのpolicyを [hdd-v2.example.json](../../recipes/experiments/hdd-v2.example.json) から作る。
時刻はタイムゾーン付きで実際の開始指示に合わせる。終了時刻は不変、re-initは禁止。
通常は独立したdiscovery系列を最低2つ準備する。1つだけなら`small_trial=true`を明示する。
未知holdoutの条件、同一系列除外、品質・漏洩審査は緩和しない。

```bash
python3 scripts/corpus.py --root CORPUS init-experiment --file policy.json
python3 scripts/corpus.py --root CORPUS experiment-progress RUN_ID \
  --kind input_ready --evidence SNAPSHOT_ID
python3 scripts/corpus.py --root CORPUS experiment-status RUN_ID
python3 scripts/corpus.py --root CORPUS admit-job RUN_ID --kind dream \
  --subject CASE_ID --hypothesis 'この事例で、失敗後にも残る未知の操作を一つ探索する'
```

`admit-job`成功後にだけ、その一件を開始する。失敗した開始も試行枠を消費する。
job kindは`recovery` / `dream` / `grounding`。subjectは**Case ID**を使い、別名で上限を回避しない。
groundingはそのCaseの`affordance_found`記録が必要。既定ではCaseごとに1回の実装・実証作業を許可する。
全コマンドはホスト用。モデルの呼出し・課金・候補コマンドの実行はしない。

進捗時計を進めるのは次だけ:

- `input_ready`: 現時点でも有効なSEALED snapshotが新しいdiscovery系列を追加した。
- `blocker_resolved`: 直前に未解除だったblockerが、根拠付きの最新recovery recordで解除された。
- `affordance_found`: admission済みCaseの操作に、ホストが`NOVEL_OPERATION`を認めた。

`experiment-progress RUN_ID --kind KIND --evidence RECORD_ID`で記録する。
heartbeat、コマンド数、テスト数、追記行数、同じsnapshot/系列/判定の再登録は進捗ではない。
affordanceはCaseごとに1回まで時計を進める。細かい文言変更で延命しない。
スナップショットはjob admission時にも再検証し、審査撤回・revocation・exporter変更を検出する。

既定で30分、有効な進捗がなければ`PRESERVE_NO_PROGRESS`となり、新job admissionを拒否する。
Caseの試行枠が尽きたら`SWITCH_CASE`。別の準備済みCaseがなければ保全・終了する。
時刻まで無意味な作業で枠を埋めない。0成果物の終了を許容する。
開始済みjobから本物の新しい証拠が届き、保全時刻前なら記録できる。閉じたrunは再開しない。

これは**admission gate**であり、実行中プロセスを自動終了するdaemonではない。
コーディネータは待機中も短い間隔でstatusを確認し、既存の実行上限とタイムアウトを併用する。
`PRESERVE` / `PRESERVE_NO_PROGRESS` / `HARD_STOP`なら、新規起動を止め、当該runだけの実行中jobを回収・必要に応じ停止する。
`experiment-status`はWORK以外でexit 3。`admit-job`は拒否時に非0終了するので無視しない。
NOT_BEFORE時も、開始時刻を書き換えたり時計を偽造しない。

予算ゲートは別途維持する。`max(0,min(user_cap,remaining-reserve))`、R1呼出し上限、同時実行上限、
保全・hard_endをすべて満たした場合にだけ呼び出す。新admissionは残高確認の代わりではない。
旧1730 runの絶対パス・時刻を持つscriptsを新runでそのまま実行しない。

## 4. 終了・移行

日末の報告は、稼働時間、適格入力/系列の増分、Dream数、発見した操作、実証した候補、採否、
HOLD解除数、park理由、R1費用、ホスト費用の把握範囲を短くまとめる。
費用が取得できない場合はunknownとし、R1費用を総費用として書かない。
詳細なstdout/stderrは個別証拠へ置き、STATE/STATUS/heartbeatへ同じ長文を複製しない。

実プロセスの回収・停止確認とバックアップ後に:

```bash
python3 scripts/corpus.py --root CORPUS close-experiment RUN_ID --reason '進捗停止、証拠保存、当該runのプロセス回収済み'
```

closeは台帳の終了だけを記録する。`processes_stopped=false`はツールがプロセス停止を実証していないという意味。
別の停止記録で実PIDの生存確認を残す。実時刻と予定のhard_endを分け、早期終了を予定時刻の実行に偽装しない。
未完了の再現調査は次回へ機械的に継続せず、残る不足物が入力化・採否を変えるかを再評価する。

公開seedテンプレートの変更でexporter hashが変わる。旧PASS/snapshotは新exporterでは無効になる。
旧runは履歴のまま残し、同じ引用でも再process→全文再審査→新selection→seal→新しいexport先を使う。
古いreview IDや固定snapshot IDを新しいseedへ転用しない。

検証: `python3 scripts/check_corpus.py`。ネットワーク・外部モデルなしで、HOLD解除から審査・seal/exportまで、
無進捗の打切り、重複進捗、審査撤回、架空の操作と実証の分離をテストする。
