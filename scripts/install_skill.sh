#!/bin/zsh
# スキル research-slide-design を ~/.claude/skills と ~/.codex/skills にシンボリックリンクする。
# 同名のフォルダが既にあれば上書きせずに止まる。
set -eu
SRC=${0:A:h:h}/skills/research-slide-design
for dir in ~/.claude/skills ~/.codex/skills; do
  mkdir -p "$dir"
  if [[ -e "$dir/research-slide-design" && ! -L "$dir/research-slide-design" ]]; then
    echo "既にあります(上書きしません): $dir/research-slide-design"; continue
  fi
  ln -sfn "$SRC" "$dir/research-slide-design"
  echo "linked: $dir/research-slide-design -> $SRC"
done
