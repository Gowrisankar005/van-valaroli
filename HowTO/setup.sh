#!/usr/bin/env bash
# setup.sh — one-time install for the magazine production toolkit.
# Run from this directory: ./setup.sh

set -e

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$HERE"

echo "━━━ வான் வளரொளி இதழ் — Toolkit Setup ━━━"
echo "  Location: $HERE"
echo

# 1. Python check
if ! command -v python3 >/dev/null 2>&1; then
    echo "✗ python3 not found. Install Python 3.11+ first:"
    echo "    brew install python@3.13"
    exit 1
fi

PY_VER=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "  ✓ Python $PY_VER detected"

# 2. Create virtual environment
if [ -d ".venv" ]; then
    echo "  ✓ Virtual env already exists at .venv/"
else
    echo "  · Creating virtual env at .venv/ …"
    python3 -m venv .venv
    echo "  ✓ Virtual env created"
fi

# 3. Activate and install
echo
echo "  · Installing Python packages …"
source .venv/bin/activate
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt
echo "  ✓ Packages installed"

# 4. Playwright Chromium browser
echo
echo "  · Installing Playwright Chromium (downloads ~120 MB once) …"
playwright install chromium 2>&1 | tail -3
echo "  ✓ Chromium ready"

# 5. Smoke test
echo
echo "  · Running smoke test (builds the sample 3-article issue) …"
mkdir -p output
if python make_magazine.py \
    --from-issue issues/Issue-02-sample \
    output/_setup_test.pdf \
    --skip-audit >/dev/null 2>&1; then
    SIZE=$(du -h output/_setup_test.pdf | cut -f1)
    echo "  ✓ Smoke test passed — built output/_setup_test.pdf ($SIZE)"
else
    echo "  ✗ Smoke test failed — try running manually to see the error:"
    echo "      source .venv/bin/activate"
    echo "      python make_magazine.py --from-issue issues/Issue-02-sample output/test.pdf"
    exit 1
fi

echo
echo "━━━ Setup complete ━━━"
echo
echo "  Next steps:"
echo "    1. Activate the env in each new shell session:"
echo "         source .venv/bin/activate"
echo "    2. Build a magazine:"
echo "         python make_magazine.py --from-issue issues/Issue-NN output/file.pdf"
echo "    3. Read GETTING_STARTED.md and PRODUCTION_WORKFLOW.md"
echo
