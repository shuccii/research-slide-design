---
name: research-slide-design
description: 研究スライドのデザインシステム(白黒基調・大きな文字・日本語の下に英語訳・16:9 と 4:3・ヒラギノ角ゴ ProN)で、学会発表・研究紹介・進捗報告のスライドを作る。「研究用デザインで」「日英併記で」「第三者にもわかるように」と言われたとき、書式指定のない研究スライドを作るときに使う。1 枚の要素は 3 つまで。表は色なし・黒罫線、数式は LaTeX からネイティブ数式へ変換して原文を代替テキストに残す、引用は ACS 風の番号式。
---

# 研究スライド(大きな文字・日英併記)

本体: このスキルのリンク元リポジトリ(`research-slide-design/`)。**最初に `AGENTS.md` と `DESIGN.md` を読む。** 値の正本は `tokens/*.json`、根拠は `REFERENCES.md`。

## 手順

1. 適用範囲を確認する。学会・提出先の書式指定があればそちらが優先。学会資料は確認前の草案として扱い、投稿・共有しない。
2. 依頼を `guides/slide-brief.md` の書式に落とす。用途(学会発表・研究紹介・進捗報告)は `guides/use-cases.md`。出典・数値が足りなければ質問する。
3. 比率は指定がなければ 16:9(6 カラム、`tokens/spacing-16x9.json`)。4:3 指定時は 4 カラム(`tokens/spacing.json`)。組み分けは `layouts/ratios.md`。
4. 値は tokens から取る。書体は PowerPoint 用に `Hiragino Kaku Gothic ProN W3` / `W6`(ファミリー名だけだと代替される)。色は roles の場所だけ。表は色なし・黒罫線。
5. レイアウトは `layouts/*.md` の 16 種(どれも両方の比率で使える)。**1 枚の要素は 3 つまで、余白は残してよい。** 入らなければ文字を小さくせず、文を短くするかページを分ける。文字は (日本語, 英語訳) の組で渡し、略語は初出で説明、軸に向き、結論に根拠のページ。角丸は面と枠だけ。選び分けは `guides/layout-selection.md`。
6. 図は `guides/figures.md`: グラフは `use_chart_style()` で貼り付け枠の実寸に描く。模式図は構成をノードと矢印のリストにしてから SVG で描き、`scripts/export_svg.sh` で書き出して目視・最小文字を検査する。
7. 組むのは `lib/research_deck.py`(見本 `examples/build_sample.py`)。数式は `Slide.equation(latex, …)`。Word がない環境では `$$ … $$` のプレースホルダーになり、後で `tools/latex_eq.py deck.pptx --convert`。全式の LaTeX は `--extract` で取り出せる。
8. 引用は `tokens/citation.json`: 本文 [n]、図の直下に出典区分、ページ下端に短縮形、最終ページに文献表と図表の出典表。DOI と Web の確認日を書く。
9. 検証: `deck.save(path, strict=True)` で警告を 0 件にしてから、`scripts/pptx2pdf.sh deck.pptx deck.pdf` → `swift scripts/pdf2png.swift deck.pdf png` で全ページを目視。PDF のフォントが HiraKakuProN-W3/W6 か確認する。独自の色を足したら `python3 tools/contrast.py`。`DESIGN.md` の「納品前チェック」を全部満たしてから渡す。
