# レイアウトの選び分け

基本10種と追加6種を、説明したい関係で選ぶ。追加6種は16:9用の派生レイアウトであり、別の配色テーマではない。4:3指定時は基本10種から選び、必要なら図を別ページに分ける。

| 説明したいこと | 選ぶレイアウト | 既存との違い |
| --- | --- | --- |
| 対照実験、前後比較、従来法と提案法の比較 | [matched-comparison](../layouts/matched-comparison.md) | two-figuresの派生。左右を対称にし、比較条件と対応する根拠を固定する。 |
| 温度・試料・期間などの複数条件を一覧する | [small-multiples-6](../layouts/small-multiples-6.md) | two-figuresの派生。3枚1列から6枚2段へ拡張し、短い条件名で統一する。 |
| ピーク、交点、外挿域など局所的な差を説明する | [overview-detail](../layouts/overview-detail.md) | figure-notesの派生。右欄を説明文から拡大図2枚へ置換し、範囲を明記する。 |
| 前処理、モデル要素、データ源の寄与を検証する | [ablation](../layouts/ablation.md) | figure-tableの用途特化。結果の順位だけでなく、何を除いたかを対応表で示す。 |
| 平均指標だけでは見えない系統誤差や外れ値を調べる | [error-diagnosis](../layouts/error-diagnosis.md) | two-figuresとfigure-tableの組合せ。位置・分布・代表例の3種類の根拠を固定する。 |
| 研究MTGの判断、考察、追加実験の相談に使う | [evidence-next](../layouts/evidence-next.md) | summaryの派生。3段組の要約から、結論・根拠・限界・次の検証の対応表にする。 |

## 選択の目安

- 二つの構成の差を見せる場合は `matched-comparison`。条件が違う比較には条件差を明記する。
- 同じ形のグラフを多条件で並べる場合は `small-multiples-6`。異なる種類の図3枚なら既存の `two-figures`。
- 全体図では差が見えない場合は `overview-detail`。単なる補足説明なら既存の `figure-notes`。
- 構成要素の寄与を調べる場合は `ablation`。結果全般の表なら既存の `figure-table`。
- 平均指標の理由を調べる場合は `error-diagnosis`。単一の指標の強調なら既存の `key-numbers`。
- 結論と追加検証を相談する場合は `evidence-next`。発表全体の総括なら既存の `summary`。

## 見本の再生成

`examples/build_layout_gallery.py` は既存の `Deck` / `Slide` とtokensで6枚を生成する。出力先は `examples/out/layout_gallery/`。PPTXの本文と表は編集可能、図は画像で貼付し、生成元とPDFも保存する。

全数値は架空の配置検証データ。対照比較・残差図は合成関数から計算し、要素別検証の値は見本用の定数。出力の `sample-data.json` とスクリプトを参照する。研究上の手法の有効性や因果関係を示すものではない。
