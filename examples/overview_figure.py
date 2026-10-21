"""模式図(SVG)の見本。guides/figures.md の流れで、このリポジトリ自身の図を 2 枚描く(標準ライブラリだけ)。

    python3 examples/overview_figure.py           # docs/overview.svg と docs/figure-flow.svg を作る
    scripts/export_svg.sh docs/overview.svg       # PDF / PNG に書き出して最小文字を確認

型: パイプライン(左→右)。構成(ノードと矢印)は下の NODES / FLOW に文字で先に書き、座標はそこから決める。
色は tokens/colors.json の roles: 本システムの中心(デザイン仕様)= accent、検証 = ink、注意 = alert。
"""
from __future__ import annotations

import json
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
C = {k: v["value"] for k, v in json.loads((ROOT / "tokens/colors.json").read_text()).items() if isinstance(v, dict) and "value" in v and isinstance(v["value"], str)}
FONT = "Hiragino Kaku Gothic ProN, Hiragino Sans, Yu Gothic, Meiryo, sans-serif"


class SVG:
    def __init__(self, w, h):
        self.w, self.h, self.items = w, h, []

    def text(self, x, y, s, size=24, color="ink", weight=300, anchor="start"):
        self.items.append(f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{C[color]}" '
                          f'text-anchor="{anchor}" xml:space="preserve">{escape(s)}</text>')

    def line(self, x1, y1, x2, y2, color="ink", width=2, dash=None, arrow=False):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        m = ' marker-end="url(#arrow)"' if arrow else ""
        self.items.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{C[color]}" stroke-width="{width}"{d}{m}/>')

    def rect(self, x, y, w, h, stroke="ink", width=1.5, fill="background"):
        self.items.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{C[fill]}" stroke="{C[stroke]}" stroke-width="{width}"/>')

    def frac(self, x, y, num, den, size=24, color="ink"):
        """分数を分子・横線・分母に組む(スラッシュで書かない)。x は横線の中心、y は横線の高さ。"""
        w = max(len(num), len(den)) * size * 0.62 + size * 0.3
        self.text(x, y - size * 0.25, num, size, color, anchor="middle")
        self.line(x - w / 2, y, x + w / 2, y, color, max(1.2, size / 18))
        self.text(x, y + size * 0.95, den, size, color, anchor="middle")
        return w

    def save(self, path):
        head = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" width="{self.w}" height="{self.h}" '
                f'font-family="{FONT}">\n<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
                f'markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{C["ink"]}"/></marker></defs>\n'
                f'<rect width="{self.w}" height="{self.h}" fill="#FFFFFF"/>\n')
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(head + "\n".join(self.items) + "\n</svg>\n", encoding="utf-8")
        print(path)


def column(svg, x, w, title, lines, top=150, color="ink", heading_size=30, size=24):
    """1 段階 = 上に太線+見出し+説明。枠付きカードは使わない。"""
    svg.line(x, top, x + w, top, color, 5)
    svg.text(x, top + heading_size * 1.55, title, heading_size, color, 600)
    for i, s in enumerate(lines):
        svg.text(x, top + heading_size * 1.55 + size * 1.9 + i * size * 1.6, s, size, "ink")


# ---------- 図 1: リポジトリの全体像(16:9、1600 × 900) ----------
NODES = [
    ("入力", ["依頼(slide-brief)", "データ・図の元", "文献(DOI・URL)"], "ink"),
    ("読む", ["AGENTS.md", "DESIGN.md", "guides/"], "ink"),
    ("値を取る", ["tokens/*.json", "色・文字・余白", "表・引用・図"], "accent"),
    ("組む", ["lib/research_deck.py", "layouts/ の 10 種", "tools/latex_eq.py"], "ink"),
    ("確かめる", ["PDF → PNG で目視", "contrast.py", "納品前チェック"], "ink"),
]
FLOW = [(0, 1), (1, 2), (2, 3), (3, 4)]


def overview(path):
    s = SVG(1600, 900)
    s.text(60, 70, "研究・高密度スライドのデザインシステム: AI エージェントが読む順番", 36, "ink", 600)
    s.line(60, 95, 1540, 95, "line-strong", 1.5)
    n = len(NODES)
    gap, x0 = 50, 60
    w = (1480 - gap * (n - 1)) / n
    for i, (title, lines, color) in enumerate(NODES):
        column(s, x0 + i * (w + gap), w, title, lines, top=140, color=color, heading_size=36, size=26)
    for a, b in FLOW:
        xa = x0 + a * (w + gap) + w + 6
        s.line(xa, 140, xa + gap - 12, 140, "ink", 2.5, arrow=True)
    # 下段: 出力と規則(表は色なし・黒罫線)
    s.line(60, 450, 1540, 450, "line-strong", 1.5)
    s.text(60, 510, "出力", 34, "ink", 600)
    for i, t in enumerate(["16:9 の PPTX(4:3 も可)", "ネイティブ数式+代替テキストに LaTeX", "SVG / PDF / PNG の図と生成スクリプト", "文献表と図表の出典表"]):
        s.text(60, 572 + i * 54, "・" + t, 30)
    s.text(820, 510, "守る規則", 34, "ink", 600)
    rules = [("1 スライド 1 イシュー、タイトルは結論", "ink"), ("余白は文字・図を大きくして埋める", "ink"),
             ("色は役割のある場所だけ(本研究 = 青)", "accent"), ("表は色なし・黒罫線", "ink"),
             ("出典のない数値・図は載せない", "alert")]
    for i, (t, c) in enumerate(rules):
        s.text(820, 572 + i * 54, "・" + t, 30, c)
    s.text(60, 878, "模式図。各ファイルの役割は README のファイル構成を参照", 22, "caption")
    s.save(path)


# ---------- 図 2: 図の作成フロー(guides/figures.md、1600 × 520) ----------
STEPS = [("1 入力を読む", ["元資料・データ", "貼る枠の大きさ"]), ("2 型を選ぶ", ["パイプライン", "ループ・比較 …"]),
         ("3 構成を文字に", ["ノードと矢印", "ラベルの出典"]), ("4 描く", ["Python で SVG", "色は roles"]),
         ("5 書き出す", ["export_svg.sh", "PDF と PNG"]), ("6 確かめる", ["目視・最小 12 pt", "出典を図の下に"])]


def flow(path):
    s = SVG(1600, 470)
    s.text(60, 64, "図の作成フロー: 描く前に構成を文字で決め、書き出して目で確かめる", 32, "ink", 600)
    s.line(60, 88, 1540, 88, "line-strong", 1.5)
    n = len(STEPS)
    gap = 36
    w = (1480 - gap * (n - 1)) / n
    for i, (title, lines) in enumerate(STEPS):
        x = 60 + i * (w + gap)
        column(s, x, w, title, lines, top=140, color="accent" if i == 3 else "ink", heading_size=26, size=22)
        if i < n - 1:
            s.line(x + w + 4, 140, x + w + gap - 6, 140, "ink", 2.5, arrow=True)
    # 直しのループ(6 → 4)
    x4 = 60 + 3 * (w + gap) + w / 2
    x6 = 60 + 5 * (w + gap) + w / 2
    s.line(x6, 330, x6, 380, "alert", 2, dash="8 6")
    s.line(x6, 380, x4, 380, "alert", 2, dash="8 6")
    s.line(x4, 380, x4, 336, "alert", 2, dash="8 6", arrow=True)
    s.text((x4 + x6) / 2, 416, "重なり・はみ出し・小さい文字があれば 4 に戻る", 22, "alert", anchor="middle")
    s.save(path)


if __name__ == "__main__":
    overview(ROOT / "docs" / "overview.svg")
    flow(ROOT / "docs" / "figure-flow.svg")
