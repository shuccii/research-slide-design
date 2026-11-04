# レイアウトの選び分け

基本 10 種と派生 6 種を、説明したい関係で選ぶ。すべて 16:9 と 4:3 の両方で使える(比率ごとの組み分けは [ratios](../layouts/ratios.md))。どれも 1 枚に要素は 3 つまで。入らなければページを分ける。

| 説明したいこと | 選ぶレイアウト | 基本との関係 |
| --- | --- | --- |
| 1 つの図が主張の根拠 | [figure-notes](../layouts/figure-notes.md) | 基本 |
| 図の傾向と正確な値 | [figure-table](../layouts/figure-table.md) | 基本 |
| 手法 × 条件の数値 | [comparison-table](../layouts/comparison-table.md) | 基本 |
| 対照実験、前後比較、従来法と提案法の比較 | [matched-comparison](../layouts/matched-comparison.md) | two-figures の派生。左右を対称にし、比較条件をそろえる |
| 温度・試料・期間などの複数条件を一覧する | [small-multiples](../layouts/small-multiples.md) | two-figures の派生。同じ形の図を同じ軸で並べる |
| ピーク、交点、外挿域など局所的な差を説明する | [overview-detail](../layouts/overview-detail.md) | figure-notes の派生。数値の代わりに拡大図を置く |
| 前処理、モデル要素、データ源の寄与を検証する | [ablation](../layouts/ablation.md) | figure-table の用途特化。何を除いたかを対応表で示す |
| 平均指標だけでは見えない系統誤差や外れ値を調べる | [error-diagnosis](../layouts/error-diagnosis.md) | two-figures の用途特化。位置と分布の 2 つの根拠を並べる |
| 研究MTGの判断、考察、追加実験の相談に使う | [evidence-next](../layouts/evidence-next.md) | summary の派生。結論・根拠・限界・次の検証の対応表にする |

## 選択の目安

- 二つの構成の差を見せる場合は `matched-comparison`。条件が違う比較には条件差を明記する。
- 同じ形のグラフを多条件で並べる場合は `small-multiples`。異なる種類の図なら `two-figures`。
- 全体図では差が見えない場合は `overview-detail`。単なる補足説明なら `figure-notes`。
- 構成要素の寄与を調べる場合は `ablation`。結果全般の表なら `figure-table` か `comparison-table`。
- 平均指標の理由を調べる場合は `error-diagnosis`。単一の指標の強調なら `key-numbers`。
- 結論と追加検証を相談する場合は `evidence-next`。発表全体の総括なら `summary`。

## 見本の再生成

`examples/build_layout_gallery.py` が派生 6 種を 16:9 と 4:3 で生成する。出力先は `examples/out/layout_gallery/`。PPTX の本文と表は編集でき、図は画像で貼る。

全数値は架空の配置確認用データ。対照比較・残差図は合成関数から計算し、要素別検証の値は見本用の定数。研究上の手法の有効性や因果関係を示すものではない。
