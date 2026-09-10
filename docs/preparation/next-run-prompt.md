# 次回実行プロンプト — HDD v2

`docs/protocols/hdd-v2.md`を正本として使う。2026-09-09の11:30/17:30 runは終了済み。
旧runを再initせず、固定時刻・絶対パス付きの旧scriptsを次回へ流用しない。
この文書の保存は次回の課金実験やautomationの開始を意味しない。

まず入力を準備する。今回の失敗は、3 Dreamsの後に再構成調査が長時間続き、
新しい審査済み入力を1件も追加できなかったこと。新たな大量収集やバージョン総当たりより、
原文に入力が揃っている1件をCase/Claimから審査・seal/exportまで完遂することを優先する。

1. 既存corpusをauditし、保存SourceRevisionを確認する。HOLDごとに不足物、担当者、次の作業、
   解除条件を`save-recovery`で記録する。「No View」だけを理由にしない。
2. 解消したblockerにはimmutable record IDを添える。全blocker解消後は`prepare-review`で
   private review packageを作り、全文・出典・解答文脈を読む。
3. 実際のquality/leakage審査を`record-review`で記録する。委任されたagentはagentとして記録し、
   human PASSを捏造しない。解消していないHOLD/FAILを数合わせでPASSにしない。
4. 両審査PASS後にselect→seal-selection→exportする。変更後のexporterでは旧snapshot/PASSを
   再利用できないため、既存Deno事例も再process・再審査する。原文、host実機、PR、過去の候補名を混ぜない。
5. 通常は独立したdiscovery系列を2件以上準備する。1件だけならsmall_trialを明示する。
   discoveryを未知holdoutへ付け替えない。24事例が揃っていないことは不足として記録する。

収集が必要なら既存の`collection-readiness.md`と固定recipeに従う。同じcollectionを再開し、
`NO_RUNNABLE_JOB`や未完了0件のcollectionをresumeし続けない。総予算を自動で増やさない。
再構成だけで原文入力が得られないCaseはparkする。現行の公開adapterはreported evidence用であり、
ホストの実験コードをgenerated_promptやoperator_suppliedへ付け替えて通さない。

HDD開始を指示されたら、新しいrun ID・開始/保全/終了時刻・予算を固定する。
`recipes/experiments/hdd-v2.example.json`からpolicyを作り`init-experiment`へ渡す。
公開snapshotを`experiment-progress --kind input_ready`へ登録する。
R1原版をDreamer、ホストをRed Penとする。provider・残高・予算上限は実測し、無断代替・自動補充しない。

毎jobの前に`experiment-status`と`admit-job`を通す。subjectにはCase IDを使い、
意味のある仮説と、その結果で変える判断を書く。admission成功に加えて既存の費用・時刻・同時実行ゲートも必要。
既定の上限は同一Caseのrecovery 3回、Dream 3回、grounding 1回。
空き枠は、具体的な不足物を埋める作業または新しい操作を試す作業へ渡す。埋めること自体を目的にしない。

Dreamerには公開bundleと世界内の要求だけを送る。未知CLIの架空の操作記録を生成させ、
ホストは原文と想像を区別して扱う。未知CLIが実在しないことや、実機のargvがないことだけで棄却しない。
Red PenはPreserve、既存操作との差分、世界内の矛盾を先に評価し、1〜3個の圧力を返す。
`record-discovery`で元traceと判定を保存する。NOVEL_OPERATIONは実証済みの意味ではない。
安定した操作が出たら、別worktreeで現実の観測機構へ対応づけ、実argv・出力・反例で実証する。

進捗は新しい適格入力、根拠付きblocker解除、有意味な操作の発見だけ。
`experiment-progress`へ根拠IDを登録し、heartbeat・実行回数・同じsnapshotの再登録を進捗にしない。
30分の無進捗で新規jobは打切り。試行上限に達したCaseは切り替え、代わりがなければ早期保全する。
日末まで同じHOLDにフラグを足し続けない。

保全/打切り/終了時刻に達したら新規起動を止め、当該runの実プロセスだけを回収・停止確認する。
admission gateやclose-experimentはプロセスをkillしない。実際の停止確認を別途記録する。
入力hash、採否、費用、再実行方法、未解決blockerを保存・backupし、close-experimentを記録する。
R1費用を総費用に見せず、ホスト費用が不明なら不明とする。0成果物を許容する。
