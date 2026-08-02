# Getting Started

One-time setup for a fresh machine.

## 1. Prerequisites

Make sure you have:

| Tool | Version | Check | Install if missing |
|---|---|---|---|
| Python | 3.11 or newer | `python3 --version` | `brew install python@3.13` (macOS) |
| Homebrew | latest | `brew --version` | https://brew.sh |
| Google Chrome | latest stable | open Chrome | https://chrome.google.com |

## 2. Run the setup script

```bash
cd /Users/gowri/spaceclub/e-magazine/magazine-toolkit
./setup.sh
```

This will:
1. Create a Python virtual environment in `.venv/`
2. Install required Python packages (Playwright, lxml, img2pdf, Pillow, python-docx)
3. Install Playwright's bundled Chromium browser

If `./setup.sh` doesn't run, do it manually:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

## 3. Smoke test — build the sample issue

```bash
source .venv/bin/activate
python make_magazine.py \
    --from-issue issues/_starter-template \
    output/test.pdf
```

Expected output:

```
================================================================
  வான் வளரொளி இதழ் — Magazine Production Pipeline
================================================================
...
✓ Step 0/4  build_issue_html.py  (0.0s)
✓ Step 1/4  fix_html.py  (0.1s)
✓ Step 2/4  rebalance_sections.py  (~6s)
✓ Step 3/4  compare_html.py  (0.0s)
✓ Step 4/4  build_text_pdf.py  (~3s)
================================================================
  ✓ Done in ~9s
  ✓ Output: output/test.pdf
  ✓ Size:   ~2.2 MB
================================================================
```

Open `output/test.pdf` — you should see a small 3-article sample magazine
(தலையங்கம், திருக்குறள் ஆய்வு், சங்க இலக்கியம்).

If you see that, setup is complete. To see a full-size issue instead, build
from a real one once it exists, e.g. `--from-issue issues/released/Issue-02` (~15-20s,
~7 MB for an 11-article issue).

## 4. Try a different theme

```bash
python make_magazine.py \
    --from-issue issues/_starter-template \
    output/test_peacock.pdf \
    --theme peacock
```

Available themes: `default` (green), `peacock` (teal), `blue`, `terracotta`, `saffron`.

## 5. Verify your PDF is searchable

Open `output/test.pdf` in Preview or any PDF reader. Try:

1. **Search**: Cmd+F and type a Tamil word from the magazine — should highlight.
2. **Select**: drag-select any text — should highlight as text, not as an image.
3. **Copy**: copy the selection, paste somewhere — should paste as text.

If all three work, the text-PDF pipeline is correct.

## 6. Daily use

Once setup is done, every future session just needs:

```bash
cd /Users/gowri/spaceclub/e-magazine/magazine-toolkit
source .venv/bin/activate
python make_magazine.py --from-issue issues/Issue-NN output/file.pdf
```

## Troubleshooting

### `playwright: command not found`
You're not in the venv. Run `source .venv/bin/activate` first.

### `cannot load library 'libgobject-2.0-0'`
This affects only the older WeasyPrint route. The default pipeline uses
Chrome via Playwright, which doesn't need GLib. If you really need
WeasyPrint, install: `brew install pango glib`

### `Tamil text shows as boxes/blocks in PDF`
Playwright's bundled Chromium ships with default fonts including
Noto Sans Tamil. If you see this, run `playwright install chromium`
again to refresh the browser bundle.

### PDF generation hangs
Most likely a font network fetch is stalling. Try once more — the second
run uses cached resources. If still hanging, check `--skip-audit` to see
whether it's the build step or audit step.

### Output PDF is much bigger than 18 MB
You're probably using `--format image`. Drop that flag for text-PDF.

## What next

Once setup is verified:
- Read `PRODUCTION_WORKFLOW.md` to learn the issue-by-issue process
- Read `docs/Editor_Guide.docx` for the editor's reference
- Pass `docs/Author_Guide.docx` to article contributors
