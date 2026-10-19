# 数式(LaTeX で書いて、後で変換できる形で残す)

数式は **LaTeX を正本** にする。スライドではネイティブ数式(OMML)として表示し、元の LaTeX は図形の代替テキストに残す。こうしておくと、論文・Markdown・ポスターへそのまま転記でき、変換環境がない場所でも後でまとめて変換できる。

## 書き方の約束

| 項目 | 書き方 | 例 |
| --- | --- | --- |
| 式の区切り | 別行立ては `$$ … $$`、文中は `$ … $` | `$$ y = f(\mathbf{x}) + \varepsilon $$` |
| ベクトル・行列 | ベクトルは `\mathbf{x}`、行列は大文字 `K` | `\mathbf{k}_{*}^{\top}` |
| 添え字 | 必ず波括弧 | `\sigma_{n}^{2}`(`\sigma_n^2` も可だが統一する) |
| 括弧 | 伸びる括弧は `\left( … \right)` | `\left(K + \sigma_{n}^{2} I\right)^{-1}` |
| 関数名 | 立体 | `\log`, `\exp`, `\mathrm{RMSE}` |
| 単位 | 式の外に [ ] で | `T [K]` |
| 番号 | `number=1` で右端に (1) | – |

使えない記法(`\begin{align}` の複数行、マクロ定義 `\newcommand` など)は変換時にエラーで止まる。1 行ずつ別の式に分ける。

## スライドに入れる

```python
import sys; sys.path.insert(0, "lib")
from research_deck import Deck
deck = Deck("16:9")
s = deck.slide("GPR は予測の平均と分散を同時に返す", "式と変数")
x, w = s.col(0, 7)
s.equation(r"\bar{f}_{*} = \mathbf{k}_{*}^{\top}\left(K + \sigma_{n}^{2} I\right)^{-1}\mathbf{y}", x, 2.4, w, 0.8, number=1)
```

- Microsoft Word(Mac / Windows)がある環境では、Word 同梱の `mathml2omml.xsl` を使ってネイティブ数式になる。PowerPoint の数式エディタでそのまま編集できる。
- Word がない環境では `$$ … $$` のプレースホルダー(図形名 `latex-eq`)が置かれる。

## 後でまとめて変換・取り出す

```bash
# プレースホルダーをネイティブ数式へ(Word のある環境で)
uv run --no-project --with latex2mathml --with lxml --with python-pptx \
  python tools/latex_eq.py deck.pptx --convert

# デッキ内の全数式の LaTeX を一覧(論文・Markdown への転記用)
uv run --no-project --with latex2mathml --with lxml --with python-pptx \
  python tools/latex_eq.py deck.pptx --extract

# 記法だけ確かめる
uv run --no-project --with latex2mathml --with lxml \
  python tools/latex_eq.py --check "\frac{a}{b}"
```

手で入れる場合は、PowerPoint の「挿入 → 数式 → LaTeX 形式」に貼り付けて変換し、代替テキストに `LaTeX: …` を書いておく。

## 変換の注意(Word の XSL の癖を前処理で補正済み)

`\left(` 内の演算子が区切り文字になる、数学用英数字(𝐱 など)が描けない、行列の括弧が伸びない、空白が消える、総和の添字が横に付く — これらは `tools/latex_eq.py` が変換前に直す。変換後は必ず PDF に書き出して目視する。

## 変数の説明表

式の近くに「記号 / 意味 / 単位」の表を置き、式中の全記号を載せる。表は色なし・黒罫線。
