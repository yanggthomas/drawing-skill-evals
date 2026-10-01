#!/bin/bash
# Setup script for the Claude Code cloud environment (paste into the environment's
# "Setup script" field). Runs as root on Ubuntu 24.04 before the session starts.
# Round 1 (G1) only needs Graphviz. The TikZ toolchain for model-architecture
# cases (M1, M2) is commented out until those cases are promoted.
set -euo pipefail

apt-get update
apt-get install -y --no-install-recommends \
  graphviz fonts-dejavu-core \
  bubblewrap socat    # OS sandbox backend required when plugin eval grants Bash

# M1/M2 (model-architecture) — enable when promoted; check it stays under ~5 min:
# apt-get install -y --no-install-recommends \
#   latexmk texlive-xetex texlive-pictures texlive-latex-extra poppler-utils
