"""派生レイアウト 6 種の見本を 16:9 と 4:3 で作る。全数値は配置確認用の架空データ(研究結果ではない)。

    uv run --no-project --with python-pptx --with lxml --with latex2mathml --with matplotlib --with numpy \\
        python examples/build_layout_gallery.py

出力: examples/out/layout_gallery/layout_gallery_{16x9,4x3}.pptx。警告が 1 件でもあれば止まる。
"""
import json
import os
import sys
import tempfile
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "research-slide-mpl"))
R = Path(__file__).resolve().parent.parent
O = R / "examples" / "out" / "layout_gallery"
A = O / "assets"
A.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(R / "lib"))
import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from research_deck import COLORS, SHAPES, Deck, measure, use_chart_style  # noqa: E402

C = lambda k: COLORS[k]["value"]  # noqa: E731
ink, accent, sub = C("ink"), C("accent"), C("ink-sub")
x = np.linspace(0, 1, 81)
truth = np.sin(2 * np.pi * x)
resA = 0.22 * np.sin(4 * np.pi * x) + 0.18 * x
resB = 0.07 * np.sin(4 * np.pi * x) + 0.04 * x
predA, predB = truth + resA, truth + resB
rmse = lambda a: float(np.sqrt(np.mean(a * a)))  # noqa: E731
SRC = ["見本データ: 配置確認用の架空データ。研究結果ではない  Sample data for layout checks"]


def fig(name, w, h, draw):
    use_chart_style()
    f, ax = plt.subplots(figsize=(w, h))
    draw(ax)
    p = A / f"{name}.png"
    f.savefig(p)
    plt.close(f)
    return p


def curve(ax, pred, label, col):
    ax.plot(x, truth, color=sub, ls="--", lw=1.5, label="真値 True")
    ax.plot(x, pred, color=col, lw=2, marker="s" if col == accent else "o", markevery=10, label=label)
    ax.set(xlabel="入力 x  Input", ylabel="応答 y  Response", xlim=(0, 1), ylim=(-1.4, 1.6))
    ax.legend(loc="upper right", fontsize=14)


def build(ratio):
    d = Deck(ratio)
    wide = ratio == "16:9"
    N = 6 if wide else 4
    tag = "16x9" if wide else "4x3"
    half = N // 2
    spec = []

    def slide(key, title, message, purpose):
        s = d.slide(title, message)
        s.sources(SRC)
        s.notes(f"レイアウト: {key}\n用途: {purpose}\n数値は配置確認用の架空データ。研究上の主張に使わない。")
        spec.append(dict(id=key, title=title[0], purpose=purpose))
        return s

    def panel(s, c, span, head, name, draw, foot=None):
        """見出し+図(+下の一言)。図の上端は見出しの高さで決める。"""
        xx, w = s.col(c, span)
        y = s.heading(xx, s.top, w, head)
        fh_foot = measure([foot], "label", w) + 0.15 if foot else 0
        fh = s.bottom - y - fh_foot
        s.image(fig(f"{name}-{tag}", w, fh, draw), xx, y, w, fh)
        if foot:
            s.text(xx, s.bottom - fh_foot + 0.15, w, fh_foot - 0.15, [foot], "label")

    # 01 matched-comparison
    s = slide("matched-comparison", ("同じ条件なら構成 B の誤差が小さい", "Config B has smaller error under the same conditions"),
              ("01 対照比較: 左右で軸・条件・表記をそろえる", "01 Matched comparison: same axes and conditions"), "対照実験、前後比較、従来法と提案法の比較")
    panel(s, 0, half, ("構成 A", "Config A"), "cmpA", lambda ax: curve(ax, predA, "構成 A", ink),
          (f"RMSE {rmse(resA):.3f}(81 点)", f"RMSE {rmse(resA):.3f} (81 points)"))
    panel(s, half, half, ("構成 B", "Config B"), "cmpB", lambda ax: curve(ax, predB, "構成 B", accent),
          (f"RMSE {rmse(resB):.3f}(81 点)", f"RMSE {rmse(resB):.3f} (81 points)"))

    # 02 small-multiples
    k = 3 if wide else 2
    s = slide("small-multiples", (f"{k} 条件の変化を共通の軸で比べる", f"Compare {k} conditions on shared axes"),
              ("02 条件の一覧: 軸の範囲と系列の意味を全パネルでそろえる", "02 Small multiples: identical axes in every panel"), "温度・試料・期間などの複数条件を一覧する")
    for i in range(k):
        def draw(ax, i=i):
            ax.plot(x, truth, color=sub, ls="--", lw=1.5)
            ax.plot(x, np.sin(2 * np.pi * x) + (0.05 + i * 0.12) * np.cos(4 * np.pi * x), color=ink, lw=2, marker="o", markevery=20)
            ax.set(xlim=(0, 1), ylim=(-1.4, 1.4), xlabel="x", ylabel="y")
            ax.set_xticks([0, 0.5, 1])
            ax.set_yticks([-1, 0, 1])
        panel(s, i * (N // k), N // k, (f"({chr(97 + i)}) 条件 {i + 1}", f"({chr(97 + i)}) Condition {i + 1}"), f"cond{i}", draw)

    # 03 overview-detail
    s = slide("overview-detail", ("全体の傾向と局所のずれを同じページで示す", "Show the overall trend and a local deviation together"),
              ("03 全体と拡大: 拡大図には範囲を明記する", "03 Overview and detail: label the zoomed range"), "ピーク、交点、外挿域など局所的な差を説明する")
    ov = 4 if wide else 2
    panel(s, 0, ov, ("(a) 全範囲", "(a) Full range"), "overview", lambda ax: curve(ax, predB, "構成 B", accent))

    def detail(ax):
        lo, hi = 0.65, 0.85
        ax.plot(x, truth, color=sub, ls="--", lw=1.5)
        ax.plot(x, predB, color=accent, lw=2, marker="s", markevery=3)
        ax.set(xlim=(lo, hi), ylim=(-1.15, -0.3), xlabel="x", ylabel="y")
        ax.locator_params(nbins=3)
    panel(s, ov, N - ov, ("(b) x = 0.65–0.85", "(b) Zoom: x = 0.65–0.85"), "detail", detail,
          ("拡大すると予測が真値より上にずれる", "The zoom shows the prediction above the truth"))

    # 04 ablation
    values, labels = [0.12, 0.19, 0.28], ["全要素", "P なし", "Q なし"]
    s = slide("ablation", ("要素 Q を除くと誤差が最も大きくなる", "Removing element Q increases the error most"),
              ("04 要素別検証: 評価点 81 点と指標 RMSE は固定", "04 Ablation: 81 points and RMSE kept fixed"), "前処理、モデル要素、データ源の寄与を検証する")

    def bars(ax):
        pos = np.arange(3)
        ax.barh(pos, values, color=[accent, ink, ink], height=0.55)
        ax.set_yticks(pos, labels)
        ax.invert_yaxis()
        ax.set(xlabel="RMSE(小さいほどよい) lower is better", xlim=(0, 0.36))
        ax.grid(axis="x", visible=False)
        for i, v in enumerate(values):
            ax.text(v + 0.008, i, f"{v:.2f}", va="center", fontsize=16, color=ink)
    panel(s, 0, half, ("誤差の比較", "Error comparison"), "ablation", bars)
    xx, w = s.col(half, half)
    y = s.heading(xx, s.top, w, ("使った要素", "Elements used"))
    s.table(xx, y, w, [[("構成", "Config"), "P", "Q"], [("全要素", "All"), ("使用", "Used"), ("使用", "Used")],
                       [("P なし", "No P"), ("除外", "Removed"), ("使用", "Used")], [("Q なし", "No Q"), ("使用", "Used"), ("除外", "Removed")]],
            col_widths=[w * 0.4, w * 0.3, w * 0.3], align=["l", "l", "l"])

    # 05 error-diagnosis
    s = slide("error-diagnosis", ("平均の誤差が小さくても残差には周期的な偏りがある", "Residuals show a periodic bias despite a small mean error") if wide else
              ("残差には周期的な偏りがある", "Residuals show a periodic bias"),
              ("05 誤差の診断: 入力に対する残差と分布を並べる", "05 Error diagnosis: residuals vs. input and their distribution"), "平均指標だけでは見えない系統誤差や外れ値を調べる")

    def residual(ax):
        ax.axhline(0, color=sub, ls="--", lw=1.5)
        ax.plot(x, resB, color=accent, lw=2, marker="s", markevery=5)
        ax.set(xlabel="入力 x  Input", ylabel="残差  Residual", ylim=(-0.09, 0.12))

    def hist(ax):
        ax.hist(resB, bins=np.linspace(-0.09, 0.12, 10), color=ink, rwidth=0.85)
        ax.set(xlabel="残差  Residual", ylabel="度数  Count")
        ax.locator_params(nbins=4)
    rs = 4 if wide else 2
    panel(s, 0, rs, ("(a) 入力に対する残差", "(a) Residual vs. input"), "residual", residual,
          ("x に応じて上下する: 系統誤差の疑い", "Varies with x: possible systematic error"))
    panel(s, rs, N - rs, ("(b) 残差の分布", "(b) Distribution"), "hist", hist)

    # 06 evidence-next
    s = slide("evidence-next", ("結論ごとに根拠と限界を結び、次の検証を決める", "Link each conclusion to evidence, limits and next step") if wide else
              ("結論・根拠・限界・次の検証", "Conclusion, evidence, limit, next step"),
              ("06 議論と次の検証: 1 行に一つの結論", "06 Evidence and next step: one conclusion per row"), "研究MTGの判断、考察、追加実験の相談に使う")
    xx, w = s.col(0, N)
    s.table(xx, s.top, w, [[("結論", "Conclusion"), ("根拠", "Evidence"), ("限界", "Limit"), ("次の検証", "Next")],
                           [("B の誤差が小さい", "B has less error"), (f"RMSE {rmse(resB):.3f}", f"A: {rmse(resA):.3f}"), ("関数 1 つ", "One function"), ("別の関数で反復", "Repeat on others")],
                           [("Q の除外で悪化", "Removing Q hurts"), ("p.4 の 0.28", "0.28 on p.4"), ("相互作用は未評価", "No interactions"), ("P と Q を同時に除く", "Remove both")]],
            col_widths=[w / 4] * 4, align=["l"] * 4)
    q = [("今回の相談: 次の検証を一つ選び、判断基準を決める", "To discuss: choose one next step and its criterion")]
    s.text(xx, s.top + s.last_table_h + 0.3, w, measure(q, "body", w), q, "body")

    path = d.save(O / f"layout_gallery_{tag}.pptx", "派生レイアウト 6 種(見本)", strict=True)
    (O / "layout-manifest.json").write_text(json.dumps(spec, ensure_ascii=False, indent=2), encoding="utf-8")
    print(path)


for r in ("16:9", "4:3"):
    build(r)
(O / "sample-data.json").write_text(json.dumps({"x": x.tolist(), "truth": truth.tolist(), "prediction_a": predA.tolist(),
                                                 "prediction_b": predB.tolist()}, ensure_ascii=False, indent=2), encoding="utf-8")
