#!/bin/bash
# Setup script for the Claude Code cloud environment (paste into the environment's
# "Setup script" field). Runs as root on Ubuntu 24.04 before the session starts.
#
# Both eval arms get the same drawing toolbox, so the no-skill arm can pick its own
# route: Graphviz, Mermaid, matplotlib/Pillow, LaTeX/TikZ, ImageMagick. Image
# models are deliberately not provided (the Bash sandbox has no network); a run
# that tries one is recorded by scripts/collect.py.
set -euo pipefail

apt-get update
apt-get install -y --no-install-recommends \
  graphviz fonts-dejavu-core imagemagick \
  bubblewrap socat \
  latexmk texlive-latex-base texlive-latex-extra texlive-pictures texlive-xetex \
  poppler-utils

# Use the same interpreter that `python3` resolves to on PATH.
python3 -m pip install --quiet matplotlib pillow

# Mermaid CLI, driven by the preinstalled Playwright Chromium instead of a
# puppeteer download. The eval child gets only an allowlisted environment, so the
# browser path is baked into a wrapper rather than passed as an env var.
export PATH="/opt/node22/bin:$PATH"
PUPPETEER_SKIP_DOWNLOAD=1 npm install -g --silent @mermaid-js/mermaid-cli
cat > /etc/mermaid-puppeteer.json <<'EOF'
{ "executablePath": "/opt/pw-browsers/chromium", "args": ["--no-sandbox", "--disable-gpu"] }
EOF
MMDC_REAL="$(npm root -g)/@mermaid-js/mermaid-cli/src/cli.js"
cat > /usr/local/bin/mmdc <<EOF
#!/bin/sh
exec /opt/node22/bin/node "$MMDC_REAL" -p /etc/mermaid-puppeteer.json "\$@"
EOF
chmod +x /usr/local/bin/mmdc
# npm's own mmdc link sits earlier on PATH and would bypass the wrapper.
rm -f /opt/node22/bin/mmdc
