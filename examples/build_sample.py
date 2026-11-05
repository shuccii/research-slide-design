"""見本デッキを作る(架空の合成データ。研究結果ではない)。

    uv run --no-project --with python-pptx --with lxml --with latex2mathml \
        --with matplotlib --with numpy --with scikit-learn python examples/build_sample.py

出力: examples/out/sample_16x9.pptx と sample_4x3.pptx、図の PNG。数値は全てこのスクリプトの計算結果から入れる。
1 枚に要素は 3 つまで、日本語の各文の直下に英語訳(DESIGN.md)。はみ出しなどの警告が 1 件でもあれば止まる。
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel, WhiteKernel
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "lib"))
from research_deck import SHAPES, Deck, measure, use_chart_style  # noqa: E402

OUT = ROOT / "examples" / "out"
SAMPLE = "見本データ(合成関数)。研究結果ではない"
REFS = [
    "Rasmussen, C. E.; Williams, C. K. I. Gaussian Processes for Machine Learning; MIT Press: Cambridge, MA, 2006. https://gaussianprocess.org/gpml/ (accessed 2026-10-20).",
    "Breiman, L. Random Forests. Mach. Learn. 2001, 45 (1), 5–32. https://doi.org/10.1023/A:1010933404324",
    "Pedregosa, F.; Varoquaux, G.; Gramfort, A.; et al. Scikit-learn: Machine Learning in Python. J. Mach. Learn. Res. 2011, 12, 2825–2830.",
    "Okabe, M.; Ito, K. Color Universal Design (CUD): How to Make Figures and Presentations That Are Friendly to Colorblind People. J*Fly, 2002 (rev. 2008). https://jfly.uni-koeln.de/color/ (accessed 2026-10-05).",
    "Wong, B. Points of View: Color Blindness. Nat. Methods 2011, 8 (6), 441. https://doi.org/10.1038/nmeth.1618",
]
METHODS = ["線形回帰", "ランダムフォレスト", "GPR(本手法の例)"]
LAB = {"線形回帰": "線形回帰 Linear", "ランダムフォレスト": "ランダムフォレスト RF", "GPR(本手法の例)": "GPR"}
# ページ内の出典欄は短い形(詳しい書誌は最後の文献表)
SH = {1: "[1] Rasmussen & Williams, MIT Press 2006", 2: "[2] Breiman, Mach. Learn. 2001",
      3: "[3] Pedregosa et al., JMLR 2011", 4: "[4] Okabe & Ito, J*Fly 2002", 5: "[5] Wong, Nat. Methods 2011"}


# ---------- 合成データと計算 ----------
def truth(x):
    return np.sin(2 * np.pi * x) + 0.5 * x


def make_models(seed):
    k = ConstantKernel(1.0) * RBF(0.2) + WhiteKernel(0.01)
    return [LinearRegression(), RandomForestRegressor(n_estimators=200, random_state=seed),
            GaussianProcessRegressor(kernel=k, normalize_y=True, random_state=seed)]


def dataset(n, seed, noise=0.15):
    rng = np.random.default_rng(seed)
    x = rng.uniform(0, 1, n)
    return x[:, None], truth(x) + rng.normal(0, noise, n)


def run():
    x_test = np.linspace(0, 1, 200)[:, None]
    y_test = truth(x_test.ravel())
    ns, seeds = [10, 20, 40, 80], range(5)
    curve = {m: [] for m in METHODS}
    for n in ns:
        per = {m: [] for m in METHODS}
        for sd in seeds:
            X, y = dataset(n, sd)
            for m, model in zip(METHODS, make_models(sd)):
                per[m].append(mean_squared_error(y_test, model.fit(X, y).predict(x_test)) ** 0.5)
        for m in METHODS:
            curve[m].append((np.mean(per[m]), np.std(per[m])))
    # 代表例: n = 20, seed = 0
    X, y = dataset(20, 0)
    preds, scores = {}, {}
    for m, model in zip(METHODS, make_models(0)):
        model.fit(X, y)
        p = model.predict(x_test)
        preds[m] = p
        scores[m] = dict(rmse=mean_squared_error(y_test, p) ** 0.5, mae=mean_absolute_error(y_test, p), r2=r2_score(y_test, p))
    gp = make_models(0)[2].fit(X, y)
    mu, sd = gp.predict(x_test, return_std=True)
    cover = float(np.mean(np.abs(y_test - mu) <= 1.96 * sd))
    return dict(ns=ns, curve=curve, X=X, y=y, x_test=x_test.ravel(), y_test=y_test, preds=preds,
                scores=scores, mu=mu, sd=sd, cover=cover)


# ---------- 図(貼り付け先の実寸で描く。軸名は日本語と英語の 2 行) ----------
def fig_curve(R, w, h, path):
    st = use_chart_style()
    fig, ax = plt.subplots(figsize=(w, h))
    for (c, mk, ls, tc), m in zip([st[0], st[2], st[1]], METHODS):
        mean = [a for a, _ in R["curve"][m]]
        err = [b for _, b in R["curve"][m]]
        ax.errorbar(R["ns"], mean, yerr=err, color=c, marker=mk, ls=ls, capsize=3)
        ax.annotate(LAB[m], (R["ns"][-1], mean[-1]), xytext=(6, {METHODS[1]: 10, METHODS[2]: -10}.get(m, 0)),
                    textcoords="offset points", va="center", color=tc, fontsize=14)
    ax.set_xscale("log")
    ax.set_xticks(R["ns"], [str(n) for n in R["ns"]])
    ax.minorticks_off()
    ax.set_xlim(8, 400 if w > 6 else 600)
    ax.set_ylim(0, None)
    ax.set_xlabel("学習データ数 n [点]  Training size n")
    ax.set_ylabel("RMSE(小さいほどよい)\nRMSE (lower is better)")
    fig.savefig(path)
    plt.close(fig)


def fig_parity(R, w, h, path):
    st = use_chart_style()
    fig, ax = plt.subplots(figsize=(w, h))
    lo, hi = -1.3, 1.8
    ax.plot([lo, hi], [lo, hi], color="#595959", ls="--", lw=1)
    for (c, mk, ls, tc), m in zip([st[0], st[2], st[1]], METHODS):
        ax.plot(R["y_test"][::8], R["preds"][m][::8], ls="none", marker=mk, color=c, mfc="none" if m != METHODS[2] else c,
                label=LAB[m].split(" ")[-1])
    ax.set_xlim(lo, hi)
    ax.set_ylim(lo, hi)
    ax.set_aspect("equal")
    ax.grid(False)
    ax.set_xlabel("真値  True")
    ax.set_ylabel("予測値  Predicted")
    ax.legend(loc="lower right", handletextpad=0.2, borderaxespad=0.1, fontsize=14)
    fig.savefig(path)
    plt.close(fig)


def fig_band(R, w, h, path):
    st = use_chart_style()
    fig, ax = plt.subplots(figsize=(w, h))
    x = R["x_test"]
    ax.fill_between(x, R["mu"] - 1.96 * R["sd"], R["mu"] + 1.96 * R["sd"], color="#0072B2", alpha=0.15, lw=0)
    ax.plot(x, R["y_test"], color=st[0][0], ls="--", lw=1.5)
    ax.plot(x, R["mu"], color=st[1][0], lw=2)
    ax.plot(R["X"].ravel(), R["y"], ls="none", marker="o", color="#1A1A1A", ms=5)
    ax.annotate("真の関数 True", (0.86, truth(0.86)), xytext=(0.45, -1.3), color="#1A1A1A", fontsize=14,
                arrowprops=dict(arrowstyle="-", color="#595959", lw=0.8))
    ax.set_ylim(-1.5, 1.8)
    ax.set_xlabel("記述子 x  Descriptor")
    ax.set_ylabel("目的変数 y  Target")
    fig.savefig(path)
    plt.close(fig)


def fig_sigma(R, w, h, path):
    st = use_chart_style()
    fig, ax = plt.subplots(figsize=(w, h))
    x = R["x_test"]
    err = np.abs(R["y_test"] - R["mu"])
    ax.plot(x, R["sd"], color=st[1][0], lw=2)
    ax.plot(x, err, color=st[0][0], ls="--", lw=1.5)
    top = float(max(R["sd"].max(), err.max())) * 1.2
    ax.plot(R["X"].ravel(), np.full(len(R["X"]), top * 0.02), ls="none", marker="|", color="#1A1A1A", ms=10)
    i = int(np.argmax(R["sd"]))
    ax.annotate("σ", (x[i], R["sd"][i]), xytext=(x[i] - 0.15, R["sd"][i] + top * 0.05), color="#0072B2", fontsize=16,
                arrowprops=dict(arrowstyle="-", color="#0072B2", lw=0.8))
    ax.set_ylim(0, top)
    ax.set_xlabel("記述子 x  Descriptor")
    ax.set_ylabel("σ と |誤差|\nσ and |error|")
    fig.savefig(path)
    plt.close(fig)


# ---------- スライド(16:9 は 6 カラム、4:3 は 4 カラム) ----------
def build(ratio):
    R = RUN
    OUT.mkdir(parents=True, exist_ok=True)
    d = Deck(ratio)
    wide = ratio == "16:9"
    N = 6 if wide else 4
    tag = "16x9" if wide else "4x3"
    sc = R["scores"]
    gpr, lin = sc[METHODS[2]], sc[METHODS[0]]
    cov = f"{R['cover'] * 100:.0f}%"
    pct = f"{(1 - gpr['rmse'] / lin['rmse']) * 100:.0f}%"

    # 1 cover
    d.cover(("少量データで不確かさも示す(見本)", "Report uncertainty with small data (sample)"),
            ("合成データによる見本。研究結果ではない", "Synthetic-data sample, not research results"),
            ["発表者 氏名  所属・学会名・発表日"],
            [("n = 20 で GPR の誤差が最小", "GPR has the smallest error at n = 20"),
             (f"95% 区間に {cov} の点が入る", f"The 95% interval covers {cov} of points")])

    # 2 figure-notes: 図 + 要点数値
    s = d.slide(("少量データでは GPR の誤差が最小", "GPR has the smallest error with small data"),
                ("予測誤差 RMSE を 3 手法で比べた", "Prediction error (RMSE) of three methods"))
    fs = 4 if wide else 2
    x, w = s.col(0, fs)
    cap = ("GPR = ガウス過程回帰。見本データ、誤差棒 ±1σ", "GPR: Gaussian process regression. Sample data; bars ±1σ")
    fh = s.bottom - s.top - measure([cap], "label", w) - 0.1
    fig_curve(R, w, fh, OUT / f"curve-{tag}.png")
    s.image(OUT / f"curve-{tag}.png", x, s.top, w, fh, credit=cap)
    x, w = s.col(fs, N - fs)
    s.number_box(x, s.top, w, ("GPR の RMSE(n = 20)", "GPR RMSE at n = 20"), f"{gpr['rmse']:.3f}",
                 (f"線形回帰は {lin['rmse']:.3f}", f"Linear: {lin['rmse']:.3f}"), accent=True)
    s.sources([SH[1], SH[2]])

    # 3 method: 流れ + 式 2 本
    s = d.slide(("GPR は予測の平均と分散を同時に返す", "GPR returns both the mean and the variance"),
                ("手法の流れと、予測に使う 2 つの式", "Workflow and the two predictive equations"))
    stages = [("データ生成", "Data"), ("学習", "Training"), ("予測", "Prediction"), ("評価", "Evaluation")]
    g = 0.45
    bw = (s.width - g * 3) / 4
    bh = measure([stages[0]], "heading", bw) + 0.35
    for i, st in enumerate(stages):
        bx = s.margin + i * (bw + g)
        s.box(bx, s.top, bw, bh, r=SHAPES["radius_in"]["medium"], fill=None, line="ink", pt=1.25)
        s.text(bx, s.top, bw, bh, [st], "heading", align="center", anchor="middle")
        if i < 3:
            s.arrow(bx + bw + 0.06, s.top + bh / 2, bx + bw + g - 0.06, s.top + bh / 2)
    s.pill(s.margin + 2 * (bw + g), s.top + bh + 0.15, "平均と分散", size=16)
    ex, ew = s.col(0, N)
    ey = s.top + bh + 0.75
    s.equation(r"\bar{f}_{*} = \mathbf{k}_{*}^{\top}\left(K + \sigma_{n}^{2} I\right)^{-1}\mathbf{y}", ex, ey, ew, 0.7, number=1)
    s.equation(r"\mathbb{V}[f_{*}] = k(\mathbf{x}_{*}, \mathbf{x}_{*}) - \mathbf{k}_{*}^{\top}\left(K + \sigma_{n}^{2} I\right)^{-1}\mathbf{k}_{*}", ex, ey + 0.8, ew, 0.7, number=2)
    note = ("(1) 予測の平均、(2) 予測の分散(不確かさ)[1]。記号は p.4", "(1) predictive mean; (2) predictive variance (uncertainty) [1]. Symbols on p.4")
    s.text(ex, ey + 1.65, ew, measure([note], "label", ew), [note], "label")
    s.sources([SH[1]])
    s.notes("式は代替テキストに LaTeX を保存してある(tools/latex_eq.py --extract で一覧)。")

    # 4 equation の記号表 + 条件
    s = d.slide(("式 (1)(2) の記号と計算条件", "Symbols in Eqs. (1)(2) and conditions"),
                ("p.3 の式で使う記号の意味", "Meaning of the symbols on p.3") if wide else
                ("条件: テスト 200 点、乱数 5 回、雑音 σ = 0.15", "200 test points, 5 seeds, noise σ = 0.15"))
    rows = [[("記号", "Symbol"), ("意味", "Meaning")], ["x*", ("予測したい点の記述子", "Descriptor of the query point")],
            ["k*", ("学習点と x* の共分散", "Covariance between training points and x*")],
            ["K", ("学習点どうしの共分散行列", "Covariance matrix of training points")], ["σn²", ("観測雑音の分散", "Noise variance")]]
    cond = [("条件", "Conditions"), ("テスト 200 点", "200 test points"), ("乱数 5 回", "5 random seeds"), ("雑音 σ = 0.15", "Noise σ = 0.15")]
    if wide:
        x, w = s.col(0, 4)
        s.table(x, s.top, w, rows, col_widths=[w * 0.2, w * 0.8], align=["l", "l"])
        x, w = s.col(4, 2)
        h = measure(cond, "body", w - 0.4, spacing=6) + 0.4
        s.box(x, s.top, w, h)
        s.text(x + 0.2, s.top + 0.2, w - 0.4, h - 0.4, cond, "body", spacing=6)
    else:
        x, w = s.col(0, 4)
        s.table(x, s.top, w, rows, col_widths=[w * 0.2, w * 0.8], align=["l", "l"])  # 4:3 は条件を一言メッセージへ
    s.sources([SH[1], SH[3]])

    # 5 two-figures: 16:9 は 3 枚、4:3 は 2 枚
    s = d.slide(("GPR は学習点のない端で σ が大きい", "GPR's σ grows where training points are absent"),
                ("n = 20・乱数 0 の代表例。同じ予測から作図", "Representative case (n = 20, seed 0) from the same prediction"))
    panels = [(("(a) 予測値と真値", "(a) Predicted vs. true"), fig_parity, "parity"),
              (("(b) 平均と 95% 区間", "(b) Mean and 95% interval"), fig_band, "band"),
              (("(c) σ と |誤差|", "(c) σ and |error|"), fig_sigma, "sigma")]
    if not wide:
        panels = panels[1:]  # 4:3 は 2 枚まで。(a) は p.2 の数値で代える
    span = N // len(panels)
    cap = ("見本データ。(b) の帯は平均 ± 1.96σ、(c) の下端の縦線は学習点", "Sample data. Band in (b): mean ± 1.96σ; ticks in (c): training points")
    ch = measure([cap], "label", s.width)
    hh = max(measure([p[0]], "heading", s.col(0, span)[1]) for p in panels) + 0.11  # 見出しの高さをそろえて図の上端を合わせる
    for k, (ttl, fn, name) in enumerate(panels):
        x, w = s.col(k * span, span)
        s.heading(x, s.top, w, ttl)
        y = s.top + hh
        fh = s.bottom - y - ch - 0.15
        fn(R, w, fh, OUT / f"{name}-{tag}.png")
        s.image(OUT / f"{name}-{tag}.png", x, y, w, fh)
    s.text(s.margin, s.bottom - ch, s.width, ch, [cap], "label")
    s.sources([SH[1], SH[3]])

    # 6 comparison-table
    s = d.slide(("データが増えると手法の差は縮む", "The gap between methods closes with more data"),
                ("テスト RMSE の平均(下段は ±1σ、5 回)。小さいほどよい", "Mean test RMSE (±1σ below, 5 seeds). Lower is better"))
    ns = R["ns"] if wide else R["ns"][1:]
    rows = [[("手法", "Method")] + [f"n = {n}" for n in ns]]
    for m in METHODS:
        c = dict(zip(R["ns"], R["curve"][m]))
        ja = m.replace("(本手法の例)", "")
        en = LAB[m].split(" ")[-1]
        rows.append([(ja, en) if en != ja else ja] + [(f"{c[n][0]:.3f}", f"±{c[n][1]:.3f}") for n in ns])
    x, w = s.col(0, N)
    fw = w * (0.28 if wide else 0.34)
    s.table(x, s.top, w, rows, col_widths=[fw] + [(w - fw) / len(ns)] * len(ns), bold_cells={(3, 2 if wide else 1)})
    read = [("読み方: n = 20 では GPR が最小、n = 80 では RF との差が小さい", "At n = 20 GPR is lowest; at n = 80 the gap to RF is small")]
    if not wide:
        s.notes("4:3 は列を 4 つまでにするため n = 10 を省いた(16:9 版の表にある)。")
    s.text(x, s.top + s.last_table_h + 0.25, w, measure(read, "label", w), read, "label")
    s.sources([SH[1], SH[2], SH[3]])

    # 7 summary
    s = d.slide(("少量データでは不確かさも示す", "With small data, report uncertainty too"),
                ("p.2–6 の結論と限界", "Conclusions and limitation of pp. 2–6"))
    cs = 3 if wide else 2
    x, w = s.col(0, cs)
    y = s.heading(x, s.top, w, ("結論", "Conclusions"))
    items = [(f"・誤差は線形回帰より {pct} 小さい(p.2)", f"Error is {pct} below linear (p.2)"),
             ("・データが増えると差は縮む(p.6)", "The gap closes with more data (p.6)")]
    if wide:
        items.append((f"・95% 区間に {cov} の点が入る", f"The 95% interval covers {cov} of points"))
    s.text(x, y, w, measure(items, "body", w, spacing=14), items, "body", spacing=14)
    x, w = s.col(cs, N - cs)
    y = s.number_box(x, s.top, w, ("GPR の RMSE(n = 20)", "GPR RMSE at n = 20"), f"{gpr['rmse']:.3f}",
                     (f"線形回帰は {lin['rmse']:.3f}", f"Linear: {lin['rmse']:.3f}"), accent=True)
    lim = [("{bold|限界} {alert|1 次元の例だけ}", "Limitation: 1-D example only")]
    lh = measure(lim, "body", w - 0.4) + 0.4
    s.box(x, y + SHAPES["gap_in"], w, lh, fill=None, line="alert", pt=1.25)
    s.text(x + 0.2, y + SHAPES["gap_in"] + 0.2, w - 0.4, lh - 0.4, lim, "body")
    s.sources([SH[1], SH[2], SH[3]])

    # 8 references
    d.references(REFS)
    path = d.save(OUT / f"sample_{tag}.pptx", "研究スライド デザインシステム 見本", strict=True)
    print(path)
    return path


if __name__ == "__main__":
    RUN = run()
    for r in ("16:9", "4:3"):
        build(r)
