# 参考文献(設計の根拠)

ACS 風・番号式。tokens・DESIGN.md・guides の [n] はこの番号を指す。確認日はすべて 2026-10-05。

1. デジタル庁. デジタル庁デザインシステム: カラー. https://design.digital.go.jp/dads/foundations/color/ (accessed 2026-10-05).
   — 文字と背景は常に 4.5:1 以上、テキスト以外の UI 要素は 3:1 以上。グレーは solid-gray の段階を使う。
2. デジタル庁. デジタル庁デザインシステム: カラー/アクセシビリティ. https://design.digital.go.jp/dads/foundations/color/accessibility/ (accessed 2026-10-05).
   — 文字サイズにかかわらず 4.5:1、色だけで情報を区別しない、図にはテキストラベルを併記、CUD 推奨配色の利用を推奨。
3. Okabe, M.; Ito, K. Color Universal Design (CUD): How to Make Figures and Presentations That Are Friendly to Colorblind People. J*Fly, 2002 (rev. 2008). https://jfly.uni-koeln.de/color/ (accessed 2026-10-05).
   — 系列色(Black, Blue #0072B2, Vermillion #D55E00, Bluish green #009E73, Reddish purple #CC79A7)の出典。HEX は同配色を再掲した [8] と二次資料で照合。
4. Office 伝わる(高橋佑磨, 片山なつ). 伝わるデザイン: ユニバーサルデザイン. https://tsutawarudesign.com/universal1.html (accessed 2026-10-05).
   — 赤と緑の組み合わせを避ける、マーカー・線種・直接ラベルで区別する、純黒より濃いグレーの文字。
5. Rougier, N. P.; Droettboom, M.; Bourne, P. E. Ten Simple Rules for Better Figures. PLoS Comput. Biol. 2014, 10 (9), e1003833. https://doi.org/10.1371/journal.pcbi.1003833
   — 図の設計原則(書誌のみ確認。本文は今回アクセスできず)。
6. Tufte, E. R. The Visual Display of Quantitative Information, 2nd ed.; Graphics Press: Cheshire, CT, 2001.
   — data-ink ratio(図のインクはデータに使う)。グリッドを薄く、枠線を減らす根拠。
7. デジタル庁. デジタル庁デザインシステム: タイポグラフィ. https://design.digital.go.jp/dads/foundations/typography/ (accessed 2026-10-05).
   — 14 CSS px 未満は原則使わない、本文行間 150–175%。本系統は投影スライド用に本文 16pt・注 12pt・出典 10pt とし、10pt は出典欄に限る。
8. Wong, B. Points of View: Color Blindness. Nat. Methods 2011, 8 (6), 441. https://doi.org/10.1038/nmeth.1618
9. W3C. Web Content Accessibility Guidelines (WCAG) 2.1, Success Criteria 1.4.1, 1.4.3, 1.4.11. https://www.w3.org/TR/WCAG21/ (accessed 2026-10-05).
   — コントラスト比の計算式(相対輝度)。`tools/contrast.py` はこの式を使う。
10. 科学技術振興機構. SIST02 参照文献の書き方, 2007 年版. https://jipsti.jst.go.jp/sist/handbook/sist02_2007/main.htm (accessed 2026-10-05).
    — 日本の参照文献の基準(2012 年に事業終了、現在も大学図書館で参照)。和文献の書き方の確認に使う。
11. Banik, G. M.; Baysinger, G.; Kamat, P. V.; Pienta, N. J., Eds. The ACS Guide to Scholarly Communication; American Chemical Society: Washington, DC, 2020. https://doi.org/10.1021/acsguide
    — 文献表の書式(ACS 風)の典拠(書誌のみ。本文は未確認)。

## 確認できず採用しなかったもの

- CUD 推奨配色セット ver.4(CUDO, 2018)の画面用 HEX 値: 公式ページで値を確認できなかったため採用していない。https://cudo.jp/?page_id=1565
- 日本放射線技術学会などの学会スライド指針: 一次資料を確認できなかったため根拠にしていない。
