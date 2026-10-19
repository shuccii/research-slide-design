"""tokens/colors.json の色の組み合わせのコントラスト比を計算し、基準を満たすか確かめる。

基準(DADS [1,2]): 文字は 4.5:1 以上、線・マーカー・罫線など情報を担う非テキスト要素は 3:1 以上。
    python3 tools/contrast.py      # 不合格があれば終了コード 1
"""
import json
import sys
from pathlib import Path

C = json.loads((Path(__file__).resolve().parent.parent / "tokens/colors.json").read_text())
v = lambda k: C[k]["value"]


def lum(h):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def ratio(a, b):
    hi, lo = sorted([lum(a), lum(b)], reverse=True)
    return (hi + 0.05) / (lo + 0.05)


grounds = {"background": v("background"), "fill": v("fill")}
checks = [(k, v(k), 4.5, "文字") for k in ("ink", "ink-sub", "caption", "accent", "alert")]
checks += [(f"series-text[{i}]", h, 4.5, "文字") for i, h in enumerate(C["series-text"]["value"])]
checks += [(f"series[{i}]", h, 3.0, "線・マーカー") for i, h in enumerate(C["series"]["value"])]
checks += [("line-strong", v("line-strong"), 3.0, "構造の罫線")]
bad = 0
print(f"{'token':16} {'value':8} {'用途':10} " + " ".join(f"{g:>10}" for g in grounds))
for name, hexv, need, use in checks:
    rs = [ratio(hexv, g) for g in grounds.values()]
    ground_need = [r >= need for r in rs]
    # 系列色・罫線は白地だけで判定(fill の上には置かない)
    ok = ground_need[0] if use != "文字" else all(ground_need)
    bad += not ok
    print(f"{name:16} {hexv:8} {use:10} " + " ".join(f"{r:>9.2f}{'' if r >= need else '!'}" for r in rs) + ("" if ok else "  ← 不合格"))
print("不合格", bad, "件")
sys.exit(1 if bad else 0)
