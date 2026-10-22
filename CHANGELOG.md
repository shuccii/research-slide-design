# CHANGELOG

- 2026-10-20: 初版(公開)。非公開の研究用デザインシステム B(白黒・高密度)を元に、16:9 を標準化。色のコントラストを引き上げ(ink-sub #404040、caption #595959、alert #A04500)、色の役割(roles)を追加。表を色なし・黒罫線に変更。余白は文字・図を大きくして埋める規則と文字サイズの上限を追加。python-pptx ビルダー `lib/research_deck.py`、見本デッキ(16:9、7 枚)、数式の LaTeX 代替テキスト・プレースホルダー・一括変換(`--convert` / `--extract`)、図の作成フロー(`guides/figures.md`、`scripts/export_svg.sh`)、用途別の手引き、依頼書式を追加。PowerPoint 用の書体名を `Hiragino Kaku Gothic ProN W3/W6` に固定。
- 2026-10-21: 分数は横線で組む規則を追加。`tools/latex_eq.py` はスラッシュの分数をエラーで止め、変換後の分数を横線(bar)にそろえる。DESIGN.md・guides・charts.json・SVG 見本(`SVG.frac()`)に反映し、見本に RMSE の定義式を追加。

- 2026-10-22: 16:9用の派生レイアウト6種(対照比較・6条件一覧・全体と拡大・要素別検証・誤差診断・根拠と次の検証)を追加。用途別の選択ガイド、再生成できる6枚の見本PPTX/PDF/PNGを追加。既存トークンと基本10種は維持。
