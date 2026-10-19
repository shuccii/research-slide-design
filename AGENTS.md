# AGENTS.md — AI エージェント向け指示(Claude Code / Codex 共通)

このリポジトリは、学会発表・研究紹介・進捗報告のスライドを **白黒基調・高密度** で作るためのデザインシステム。AI が仕様を読んで、毎回同じ見た目を再現するためのもの。

## 作業の順番

1. `DESIGN.md` を読む(適用範囲・原則・版面・色・表・数式・引用・納品前チェック)。
2. 依頼を `guides/slide-brief.md` の書式に落とす。用途ごとの構成は `guides/use-cases.md`。**出典・数値がそろっていない欄は推測せず質問する。**
3. 比率は指定がなければ **16:9**(`tokens/spacing-16x9.json`、配置は `layouts/16x9.md`)。
4. 値は `tokens/*.json` から取る。色・文字サイズ・余白を自分で決めたり直書きしたりしない。
5. ページ構成は `layouts/` の 10 種から選ぶ。
6. 図は `guides/figures.md` の流れで作る(グラフは matplotlib + `lib/research.mplstyle`、模式図は SVG)。数値はデータから計算する。
7. 組むときは `lib/research_deck.py`(`Deck` / `Slide`)を使う。見本は `examples/build_sample.py`。
8. 数式は LaTeX で書き、`Slide.equation()`(`tools/latex_eq.py`)で入れる(`guides/equations.md`)。
9. `scripts/pptx2pdf.sh` → `scripts/pdf2png.swift` で全ページを PNG にして目視し、はみ出し・重なり・0.6 in を超える空き・代替フォントがなくなるまで直す。
10. 報告: 保存先、枚数、出典一覧、推測・未確認の点、目視で直した点。

## 守ること

- 学会・提出先・所属組織の書式指定が最優先。
- 1 スライド 1 イシュー。タイトルは結論を 1 文で。
- 余白が残ったら、まず文字と図を大きくする(`typography.json` の `max` まで)。それでも空けば情報を足す。
- 色は `colors.json` の `roles` の場所だけ。色だけで区別しない。**表は色なし・黒罫線。**
- 数値・事実を作らない。確認できない数値・図・書誌は載せない。見本・架空データは「見本データ」と明記する。
- 他人の図はライセンスを確認し、`Adapted from [n]` / `Reproduced from [n]` を書く。
- 学会の要旨・発表資料は、共著者・指導者の確認前は草案として扱い、投稿・共有しない。
- トークンを変えたら見本を作り直して目視し、`CHANGELOG.md` に 1 行残す。
