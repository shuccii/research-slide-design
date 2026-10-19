#!/bin/zsh
# SVG を Inkscape で PDF と PNG に書き出し、壊れていないかと最小の文字サイズを確かめる。
# usage: export_svg.sh figure.svg [貼り付け幅 in=12.53] [dpi=300]
#   貼り付け幅は、スライドに貼ったときの図の幅(16:9 の本文幅は 12.53 in)。最小文字を pt に換算して表示する。
set -eu
[[ $# -ge 1 ]] || { echo "usage: $0 figure.svg [width_in=12.53] [dpi=300]" >&2; exit 2; }
svg="$1"; width_in="${2:-12.53}"; dpi="${3:-300}"
[[ -f "$svg" ]] || { echo "not found: $svg"; exit 1; }
command -v inkscape >/dev/null || { echo "inkscape が必要です(brew install --cask inkscape)"; exit 1; }
python3 -c "import sys,xml.dom.minidom; xml.dom.minidom.parse(sys.argv[1])" "$svg" && echo "xml ok"
check_pdf() {
  python3 - "$1" <<'PY'
import sys
from pathlib import Path
b = Path(sys.argv[1]).read_bytes()
if not b.startswith(b'%PDF-') or not b.rstrip().endswith(b'%%EOF'):
    raise SystemExit(f'不完全な PDF: {sys.argv[1]}')
PY
}
pdf="${svg%.svg}.pdf"
# Inkscape は終了コード 0 でも PDF が途中で切れることがある。その場合は文字をパス化して 1 回だけ出し直す(SVG は編集できるまま)
if ! inkscape "$svg" --export-type=pdf --export-filename="$pdf" || ! check_pdf "$pdf"; then
  echo "PDF を文字のパス化で出し直します(SVG の文字は編集可能なまま)" >&2
  inkscape "$svg" --export-type=pdf --export-text-to-path --export-filename="$pdf"
  check_pdf "$pdf"
fi
inkscape "$svg" --export-type=png --export-dpi="$dpi" --export-filename="${svg%.svg}.png"
python3 - "$svg" "$width_in" <<'PY'
import re, sys, xml.etree.ElementTree as ET
svg, width_in = sys.argv[1], float(sys.argv[2])
root = ET.parse(svg).getroot()
vb = [float(v) for v in root.get("viewBox").split()]
pt_per_unit = width_in * 72 / vb[2]
sizes = []
for el in root.iter():
    fs = el.get("font-size") or (re.search(r"font-size:\s*([\d.]+)", el.get("style", "")) or [None, None])[1]
    if fs and el.tag.endswith(("text", "tspan")):
        sizes.append(float(fs))
if sizes:
    m = min(sizes) * pt_per_unit
    print(f"最小の文字: {min(sizes)} (viewBox 単位) = {m:.1f} pt(幅 {width_in} in に貼ったとき)")
    if m < 12:
        raise SystemExit("12 pt 未満の文字があります。文字を大きくするか、貼り付け幅を広げてください")
PY
echo "書き出し完了: ${svg%.svg}.pdf / ${svg%.svg}.png — PNG を開いて重なり・はみ出し・切れた文字を目視してください"
