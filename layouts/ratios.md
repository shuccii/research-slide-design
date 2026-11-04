# 16:9 と 4:3 の組み分け

縦の区画(タイトル 0.30 in、罫線 2.08 in、本文 2.25–6.68 in、出典欄 6.82 in)と文字サイズは共通。違うのはカラム数だけ: **16:9 は 6 カラム(1.533 in)、4:3 は 4 カラム(1.800 in)**、列の間はどちらも 0.667 in(本文 24pt の 2 倍)。値は `tokens/spacing-16x9.json` と `tokens/spacing.json`。

- 16:9 は 4:2、3:3、2:2:2 で組む。
- 4:3 は横に並べるのは 2 つまで(2:2)。16:9 で 3 つ並ぶものは、4:3 では 2 つにするかページを分ける。
- 4:3 のタイトルは全角約 20 字で 1 行。16:9 用に書いたタイトルが 4:3 で 2 行になるなら短くする。
- 同じ原稿から両方を作るときは、`Deck("16:9")` と `Deck("4:3")` で同じ関数を呼び、`wide = ratio == "16:9"` で組み分けだけ変える(`examples/build_sample.py`)。

| レイアウト | 16:9 | 4:3 |
| --- | --- | --- |
| [cover](cover.md) | 全幅に縦に並べる | 全幅に縦に並べる。題は全角約 18 字で 2 行に収める |
| [figure-notes](figure-notes.md) | 図 4 列 : 数値 2 列 | 図 2 列 : 数値 2 列(図が小さくなるなら数値を下に回さずページを分ける) |
| [two-figures](two-figures.md) | 3 枚(2:2:2) | 2 枚(2:2)。3 枚目は別ページか、ほかのページの数値で代える |
| [figure-table](figure-table.md) | 図 3 列 : 表 3 列 | 図を上(全幅、高さ約 2.3 in)、表を下(全幅)。入らなければページを分ける |
| [comparison-table](comparison-table.md) | 全幅 | 全幅。列は 4 つまで(省いた列は発表者ノートに書く) |
| [method](method.md) | 流れは横 1 列、式は全幅 | 流れは横 1 列(4 段階まで)、式は全幅 |
| [equation](equation.md) | 表 4 列 : 条件 2 列 | 表を全幅。条件は一言メッセージへ |
| [key-numbers](key-numbers.md) | 数値 2 列 : 図 4 列 | 数値 2 列 : 図 2 列 |
| [summary](summary.md) | 結論 3 列 : 数値と限界 3 列 | 結論 2 列 : 数値と限界 2 列。結論は 2 項目まで |
| [references](references.md) | 2 段組 | 1 段 |
| [matched-comparison](matched-comparison.md) | 3:3 | 2:2 |
| [small-multiples](small-multiples.md) | 3 枚(2:2:2) | 2 枚(2:2) |
| [overview-detail](overview-detail.md) | 全体 4 列 : 拡大 2 列 | 全体 2 列 : 拡大 2 列 |
| [ablation](ablation.md) | 3:3 | 2:2 |
| [error-diagnosis](error-diagnosis.md) | 4:2 | 2:2 |
| [evidence-next](evidence-next.md) | 全幅 | 全幅(4 列。文は短く) |

python-pptx では `Deck("16:9")` が 13.333 × 7.5 in、`Deck("4:3")` が 10 × 7.5 in にする。`latex_eq.py` はどちらの比率でもそのまま使える(位置は in で渡す)。
