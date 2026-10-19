# スライド依頼の書式(AI エージェントへの渡し方)

AI エージェントにスライドを作らせるときは、下の書式で「中身」を渡す。見た目はこのリポジトリが決めるので、依頼には書かなくてよい。エージェントはこの書式を埋めてから作り始め、埋まらない欄(出典・数値)は推測せず質問する。

```yaml
deck:
  purpose: 学会発表 | 研究紹介 | 進捗報告   # guides/use-cases.md の用途
  ratio: "16:9"                              # 指定がなければ 16:9
  minutes: 12                                # 発表時間
  audience: 同分野の研究者 | 異分野 | 研究室
  title: 結論を 1 文で
  presenter: [氏名, 所属・学会名・日付]
  constraints: 学会の書式指定があれば書く(優先される)

references:                                  # 登場順。DOI か URL+確認日
  - "Author, A. A.; Author, B. B. Title. J. Abbr. Year, Vol (Issue), Pages. https://doi.org/..."

slides:
  - layout: figure-notes                     # layouts/ の 10 種から
    title: 結論を 1 文で
    message: 何を比べた図か
    figure: { data: path/to/data.csv, kind: line | scatter | parity | bar, source: 本研究 }
    numbers: [{ label: RMSE(提案法), value: 0.091, note: 従来法 0.490, ref: null }]
    points: [読み取り 1, 読み取り 2]
    cite: [1, 2]
  - layout: equation
    title: …
    equations:                               # LaTeX が正本(guides/equations.md)
      - { latex: '\bar{f}_{*} = \mathbf{k}_{*}^{\top}\left(K + \sigma_{n}^{2} I\right)^{-1}\mathbf{y}', number: 1, ref: 1 }
    variables: [[x*, 予測したい点, 任意], [K, 共分散行列, –]]
```

## エージェントの作業順

1. `AGENTS.md` → `DESIGN.md` を読む。
2. 依頼をこの書式に落とす。数値と出典がそろっていない欄は質問する。
3. 図を作る(`guides/figures.md`)。グラフはデータから計算する。
4. `lib/research_deck.py` で組む(見本 `examples/build_sample.py`)。
5. `scripts/pptx2pdf.sh` → `scripts/pdf2png.swift` で全ページを画像にして目視し、`DESIGN.md` の「納品前チェック」を満たすまで直す。
6. 報告: 保存先、枚数、出典の一覧、推測・未確認の点、目視で直した点。
