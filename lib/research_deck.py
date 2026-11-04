"""研究スライドのビルダー(python-pptx)。値はすべて tokens/*.json から読む。

    import sys; sys.path.insert(0, "lib")
    from research_deck import Deck
    deck = Deck(ratio="16:9")                       # "16:9"(6 カラム)か "4:3"(4 カラム)
    s = deck.slide(("結論を1文で書いたタイトル", "Conclusion in one sentence"),
                   ("何を比べたページか", "What this page compares"))
    x, w = s.col(0, 4)                               # 0 番から 4 カラム分 (x, w) [in]
    s.image("fig.png", x, s.top, w, 3.5)
    x, w = s.col(4, 2)
    s.number_box(x, s.top, w, ("RMSE(n = 20)", "RMSE at n = 20"), "0.091", ("線形回帰は 0.490", "Linear: 0.490"), accent=True)
    s.text(x, 5.0, w, 1.0, [("読み取り {accent|強調} [1]", "Reading [1]")])
    s.sources(["[1] Author, J. Abbr. 2024"])
    deck.save("out.pptx")                            # はみ出しなどの警告があれば表示する

文字は「日本語」か「(日本語, 英語訳)」の組で渡す。組なら英語訳を日本語の直下に小さく置く。
{accent|語} は accent、{alert|語} は alert、{bold|語} は W6 になる。
measure() で高さを見積もり、枠からのはみ出し・本文下端超え・英語訳の長すぎを deck.warnings に集める。
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from lxml import etree
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_CONNECTOR
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Inches, Pt

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))


def _load(name):
    return json.loads((ROOT / "tokens" / name).read_text(encoding="utf-8"))


COLORS = _load("colors.json")
TYPO = _load("typography.json")
TABLE = _load("tables.json")
SHAPES = _load("shapes.json")
FONT = TYPO["family"]["pptx"]["regular"]  # PowerPoint(Mac)はウェイト付きの名前でないとヒラギノを見つけられない
FONT_BOLD = TYPO["family"]["pptx"]["bold"]
NO_STYLE_TABLE = "{2D5ABB26-0587-4C30-8999-92F81FD0307C}"  # 表スタイル「スタイルなし、表のグリッドなし」


def color(name: str) -> str:
    """トークン名(ink, accent …)か #RRGGBB を 6 桁の HEX にする。"""
    if name.startswith("#"):
        return name[1:]
    return COLORS[name]["value"][1:]


def _style(name):
    st = TYPO["styles"][name]
    return st["size"], st["weight"] >= 600, st["color"]


_MARK = re.compile(r"\{(accent|alert|bold)\|([^{}]*)\}")


def _set_font(run, size, bold, col, family=None):
    family = family or (FONT_BOLD if bold else FONT)
    run.font.size = Pt(size)
    run.font.bold = False  # 太さは W6 の書体で出す(擬似太字にしない)
    run.font.color.rgb = RGBColor.from_string(color(col))
    rpr = run._r.get_or_add_rPr()
    for tag in ("a:latin", "a:ea", "a:cs"):
        el = rpr.find(qn(tag))
        if el is None:
            el = etree.SubElement(rpr, qn(tag))
        el.set("typeface", family)
    tr = 0.02 if size <= 26 else (0.01 if size < 45 else 0)  # tokens/typography.json の tracking
    rpr.set("spc", str(int(size * tr * 100)))


def _fill_paragraph(p, line: str, style: str, col: str | None, size_override=None):
    size, bold, base = _style(style)
    size = size_override or size
    base = col or base
    pos = 0
    for m in _MARK.finditer(line):
        if m.start() > pos:
            _set_font(p.add_run(), size, bold, base)
            p.runs[-1].text = line[pos:m.start()]
        kind, word = m.groups()
        r = p.add_run()
        r.text = word
        _set_font(r, size, bold or kind == "bold", kind if kind != "bold" else base)
        pos = m.end()
    if pos < len(line) or not p.runs:
        r = p.add_run()
        r.text = line[pos:]
        _set_font(r, size, bold, base)


def _no_margin(tf, lr=0.0, tb=0.0):
    tf.margin_left = tf.margin_right = Inches(lr)
    tf.margin_top = tf.margin_bottom = Inches(tb)


WARN = []  # Deck が自分の分を取り出す


def _char_w(ch, size):
    """1 文字の幅 [in] の見積もり(ヒラギノ: 全角 = 1em、半角 ≈ 0.6em)。"""
    return size / 72 * (0.6 if ord(ch) < 0x2E80 else 1.0)


def measure(lines, style, w, size=None, spacing=0):
    """日本語+英語訳の組を含む文字ブロックの高さ [in] を見積もる。"""
    import math
    st = TYPO["styles"][style]; size = size or st["size"]; lh = st.get("line_height", 1.3)
    EN = TYPO["english"]; es = EN["size"].get(style, 14)
    items = [lines] if isinstance(lines, (str, tuple)) else lines
    h = 0
    for i, line in enumerate(items):
        ja, en = line if isinstance(line, tuple) else (line, None)
        ja = _MARK.sub(lambda m: m.group(2), ja)
        n = sum(max(1, math.ceil(sum(_char_w(ch, size) for ch in seg) / w)) for seg in ja.split("\n"))
        h += n * size * lh / 72 + (spacing / 72 if i else 0)
        if en:
            ne = max(1, math.ceil(sum(_char_w(ch, es) for ch in en) / w))
            h += ne * es * EN["line_height"] / 72 + EN["space_before_pt"] / 72
            if ne > n:
                WARN.append(f"英語訳が日本語より長い({ne} 行 > {n} 行): {en[:30]}")
    return h


class Slide:
    def __init__(self, deck: "Deck", slide, number: int):
        self.deck, self.s, self.index = deck, slide, number
        sp = deck.spacing
        self.margin = sp["margin_in"]
        self.top = sp["zones"]["content"]["top_in"]
        self.bottom = sp["zones"]["content"]["bottom_in"]
        self.col_w = sp["grid"]["column_in"]
        self.gutter = sp["grid"]["gutter_in"]
        self.width = sp["slide"]["width_in"] - 2 * self.margin

    def _chk(self, y, h, what):
        ft = self.deck.spacing["zones"]["footer"]["top_in"]
        if y < ft and y + h > self.bottom + 0.03:
            WARN.append(f"p.{self.index} 本文の下端を超える {y + h:.2f} > {self.bottom:.2f} in: {what}")

    # ---- グリッド ----
    @property
    def columns(self):
        return self.deck.spacing["grid"]["columns"]

    def col(self, start: int, span: int):
        """start 番(0 始まり)から span 本ぶんの (x, w) [in]。16:9 は 6 カラム、4:3 は 4 カラム。"""
        x = self.margin + start * (self.col_w + self.gutter)
        w = span * self.col_w + (span - 1) * self.gutter
        if start + span == self.deck.spacing["grid"]["columns"]:  # 端数は最終カラムで吸収
            w = self.margin + self.width - x
        return x, w

    # ---- 文字 ----
    def text(self, x, y, w, h, lines, style="body", col=None, align="left", anchor="top", spacing=None, size=None):
        """文字を置く。size で pt を上書きできる(余白があるときに大きくする。上限は typography.json の max)。"""
        if size:
            mx = TYPO["styles"][style].get("max", size)
            size = min(size, mx)
        need = measure(lines, style, w, size, spacing or 0)
        if need > h + 0.02:
            WARN.append(f"p.{self.index} はみ出し {need:.2f} > {h:.2f} in: {str(lines)[:40]}")
        self._chk(y, max(h, need), str(lines)[:30])
        tb = self.s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
        tf = tb.text_frame
        tf.word_wrap = True
        _no_margin(tf)
        tf.vertical_anchor = {"top": MSO_ANCHOR.TOP, "middle": MSO_ANCHOR.MIDDLE, "bottom": MSO_ANCHOR.BOTTOM}[anchor]
        lh = TYPO["styles"][style].get("line_height", 1.3)
        EN = TYPO["english"]
        first = True
        al = {"left": PP_ALIGN.LEFT, "center": PP_ALIGN.CENTER, "right": PP_ALIGN.RIGHT}[align]
        for i, line in enumerate([lines] if isinstance(lines, (str, tuple)) else lines):
            ja, en = (line if isinstance(line, tuple) else (line, None))
            p = tf.paragraphs[0] if first else tf.add_paragraph()
            first = False
            p.alignment = al
            p.line_spacing = Pt((size or TYPO["styles"][style]["size"]) * lh)  # 倍率指定はヒラギノで行間が広がりすぎるので pt で固定
            if spacing:
                p.space_before = Pt(spacing if i else 0)
            _fill_paragraph(p, ja, style, col, size)
            if en:  # 英語訳: 日本語の直下に小さく ink-sub
                es = EN["size"].get(style, 14)
                q = tf.add_paragraph()
                q.alignment = al
                q.line_spacing = Pt(es * EN["line_height"])
                q.space_before = Pt(EN["space_before_pt"])
                r = q.add_run(); r.text = en
                _set_font(r, es, False, "ink-sub")
        return tb

    def bullets(self, x, y, w, h, items, style="body", size=None, spacing=12):
        items = [("・" + t[0], t[1]) if isinstance(t, tuple) else "・" + t for t in items]
        return self.text(x, y, w, h, items, style, spacing=spacing, size=size)

    def heading(self, x, y, w, text, size=None):
        """小見出し。戻り値は次に置ける y [in]。"""
        h = measure([text], "heading", w, size)
        self.text(x, y, w, h, [text], "heading", size=size)
        return y + h + 0.11

    def number(self, x, y, w, label, value, note="", accent=False, size=None, label_size=None):
        """要点数値: ラベル(label)→ 数値(number)→ 比較対象や条件(label)。戻り値は次に置ける y [in]。"""
        vs = size or TYPO["styles"]["number"]["size"]
        ls = label_size or TYPO["styles"]["label"]["size"]
        lh = ls * 1.5 / 72 + (14 * 1.35 / 72 if isinstance(label, tuple) else 0)
        vh = vs * 1.2 / 72
        self.text(x, y, w, lh, label, "label", size=ls)
        self.text(x, y + lh, w, vh, value, "number", col="accent" if accent else None, size=vs)
        if note:
            self.text(x, y + lh + vh + 0.05, w, lh, note, "label", size=ls)
        return y + lh + vh + (lh if note else 0)

    def box(self, x, y, w, h, r=None, fill="fill", line=None, pt=1.0):
        """角丸の面(注・要点数値・流れ図の箱)。影なし。r は角丸半径 [in]。"""
        from pptx.enum.shapes import MSO_SHAPE
        self._chk(y, h, "角丸の枠")
        sh = self.s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
        r = SHAPES["radius_in"]["large"] if r is None else r
        sh.adjustments[0] = min(0.5, r / min(w, h))
        if fill:
            sh.fill.solid(); sh.fill.fore_color.rgb = RGBColor.from_string(color(fill))
        else:
            sh.fill.background()
        if line:
            sh.line.color.rgb = RGBColor.from_string(color(line)); sh.line.width = Pt(pt)
        else:
            sh.line.fill.background()
        sh.shadow.inherit = False
        return sh

    def pill(self, x, y, text, col="accent", size=18):
        """両端が半円のラベル(「本研究」など)。枠線のみ、文字は同色。"""
        w = 0.35 + len(text) * size / 72 * 1.05
        h = size / 72 * 1.6
        self.box(x, y, w, h, r=h / 2, fill=None, line=col, pt=1.25)
        self.text(x, y, w, h, text, "label", col=col, align="center", anchor="middle", size=size)
        return w

    def number_box(self, x, y, w, label, value, note=None, accent=False, size=None, pad=None, h=None):
        """角丸の面に要点数値を置く。枠の高さは中身から計算する(h を渡すと列の高さにそろえる)。戻り値は下端 y。"""
        pad = SHAPES["padding_in"] if pad is None else pad
        size = size or TYPO["styles"]["number"]["size"]
        iw = w - 2 * pad
        hl = measure([label], "label", iw)
        hv = size * 1.2 / 72
        hn = measure([note], "label", iw) if note else 0
        need = pad + hl + hv + hn + pad
        h = max(h or 0, need)
        self.box(x, y, w, h)
        yy = y + pad + (h - need) / 2
        self.text(x + pad, yy, iw, hl, [label], "label")
        self.text(x + pad, yy + hl, iw, hv, value, "number", col="accent" if accent else None, size=size)
        if note:
            self.text(x + pad, yy + hl + hv, iw, hn, [note], "label")
        return y + h

    def rule(self, x, y, w, col="line-strong", pt=0.75):
        ln = self.s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x), Inches(y), Inches(x + w), Inches(y))
        ln.line.color.rgb = RGBColor.from_string(color(col))
        ln.line.width = Pt(pt)
        return ln

    def arrow(self, x1, y1, x2, y2, col="ink", pt=1.5):
        ln = self.s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
        ln.line.color.rgb = RGBColor.from_string(color(col))
        ln.line.width = Pt(pt)
        tail = etree.SubElement(ln.line._get_or_add_ln(), qn("a:tailEnd"))
        tail.set("type", "triangle")
        return ln

    # ---- 図・表・式 ----
    def image(self, path, x, y, w=None, h=None, credit=None):
        pic = self.s.shapes.add_picture(str(path), Inches(x), Inches(y),
                                        Inches(w) if w else None, Inches(h) if h else None)
        self._chk(Emu(pic.top).inches, Emu(pic.height).inches, f"図 {Path(str(path)).name}")
        if credit:
            bottom = Emu(pic.top + pic.height).inches
            cw = Emu(pic.width).inches
            self.text(x, bottom + 0.08, cw, measure([credit], "label", cw), [credit], "label")
        return pic

    def table(self, x, y, w, rows, col_widths=None, align=None, row_h=None, size=None, bold_cells=()):
        """色なし・黒罫線の表(tokens/tables.json)。rows[0] が見出し行。

        align: 列ごとの "l" / "r" / "c"。省略時は 1 列目左、数値らしい列は右。
        bold_cells: 決め手のセル (行, 列) を W6 にする(色は使わない)。
        """
        nr, nc = len(rows), len(rows[0])
        row_h = row_h or TABLE["row_height_in"]
        gf = self.s.shapes.add_table(nr, nc, Inches(x), Inches(y), Inches(w), Inches(row_h * nr))
        tbl = gf.table
        tblpr = tbl._tbl.tblPr
        for k in ("firstRow", "bandRow"):
            tblpr.set(k, "0")
        sid = tblpr.find(qn("a:tableStyleId"))
        if sid is None:
            sid = etree.SubElement(tblpr, qn("a:tableStyleId"))
        sid.text = NO_STYLE_TABLE
        col_widths = col_widths or [w / nc] * nc
        for j, cw in enumerate(col_widths):
            tbl.columns[j].width = Inches(cw)
        total = 0
        for i in range(nr):
            need = max(measure([v if isinstance(v, tuple) else str(v)], "table", cw - 0.12, size) for v, cw in zip(rows[i], col_widths)) + 0.1
            rh = max(row_h, need)
            tbl.rows[i].height = Inches(rh)
            total += rh
        self._chk(y, total, "表")
        self.last_table_h = total
        if align is None:
            num = re.compile(r"^[-+−±0-9.,%\s()×]+$")
            align = ["l"] + ["r" if all(num.match(str(r[j]) or "0") for r in rows[1:]) else "l" for j in range(1, nc)]
        size_pt = size or TYPO["styles"]["table"]["size"]
        m = TABLE["cell_margin_in"]
        for i, r in enumerate(rows):
            for j, val in enumerate(r):
                c = tbl.cell(i, j)
                c.fill.background()
                c.margin_left = c.margin_right = Inches(m["left_right"])
                c.margin_top = c.margin_bottom = Inches(m["top_bottom"])
                c.vertical_anchor = MSO_ANCHOR.TOP
                tf = c.text_frame
                tf.word_wrap = True
                p = tf.paragraphs[0]
                p.alignment = {"l": PP_ALIGN.LEFT, "r": PP_ALIGN.RIGHT, "c": PP_ALIGN.CENTER}[align[j] if i else ("l" if align[j] == "l" else "c")]
                ja, en = val if isinstance(val, tuple) else (val, None)
                run = p.add_run()
                run.text = str(ja)
                _set_font(run, size_pt, i == 0 or (i, j) in bold_cells, "ink")
                if en:
                    q = tf.add_paragraph(); q.alignment = p.alignment
                    r2 = q.add_run(); r2.text = en
                    _set_font(r2, TYPO["english"]["size"]["table"], False, "ink-sub")
                top = 1.0 if i <= 1 else 0.5  # 上端と見出し下は 1.0pt
                bot = 1.0 if i == nr - 1 or i == 0 else 0.5
                self._cell_border(c, "a:lnT", top)
                self._cell_border(c, "a:lnB", bot)
                self._cell_border(c, "a:lnL", 0.5 if j > 0 else None)
                self._cell_border(c, "a:lnR", 0.5 if j < nc - 1 else None)
        return gf

    @staticmethod
    def _cell_border(cell, tag, pt):
        tcpr = cell._tc.get_or_add_tcPr()
        old = tcpr.find(qn(tag))
        if old is not None:
            tcpr.remove(old)
        ln = etree.Element(qn(tag))
        if pt is None:
            ln.set("w", "0")
            etree.SubElement(ln, qn("a:noFill"))
        else:
            ln.set("w", str(int(pt * 12700)))
            ln.set("cap", "flat")
            ln.set("cmpd", "sng")
            fill = etree.SubElement(ln, qn("a:solidFill"))
            etree.SubElement(fill, qn("a:srgbClr")).set("val", color("ink"))
            etree.SubElement(ln, qn("a:prstDash")).set("val", "solid")
        # 罫線は塗り(fill)より前に置く決まり
        order = ["a:lnL", "a:lnR", "a:lnT", "a:lnB"]
        idx = 0
        for k, child in enumerate(tcpr):
            if child.tag in [qn(o) for o in order[: order.index(tag)]]:
                idx = k + 1
        tcpr.insert(idx, ln)

    def equation(self, latex, x, y, w, h, number=None, size=None):
        """別行立ての式。Word の XSL があればネイティブ数式、なければ $$…$$ のプレースホルダー。

        どちらも図形の代替テキストに元の LaTeX を残す(tools/latex_eq.py --extract で取り出せる)。
        """
        from latex_eq import place_equation
        size = size or TYPO["styles"]["equation"]["size"]
        return place_equation(self.s, latex, x, y, w, h, size, number)

    def notes(self, text: str):
        """発表者ノート(話す内容・補足・LaTeX の原文など)。"""
        self.s.notes_slide.notes_text_frame.text = text

    # ---- 出典欄 ----
    def sources(self, items):
        """出典欄(2行まで)。そのページで引いた文献の短縮形を続けて書く。"""
        z = self.deck.spacing["zones"]["footer"]
        w = self.width - 0.8
        self.text(self.margin, z["top_in"], w, z["bottom_in"] - z["top_in"], "  ".join(items), "caption")


class Deck:
    def __init__(self, ratio: str = "4:3"):
        self.ratio = ratio
        self.spacing = _load("spacing.json" if ratio == "4:3" else "spacing-16x9.json")
        self.prs = Presentation()
        self.prs.slide_width = Inches(self.spacing["slide"]["width_in"])
        self.prs.slide_height = Inches(self.spacing["slide"]["height_in"])
        self._layout = self.prs.slide_layouts[6]
        self.count = 0
        self._w0 = len(WARN)

    def blank(self) -> Slide:
        """タイトル帯のないページ(表紙など自由に組むとき)。ページ番号だけ入る。"""
        return self._new()

    def _new(self) -> Slide:
        self.count += 1
        s = Slide(self, self.prs.slides.add_slide(self._layout), self.count)
        z = self.spacing["zones"]["footer"]
        s.text(s.margin + s.width - 0.8, z["top_in"], 0.8, 0.3, str(self.count), "caption", align="right")
        return s

    def slide(self, title: str, message: str = "") -> Slide:
        s = self._new()
        z = self.spacing["zones"]
        s.text(s.margin, z["title"]["top_in"], s.width, z["title"]["height_in"] - 0.15, title, "title", anchor="top")
        if message:
            s.text(s.margin, z["message"]["top_in"], s.width, z["message"]["height_in"], message, "message")
        s.rule(s.margin, z["rule"]["y_in"], s.width, "line-strong", z["rule"]["height_pt"])
        return s

    def cover(self, title, subtitle, author_lines, points, sources=None) -> Slide:
        """表紙。title・subtitle・points は「日本語」か「(日本語, 英語訳)」。上に題、下段に氏名と要点。"""
        s = self._new()
        top = 0.6
        s.rule(s.margin, top, 0.9, "ink", 1.0)
        th = measure([title], "cover-title", s.width)
        s.text(s.margin, top + 0.15, s.width, th, [title], "cover-title")
        y = top + 0.15 + th + 0.2
        sh = measure([subtitle], "cover-sub", s.width)
        s.text(s.margin, y, s.width, sh, [subtitle], "cover-sub")
        y = y + sh + 0.45
        s.rule(s.margin, y - 0.2, s.width, "line-strong", 0.5)
        yy = s.heading(s.margin, y, s.width, ("本発表の要点", "Key points"))
        items = [("・" + p[0], p[1]) if isinstance(p, tuple) else "・" + p for p in points]
        ph = measure(items, "label", s.width, spacing=8)
        s.text(s.margin, yy, s.width, ph, items, "label", spacing=8)
        ah = measure(author_lines, "body", s.width)
        ay = max(yy + ph + SHAPES["gap_in"], s.bottom - ah)  # 要点と重ねない
        s.text(s.margin, ay, s.width, ah, author_lines, "body")
        if sources:
            s.sources(sources)
        return s

    def references(self, refs, title=("参考文献", "References"), columns=None, extra_note=None) -> Slide:
        """文献表(caption 14pt)。16:9 は 2 段、4:3 は 1 段。入らなければ警告が出るのでページを分ける。"""
        s = self.slide(title, ("本文の登場順。DOI と Web 資料の確認日つき", "In order of citation, with DOIs and access dates"))
        n = self.spacing["grid"]["columns"]
        columns = columns or (2 if n >= 6 else 1)
        per = -(-len(refs) // columns)
        span = n // columns
        for k in range(columns):
            x, w = s.col(k * span, span)
            chunk = [f"[{k * per + i + 1}] {r}" for i, r in enumerate(refs[k * per:(k + 1) * per])]
            s.text(x, s.top, w, s.bottom - s.top, chunk, "caption", spacing=8)
        if extra_note:
            s.sources([extra_note])
        return s

    @property
    def warnings(self):
        return list(dict.fromkeys(WARN[self._w0:]))

    def check(self, strict=False):
        """警告(はみ出し・本文下端超え・英語訳の長すぎ)を表示する。strict なら 1 件でもあれば止める。"""
        ws = self.warnings
        for w in ws:
            print("警告:", w)
        if strict and ws:
            raise SystemExit(f"{len(ws)} 件の警告。文を短くするかページを分ける")
        return ws

    def save(self, path, title: str = "", strict=False):
        cp = self.prs.core_properties  # python-pptx の既定の作成者名を残さない
        cp.author = cp.last_modified_by = ""
        cp.title = title
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.check(strict)
        self.prs.save(str(path))
        return path


def use_chart_style():
    """matplotlib に tokens/charts.json の様式を当てる。系列の色・マーカー・線種のリストを返す。"""
    import matplotlib as mpl
    mpl.style.use(str(ROOT / "lib" / "research.mplstyle"))
    s = COLORS["series"]
    return list(zip(s["value"], s["markers"], s["linestyles"], COLORS["series-text"]["value"]))
