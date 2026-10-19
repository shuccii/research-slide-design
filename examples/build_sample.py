"""見本デッキを作る(架空の合成データ。研究結果ではない)。

    uv run --no-project --with python-pptx --with lxml --with latex2mathml \
        --with matplotlib --with numpy --with scikit-learn python examples/build_sample.py

出力: examples/out/sample_16x9.pptx と図の PNG。数値は全てこのスクリプトの計算結果から入れる。
余白は「文字・図を大きくする → それでも空けば情報を足す」の順で埋めている(DESIGN.md の版面)。
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
from research_deck import Deck, use_chart_style  # noqa: E402

OUT = ROOT / "examples" / "out"
SAMPLE = "見本データ(合成関数)。研究結果ではない"
REFS = [
    "Rasmussen, C. E.; Williams, C. K. I. Gaussian Processes for Machine Learning; MIT Press: Cambridge, MA, 2006. https://gaussianprocess.org/gpml/ (accessed 2026-10-20).",
    "Breiman, L. Random Forests. Mach. Learn. 2001, 45 (1), 5–32. https://doi.org/10.1023/A:1010933404324",
    "Pedregosa, F.; Varoquaux, G.; Gramfort, A.; et al. Scikit-learn: Machine Learning in Python. J. Mach. Learn. Res. 2011, 12, 2825–2830.",
    "Okabe, M.; Ito, K. Color Universal Design (CUD): How to Make Figures and Presentations That Are Friendly to Colorblind People. J*Fly, 2002 (rev. 2008). https://jfly.uni-koeln.de/color/ (accessed 2026-10-05).",
    "Wong, B. Points of View: Color Blindness. Nat. Methods 2011, 8 (6), 441. https://doi.org/10.1038/nmeth.1618",
]
SHORT = {
    1: "[1] Rasmussen, C. E.; Williams, C. K. I. Gaussian Processes for Machine Learning; MIT Press, 2006.",
    2: "[2] Breiman, L. Mach. Learn. 2001, 45, 5–32.",
    3: "[3] Pedregosa, F. et al. J. Mach. Learn. Res. 2011, 12, 2825–2830.",
    4: "[4] Okabe, M.; Ito, K. J*Fly, 2002 (rev. 2008).",
}
METHODS = ["線形回帰", "ランダムフォレスト", "GPR(本手法の例)"]


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


# ---------- 図(貼り付け先の実寸で描く) ----------
def fig_curve(R, w, h, path):
    st = use_chart_style()
    fig, ax = plt.subplots(figsize=(w, h))
    for (c, mk, ls, tc), m in zip([st[0], st[2], st[1]], METHODS):
        mean = [a for a, _ in R["curve"][m]]
        err = [b for _, b in R["curve"][m]]
        ax.errorbar(R["ns"], mean, yerr=err, color=c, marker=mk, ls=ls, capsize=3)
        ax.annotate(m, (R["ns"][-1], mean[-1]), xytext=(6, 0), textcoords="offset points", va="center", color=tc)
    ax.set_xscale("log")
    ax.set_xticks(R["ns"], [str(n) for n in R["ns"]])
    ax.minorticks_off()
    ax.set_xlim(8, 300)
    ax.set_ylim(0, None)
    ax.set_xlabel("学習データ数 n [点]")
    ax.set_ylabel("テスト RMSE [任意単位]")
    fig.savefig(path)
    plt.close(fig)


def fig_parity(R, w, h, path):
    st = use_chart_style()
    fig, ax = plt.subplots(figsize=(w, h))
    lo, hi = -1.3, 1.8
    ax.plot([lo, hi], [lo, hi], color="#595959", ls="--", lw=1)
    for (c, mk, ls, tc), m in zip([st[0], st[2], st[1]], METHODS):
        ax.plot(R["y_test"][::8], R["preds"][m][::8], ls="none", marker=mk, color=c, mfc="none" if m != METHODS[2] else c, label=m)
    ax.set_xlim(lo, hi)
    ax.set_ylim(lo, hi)
    ax.set_aspect("equal")
    ax.grid(False)
    ax.set_xlabel("真値 [任意単位]")
    ax.set_ylabel("予測値 [任意単位]")
    ax.legend(loc="upper left", handletextpad=0.2, borderaxespad=0.1)
    fig.savefig(path)
    plt.close(fig)


def fig_sigma(R, w, h, path):
    st = use_chart_style()
    fig, ax = plt.subplots(figsize=(w, h))
    x = R["x_test"]
    err = np.abs(R["y_test"] - R["mu"])
    ax.plot(x, R["sd"], color=st[1][0], lw=1.5)
    ax.plot(x, err, color=st[0][0], ls="--", lw=1.0)
    top = float(max(R["sd"].max(), err.max())) * 1.15
    ax.plot(R["X"].ravel(), np.full(len(R["X"]), top * 0.02), ls="none", marker="|", color="#1A1A1A", ms=10)
    i = int(np.argmax(R["sd"]))
    ax.annotate("σ", (x[i], R["sd"][i]), xytext=(x[i] - 0.12, R["sd"][i] + top * 0.06), color="#0072B2",
                arrowprops=dict(arrowstyle="-", color="#0072B2", lw=0.8))
    j = int(np.argmax(err))
    ax.annotate("|誤差|", (x[j], err[j]), xytext=(x[j] + 0.1, err[j] + top * 0.02), color="#1A1A1A",
                arrowprops=dict(arrowstyle="-", color="#595959", lw=0.8))
    ax.set_ylim(0, top)
    ax.set_xlabel("記述子 x [任意単位]")
    ax.set_ylabel("σ, |誤差| [任意単位]")
    fig.savefig(path)
    plt.close(fig)


def fig_band(R, w, h, path):
    st = use_chart_style()
    fig, ax = plt.subplots(figsize=(w, h))
    x = R["x_test"]
    ax.fill_between(x, R["mu"] - 1.96 * R["sd"], R["mu"] + 1.96 * R["sd"], color="#0072B2", alpha=0.15, lw=0)
    ax.plot(x, R["y_test"], color=st[0][0], ls="--", lw=1.2)
    ax.plot(x, R["mu"], color=st[1][0], lw=1.5)
    ax.plot(R["X"].ravel(), R["y"], ls="none", marker="o", color="#1A1A1A", ms=4)
    ax.annotate("真の関数", (0.86, truth(0.86)), xytext=(0.6, -1.25), color="#1A1A1A", arrowprops=dict(arrowstyle="-", color="#595959", lw=0.8))
    ax.annotate("GPR 平均と 95% 区間", (0.30, R["mu"][60]), xytext=(0.35, 1.45), color="#0072B2", arrowprops=dict(arrowstyle="-", color="#0072B2", lw=0.8))
    ax.set_ylim(-1.5, 1.8)
    ax.set_xlabel("記述子 x [任意単位]")
    ax.set_ylabel("目的変数 y [任意単位]")
    fig.savefig(path)
    plt.close(fig)


# ---------- スライド(16:9) ----------
def build():
    R = run()
    OUT.mkdir(parents=True, exist_ok=True)
    d = Deck("16:9")
    sc = R["scores"]
    gpr, lin, rf = sc[METHODS[2]], sc[METHODS[0]], sc[METHODS[1]]
    cov = f"{R['cover'] * 100:.0f}%"

    # 1 cover: 左 7 カラムに題、右 5 カラムに要点と主要文献
    s = d.blank()
    x, w = s.col(0, 7)
    s.rule(x, 1.6, 0.9, "ink", 1.0)
    s.text(x, 1.75, w, 1.9, ["少量データの回帰で", "予測の不確かさまで示す(見本)"], "cover-title", size=34)
    s.text(x, 3.75, w, 0.9, ["研究・高密度デザインシステムの見本デッキ", "架空の合成データで作成。研究結果ではない"], "cover-sub", size=18)
    s.rule(x, 5.0, w, "line-strong", 0.5)
    s.text(x, 5.15, w, 1.5, ["発表者 氏名", "所属・学会名・発表日"], "body", size=20)
    x, w = s.col(7, 5)
    s.heading(x, 1.6, w, "本発表の要点", size=18)
    s.bullets(x, 2.0, w, 2.6, [f"n = 20 のテスト RMSE は GPR が最小({gpr['rmse']:.3f})",
                                f"GPR の 95% 区間はテスト点の {cov} を含む",
                                "データが増えると手法間の差は縮む"], size=20, spacing=10)
    s.heading(x, 5.0, w, "主要文献", size=16)
    s.text(x, 5.4, w, 1.3, [SHORT[1], SHORT[2], SHORT[3]], "label", size=13, spacing=3)

    # 2 figure-notes: 図 7 : 右 5(要点数値 2・読み取り・条件表)
    s = d.slide("学習データが 20 点以下では GPR の RMSE が最も小さい(見本)",
                "3 手法のテスト RMSE を学習データ数ごとに比べる。5 回の乱数で平均 ± 標準偏差")
    x, w = s.col(0, 7)
    fh = s.bottom - s.top - 0.32
    fig_curve(R, w, fh, OUT / "curve.png")
    s.image(OUT / "curve.png", x, s.top, w, fh, credit=f"{SAMPLE}。誤差棒は ±1σ(5 回)")
    x, w = s.col(7, 5)
    s.number(x, s.top, w / 2 - 0.1, "RMSE(GPR, n = 20)", f"{gpr['rmse']:.3f}", f"線形回帰は {lin['rmse']:.3f}", accent=True, size=36, label_size=14)
    s.number(x + w / 2, s.top, w / 2, "95% 区間の被覆率", cov, "テスト 200 点のうち区間内", size=36, label_size=14)
    s.rule(x, s.top + 1.42, w, "line-strong", 0.5)
    s.bullets(x, s.top + 1.55, w, 2.2, ["n = 10 では GPR の ばらつきが大きい(±1σ)",
                                         "n が増えると RF と GPR の差は縮む",
                                         "線形回帰は n を増やしても下がらない({alert|モデルの形が合わない})"], size=18)
    s.table(x, s.bottom - 1.6, w, [["条件", "値"], ["テスト点", "200 点(等間隔)"], ["乱数", "5 回(seed 0–4)"], ["観測雑音 σ", "0.15"]],
            col_widths=[w * 0.45, w * 0.55], align=["l", "l"], row_h=0.4, size=15)
    s.sources([SHORT[1], SHORT[2], SHORT[3]])

    # 3 method: 5 段階の流れ+式 7 : 変数表 5+条件表
    s = d.slide("GPR は予測の平均と分散を同時に返す", "見本で使う手法の流れ・式・条件")
    stages = [("データ生成", "合成関数+雑音", "n = 10–80 点"), ("学習", "3 手法を同じ", "データで学習 [3]"),
              ("予測", "テスト 200 点で", "平均と分散"), ("評価", "RMSE・MAE・R²", "95% 区間の被覆率"), ("比較", "学習曲線と", "パリティ図")]
    sw = (s.width + 0.15) / 5
    for i, (name, a, b) in enumerate(stages):
        x = s.margin + i * sw
        s.rule(x, s.top, sw - 0.45, "ink", 2)
        s.heading(x, s.top + 0.1, sw - 0.45, name, size=18)
        s.text(x, s.top + 0.5, sw - 0.45, 0.7, [a, b], "label", size=14)
        if i < 4:
            s.arrow(x + sw - 0.4, s.top + 0.28, x + sw - 0.08, s.top + 0.28)
    ex, ew = s.col(0, 7)
    s.equation(r"\bar{f}_{*} = \mathbf{k}_{*}^{\top}\left(K + \sigma_{n}^{2} I\right)^{-1}\mathbf{y}", ex, 2.45, ew, 0.8, number=1, size=24)
    s.equation(r"\mathbb{V}[f_{*}] = k(\mathbf{x}_{*}, \mathbf{x}_{*}) - \mathbf{k}_{*}^{\top}\left(K + \sigma_{n}^{2} I\right)^{-1}\mathbf{k}_{*}", ex, 3.3, ew, 0.8, number=2, size=24)
    s.text(ex, 4.18, ew, 0.3, "式 (1)(2) は GPR の予測平均と予測分散 [1]。95% 区間は平均 ± 1.96σ", "label", size=14)
    vx, vw = s.col(7, 5)
    s.table(vx, 2.4, vw, [["記号", "意味", "単位"], ["x*", "予測したい点の記述子", "任意"], ["k*", "学習点と x* の共分散", "–"],
                          ["K", "学習点どうしの共分散行列", "–"], ["σn²", "観測雑音の分散", "任意²"], ["y", "学習データの目的変数", "任意"]],
            col_widths=[vw * 0.17, vw * 0.63, vw * 0.2], align=["l", "l", "l"], row_h=0.36, size=14)
    fx, fw = s.col(0, 12)
    s.table(fx, 4.65, fw, [["項目", "設定"], ["データ", "y = sin(2πx) + 0.5x + ε、x ~ U(0, 1)、ε ~ N(0, 0.15²)"],
                           ["カーネル", "定数 × RBF(初期長さ 0.2)+ 白色雑音。目的変数は正規化"],
                           ["比較手法", "線形回帰、ランダムフォレスト(200 本)[2]"],
                           ["評価", "テスト 200 点の RMSE・MAE・R²、95% 区間の被覆率"]],
            col_widths=[1.8, fw - 1.8], align=["l", "l"], row_h=0.4, size=15)
    s.sources([SHORT[1], SHORT[2], SHORT[3]])
    s.notes("式は代替テキストに LaTeX を保存してある(tools/latex_eq.py --extract で一覧)。")

    # 4 two-figures(16:9 は 3 枚): パリティ / 予測帯 / 誤差と σ
    s = d.slide("GPR は真の関数に沿い、学習点のない端で σ が大きくなる", "n = 20、乱数 0 の代表例。(a)(b)(c) は同じ予測から作図")
    fh = 3.35
    for k, (ttl, fn, name) in enumerate([("(a) 予測値と真値", fig_parity, "parity"),
                                         ("(b) GPR の平均と 95% 区間", fig_band, "band"),
                                         ("(c) GPR の σ と |誤差|", fig_sigma, "sigma")]):
        x, w = s.col(k * 4, 4)
        s.heading(x, s.top, w, ttl, size=16)
        fn(R, w, fh, OUT / f"{name}.png")
        s.image(OUT / f"{name}.png", x, s.top + 0.36, w, fh)
    s.text(s.margin, s.top + 0.4 + fh, s.width, 0.26, f"{SAMPLE}。破線は y = x(a)と真の関数(b)。(c) の下端の縦線は学習点の位置。帯は平均 ± 1.96σ", "label", size=13)
    fx, fw = s.col(0, 12)
    s.table(fx, 5.15, fw, [["手法", "RMSE", "MAE", "R²", "不確かさ"],
                           *[[m, f"{sc[m]['rmse']:.3f}", f"{sc[m]['mae']:.3f}", f"{sc[m]['r2']:.2f}", "あり(式 2)" if m == METHODS[2] else "なし"] for m in METHODS]],
            col_widths=[fw * 0.32, fw * 0.17, fw * 0.17, fw * 0.17, fw * 0.17], align=["l", "r", "r", "r", "l"],
            bold_cells={(3, 1)}, row_h=0.42, size=15)
    s.sources([SHORT[1], SHORT[3]])

    # 5 dense-table
    s = d.slide("データ数ごとの RMSE: 差は n = 10–20 で大きく、n = 80 で縮む", "5 回の乱数の平均 ± 標準偏差。値が小さいほどよい")
    rows = [["手法"] + [f"n = {n}" for n in R["ns"]] + ["n = 10 → 80"]]
    for m in METHODS:
        c = R["curve"][m]
        rows.append([m] + [f"{a:.3f} ± {b:.3f}" for a, b in c] + [f"{(c[-1][0] / c[0][0] - 1) * 100:+.0f}%"])
    x, w = s.col(0, 12)
    s.table(x, s.top, w, rows, col_widths=[w * 0.24] + [w * 0.155] * 4 + [w * 0.14], row_h=0.55, size=16)
    s.text(x, s.top + 2.26, w, 0.26, f"{SAMPLE}。テスト RMSE [任意単位]。表は色なし・黒罫線", "label", size=13)
    y0 = s.top + 2.68
    for i, (h, body) in enumerate([("この表から言えること", ["少量データでは GPR が最小", "線形回帰は n を増やしても改善しない"]),
                                    ("記号", ["n: 学習データ数", "±: 5 回の標準偏差"]),
                                    ("関連文献", ["GPR [1]、RF [2]", "実装 scikit-learn [3]"])]):
        x, w = s.col(i * 4, 4)
        s.heading(x, y0, w, h, size=18)
        s.bullets(x, y0 + 0.42, w, 1.1, body, size=18, spacing=4)
    y1 = y0 + 1.55
    s.rule(s.margin, y1 - 0.1, s.width, "line-strong", 0.5)
    for i, m in enumerate(METHODS):
        c = R["curve"][m]
        x, w = s.col(i * 4, 4)
        s.number(x, y1, w, m, f"{(c[-1][0] / c[0][0] - 1) * 100:+.0f}%", "RMSE の変化(n = 10 → 80)", accent=(m == METHODS[2]), size=32, label_size=14)
    s.sources([SHORT[1], SHORT[2], SHORT[3]])

    # 6 summary: 結論 5 / 主要数値 4 / 課題・限界 3、下段に関連文献
    s = d.slide("まとめ: 少量データでは予測の不確かさを一緒に示す", "見本デッキの結論と限界")
    x, w = s.col(0, 5)
    s.heading(x, s.top, w, "結論", size=18)
    s.bullets(x, s.top + 0.42, w, 3.2, [f"n = 20 で GPR の RMSE は {gpr['rmse']:.3f}、線形回帰の約 1/{lin['rmse'] / gpr['rmse']:.0f}(p.4)",
                                        "RF との差は n = 80 で縮む(p.5)",
                                        f"95% 区間はテスト点の {cov} を含む(p.2, p.4)"], size=20, spacing=10)
    x, w = s.col(5, 4)
    s.heading(x, s.top, w, "主要数値", size=18)
    y = s.top + 0.42
    for lab, val, note, acc in [("RMSE(GPR, n = 20)", f"{gpr['rmse']:.3f}", f"線形回帰 {lin['rmse']:.3f}", True),
                                ("RMSE(RF, n = 20)", f"{rf['rmse']:.3f}", "ランダムフォレスト", False),
                                ("95% 区間の被覆率", cov, "テスト 200 点", False)]:
        y = s.number(x, y, w, lab, val, note, accent=acc, size=30, label_size=14) + 0.12
    x, w = s.col(9, 3)
    s.heading(x, s.top, w, "次の課題", size=18)
    s.bullets(x, s.top + 0.42, w, 1.4, ["実データで同じ比較", "記述子を多次元に"], size=18, spacing=4)
    s.heading(x, s.top + 1.75, w, "限界", size=18)
    s.bullets(x, s.top + 2.17, w, 1.4, ["{alert|1 次元の合成関数のみ}", "ハイパーパラメータ探索なし"], size=18, spacing=4)
    s.rule(s.margin, 5.05, s.width, "line-strong", 0.5)
    s.heading(s.margin, 5.15, s.width, "関連文献", size=16)
    s.text(s.margin, 5.55, s.width, 1.3, [SHORT[1], SHORT[2], SHORT[3]], "label", size=16, spacing=4)
    s.sources(["色の設計: " + SHORT[4]])

    # 7 references: 3 段組+図表の出典表
    s = d.slide("参考文献", "本文の登場順。DOI と Web 資料の確認日つき")
    for c in range(3):
        x, w = s.col(c * 4, 4)
        chunk = [(k, r) for k, r in enumerate(REFS, 1) if (k - 1) // 2 == c]
        s.text(x, s.top, w, 3.2, [f"[{k}] {r}" for k, r in chunk], "caption", size=12, spacing=8)
    fx, fw = s.col(0, 12)
    s.heading(fx, 4.15, fw, "図表の出典", size=18)
    s.table(fx, 4.6, fw, [["ページ", "図表", "区分"], ["2", "学習曲線", "見本データ(本スクリプトで作成)"],
                          ["4", "(a)(b)(c) と結果表", "見本データ(本スクリプトで作成)"], ["5", "RMSE の表", "見本データ(本スクリプトで作成)"]],
            col_widths=[1.2, 4.0, fw - 5.2], align=["l", "l", "l"], row_h=0.5, size=16)
    path = d.save(OUT / "sample_16x9.pptx", "研究・高密度デザインシステム 見本")
    print(path)
    return path


if __name__ == "__main__":
    build()
