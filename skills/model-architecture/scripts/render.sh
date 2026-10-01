#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 || $# -gt 2 ]]; then
  echo "usage: render.sh path/to/figure.tex [--svg]" >&2
  exit 2
fi

source_file=$1
svg_mode=${2:-}

if [[ ! -f "$source_file" || "$source_file" != *.tex ]]; then
  echo "render.sh: expected an existing .tex file: $source_file" >&2
  exit 2
fi

if [[ -n "$svg_mode" && "$svg_mode" != "--svg" ]]; then
  echo "render.sh: unknown option: $svg_mode" >&2
  exit 2
fi

source_dir=$(cd "$(dirname "$source_file")" && pwd)
source_name=$(basename "$source_file")
stem=${source_name%.tex}
dpi=${TIKZ_PNG_DPI:-200}

(
  cd "$source_dir"
  latexmk -xelatex -interaction=nonstopmode -halt-on-error "$source_name"
  pdftoppm -png -singlefile -r "$dpi" "$stem.pdf" "$stem"
  if [[ "$svg_mode" == "--svg" ]]; then
    dvisvgm --no-fonts --bbox=papersize "$stem.xdv" -o "$stem.svg"
  fi
)

printf '%s\n' "$source_dir/$stem.tex" "$source_dir/$stem.pdf" "$source_dir/$stem.png"
if [[ "$svg_mode" == "--svg" ]]; then
  printf '%s\n' "$source_dir/$stem.svg"
fi
