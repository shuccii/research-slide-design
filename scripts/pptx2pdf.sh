#!/bin/zsh
# PowerPoint で .pptx を PDF に書き出す(目視検証用)。 usage: pptx2pdf.sh in.pptx out.pdf
IN=${1:A}; OUT=${2:A}
osascript <<OSA
tell application "Microsoft PowerPoint"
  open POSIX file "$IN"
  delay 3
  save active presentation in (POSIX file "$OUT") as save as PDF
  close active presentation saving no
end tell
OSA
