# equation — 数式

- 別行立ての式を 1–3 本、本文枠の左右中央に `equation` 18pt で。右端に式番号 (1)(2) を `eq-number` 12pt。
- 式の下か右に「変数の説明表」(記号 / 意味 / 単位、`table` 12pt)を必ず置く。式中の全記号を載せる。
- 最下部に「式の意味」2–3 行(`body`)と出典 [n]。長い導出は別ページに分ける。
- PowerPoint にはネイティブ数式で入れる: `tools/latex_eq.py`(LaTeX → OMML)か、PowerPoint の「数式 → LaTeX 形式」へ貼り付け。画像やテキストで代用しない。

共通: タイトル `title` 22pt W6(結論か主題を1文)、直下に `message` 14pt。0.95 in に `line-strong` の罫線。最下段(6.95–7.35 in)に出典欄 `caption` 10pt とページ番号。本文領域 1.08–6.85 in に高さ 0.6 in を超える空き枠を残さない。空いたら、まず文字(typography の max まで)と図を大きくし、それでも空けば情報を足す(spacing の fill_rule)。表は色なし・黒罫線(tables.json)。
