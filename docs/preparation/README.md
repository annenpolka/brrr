# 次回実行の準備状況

2026-09-09 JST。公開境界（P0）と保全移行（P1）の初回実装を行い、旧151標本と旧HDD状態を取り込んだ。その後P2のGitHub収集・再開も実装・検証済み。**次回は [収集開始の手順](collection-readiness.md) から始められる。** 再利用の小規模な一巡は [mini-loop.md](mini-loop.md) にまとめた。合成3事例の一括demoと、実資料1事例・2 Viewの審査パッケージを用意済み。下表と移行receiptは初回保全時点の記録。HDD本番用の24事例はまだ審査・確定していない。

## 確認した結果

| 確認 | 結果 |
| --- | --- |
| 基準コミット | `caabebcc37a699388a8a7691c055bb323916ed48` |
| 設計書SHA-256 | `4b5189e78f640550c4d7993c3ad69fc2d4922bf43b674d827601dea0470bb675` |
| 旧packet | 151件。旧 `REAL_SOURCE_BACKED` は124件 |
| specimens直下の他の項目 | `SKIP_077.md`、`SKIP_080_R1.md` の2文書。欠損packetを意味しない |
| 保全した項目 | lab run 9,511 + HDD root 2,420 = 11,931項目 |
| 特殊な項目 | symlink 18件、FIFO 7件。リンク文字列／FIFOの種別とmodeを保存し、対象を読んだり起動したりしない |
| 保存object / record / alias | 7,536 / 153 / 151。recordはsample/full archiveの2件と旧CaseRevision 151件 |
| 再取り込み | 新alias 0、新revision 0。full archive IDも一致 |
| 元ファイルの不変性 | 両root全体の内容・名前・種別・modeが変更前と一致 |
| 参照整合性 | audit成功、errors 0 |
| バックアップ復元 | 別rootでobject 7,536、record 153、alias 151を確認 |
| 公開適格 | 0件。全旧標本は品質・漏洩ともPENDING |
| 原文回収の候補 | 重複を除いたGitHub URL 220件。独立事例数や取得済みSource数ではない |
| 検証 | `scripts/check_corpus.py` の31テスト成功 |

旧run全体の `trees_hash` は `10a22232aa90ad27991927d00d2248aa4fb5b402ec9bf4ff02f6fc220adcd09c`。取り込んだfull archive IDは `be71dc2c768979db7b8cb22ec7ef7388292319bc6db14517ed53edb3f067283d`。標本の保全と使用許可は別状態であり、旧採用ラベルから新PASSを作っていない。

証跡はこのディレクトリの `legacy-baseline.json`、`import-{dry-run,sample,full,repeat}.json`、`baseline-verification.json`、`corpus-audit.json`、`backup-receipt.json`、`restore-receipt.json`、`readiness.json`、`test-results.txt`。本文・正解・DB・バックアップはGit管理外にある。

## 今回実装した経路

`src/brrr_corpus/store.py` は不変object、SQLite transaction、一意制約、単一coordinator lock、参照監査、バックアップ・復元を提供する。オブジェクトを確定してからメタデータを登録し、失敗後の孤立objectは削除せず再利用する。

`legacy.py` は旧run全体を保全し、元のpacket・manifest・旧解釈を保持する。URLは未解決の候補のまま。`raw-sources/SOURCE.md` という名前だけで原文と認定しない。FIFOの過去の通信内容は保存できず、種別とmodeのみ記録する。

`boundary.py` は出典範囲を指定した手動viewの作成、明示的な人間の品質・意味的漏洩審査、審査対象hashの確認、手動選別のsealとオフラインexportを提供する。本文・ファイル名・recipe・exporter/storeコードの変更で旧PASSは失効する。旧packetの直接公開と旧curationの流用を拒否する。

OS全体の盲検隔離は実装していない。出力は常に `static_bundle_only`。このリポジトリをそのままDreamerの作業領域に使うと、旧正解へアクセスできるため、strict blindとは呼べない。

## 再確認するコマンド

リポジトリrootで実行する。Python 3.10以上、標準ライブラリのみ。今回の検証環境はPython 3.14.5 / macOS。`fcntl` を使うためPOSIX環境が必要。

```sh
python3 scripts/check_corpus.py
python3 scripts/corpus.py audit
python3 scripts/corpus.py verify-baseline \
  --run lab-runs/specimen-hdd-20260902-1112 \
  --companion .hdd-runs/specimen-hdd-20260902-1112 \
  --baseline docs/preparation/legacy-baseline.json
python3 scripts/corpus.py readiness --recipe recipes/experiments/hdd-blind-pilot-v1.json
```

現状のreadinessは不足24をJSONで返してexit 3になる。異常終了を隠したものではなく、審査済み候補がないという意図した結果。audit/verify-baselineの成功はexit 0。入力の不正・hash不一致はexit 1。未実装コマンドを指定するとargparseがexit 2を返す。

同じrunの再importも安全に試せる。`--dry-run` はDBもobjectも作らない。

```sh
python3 scripts/corpus.py import-legacy \
  --run lab-runs/specimen-hdd-20260902-1112 \
  --companion .hdd-runs/specimen-hdd-20260902-1112 --dry-run
python3 scripts/corpus.py import-legacy \
  --run lab-runs/specimen-hdd-20260902-1112 \
  --companion .hdd-runs/specimen-hdd-20260902-1112
```

ローカル保存先は `.brrr-corpus/`。検証済みバックアップは `.brrr-corpus-backups/preparation-20260909/`、復元済みコピーは `.brrr-corpus-restored/preparation-20260909/`。別のバックアップや復元には新しい出力名を指定する。既存コピーを上書きしない。

```sh
python3 scripts/corpus.py backup --output .brrr-corpus-backups/next-check
python3 scripts/corpus.py restore \
  --backup .brrr-corpus-backups/next-check \
  --output .brrr-corpus-restored/next-check
python3 scripts/corpus.py --root .brrr-corpus-restored/next-check audit
```

## 手動でviewを審査・出力する経路

原文・view・reviewの厳密な入力契約は `schemas/README.md` に記載した。実データと審査ファイルは `.brrr-corpus/` 配下で管理する。以下のIDとファイル名は操作者が用意したものに置き換える例であり、審査済みの実データはまだ存在しない。

```sh
python3 scripts/corpus.py import-source \
  --file .brrr-corpus/original.txt --metadata .brrr-corpus/source-metadata.json
python3 scripts/corpus.py stage-view \
  --spec .brrr-corpus/view.json --recipe recipes/experiments/hdd-blind-pilot-v1.json
python3 scripts/corpus.py inspect-view VIEW_ID --output .brrr-corpus/reviews/view-001
python3 scripts/corpus.py record-review --file .brrr-corpus/quality-review.json
python3 scripts/corpus.py record-review --file .brrr-corpus/leakage-review.json
python3 scripts/corpus.py seal --view VIEW_ID_1 --view VIEW_ID_2
python3 scripts/corpus.py export SNAPSHOT_ID --output .brrr-corpus/exports/pilot-v1
python3 scripts/corpus.py record-exposure SNAPSHOT_ID --consumer hdd-run-id --scope discovery-run-id
```

pilot recipeは24件を要求するため、sealの例の2件だけでは停止する。24の適格なviewを指定し、repository最大6・主機構最大8・系列重複なしを満たす必要がある。0件を埋める目的でsyntheticを本番へ混ぜない。

`inspect-view` は人間の審査用に公開予定の全文と非公開の出典・正解照合資料を出す。Dreamerへ渡すファイルは `export` が作るbundleのみ。人間の実審査を受ける前に `reviewer_type: human` のPASSを作らない。collectorは原文のコマンドを実行せず、ローカル再現済み表示も作らない。

## 初回保全時点の設計受け入れ条件との対応

下表はP0/P1時点の記録。Case関係・母集団固定・scopeなどの追加実装と残る制限は [mini-loop.md](mini-loop.md) に記載した。

| 設計のテスト | 今回の検証範囲 | 残る条件 |
| --- | --- | --- |
| T01〜T03 | 旧run重複import、object後/transaction中/DB後の停止と再試行。追加実装でHTTPページにも故障注入済み | collection-readiness.md参照 |
| T04 | 追加実装でlease/fencingも検証済み | collection-readiness.md参照 |
| T05 | 手動原文に加え、HTTP fixtureでもコメント編集・取得観測・旧版不変を検証 | collection-readiness.md参照 |
| T06〜T10 | 追加実装で304、HTTPエラー、検索上限、再走査、コメント不足を検証済み | collection-readiness.md参照 |
| T11〜T13 | 旧資料候補を自動統合・実行証拠に格上げしない | Case関係と実行証拠schemaはP3 |
| T14〜T19 | 未審査拒否、既知文字列・識別子、意味的FAIL/未判定の拒否、hash失効、path/symlink/残存物拒否 | 未知の意味的漏洩と実view全件の内容監査は別途必要 |
| T20 | 明示した同一case/lineageの重複・分割越境を停止 | 関係の連結成分を計算するP3 |
| T21 | 手動原文の過去時点は未検証と記録 | 厳密な時点条件のviewは未対応 |
| T22 | synthetic snapshotの同一バイト列再出力 | 実pilot snapshotでも再検証する |
| T23 | 外部命令文で未審査公開が許可されない | LLMを使うP3で別途検証する |
| T24 | 明示選別の不足・多様性上限を拒否 | 母集団固定・全候補採否理由・6件holdout配分はP4 |
| T25 | DB/object復元とsynthetic snapshot再出力、実コーパス復元 | OS強制停止・電源断の耐久試験は未実施 |
| T26 | unknown拒否、記録済みdiscovery exposureを優先して拒否 | experimentごとのscopeと系列推定はP3 |

## 次に実行する作業

次回用の指示は `next-run-prompt.md`。収集器の実装を挟まず、`collection-readiness.md` のcollectから開始する。収集後は実装済みのCase/Claim/reprocess/selectを使い、[小規模な一巡](mini-loop.md) から内容審査を試す。24事例pilotは別途進める。

夜間HDD実験、R1/OpenRouterの呼び出し、定期automationは今回開始していない。実験の終了時刻・費用上限・新run IDは本番を開始する時点で固定する。旧master promptのthroughput規則より、新しい品質・漏洩・公開境界を優先する。
