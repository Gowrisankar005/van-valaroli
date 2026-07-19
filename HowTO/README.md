# வான் வளரொளி இதழ் — Production Toolkit

A self-contained workspace for producing the magazine PDF from author content.

## In 60 seconds

```bash
# One-time setup
cd /Users/gowri/spaceclub/e-magazine/HowTO
./setup.sh

# Build the magazine from author articles
source .venv/bin/activate
python make_magazine.py --from-issue issues/Issue-02-sample output/magazine.pdf
```

That's it. The pipeline reads markdown articles + images, renders a complete
A4 magazine PDF in ~10 seconds.

## What's here

```
HowTO/
├── README.md                    ← this file
├── GETTING_STARTED.md           ← one-time setup
├── PRODUCTION_WORKFLOW.md       ← per-issue checklist
├── requirements.txt
├── setup.sh                     ← bash installer
│
├── make_magazine.py             ← ONE-COMMAND ENTRY POINT
│
├── build_issue_html.py          ← Step 0 — author markdown → HTML
├── mmd_parser.py                  (used by Step 0)
├── validate_mmd.py              ← Pre-flight: lint author articles
├── fix_html.py                  ← Step 1 — auto-corrections + CSS
├── rebalance_sections.py        ← Step 2 — page count + content balance
├── compare_html.py              ← Step 3 — integrity audit
├── build_text_pdf.py            ← Step 4 — searchable text-PDF
├── build_screenshot_pdf.py        (alternative — image-PDF fallback)
│
├── templates/                   ← MAGAZINE TEMPLATE
│   ├── _base.html               (outer <html><head><body>)
│   ├── cover.html               (cover page)
│   ├── imprint.html             (page 2 — issue info)
│   ├── masthead.html            (page 3 — editor + contact)
│   ├── toc.html                 (page 4 — auto-built)
│   ├── article_page.html        (each article's page template)
│   └── magazine.css             (all styling — 1540 lines)
│
├── docs/
│   ├── Author_Guide.docx        → distribute to article contributors
│   ├── Editor_Guide.docx        → editor's workflow reference
│   ├── MMD_Specification.md     → formal Magazine Markdown spec
│   └── Architecture.md          → technical deep-dive
│
├── issues/                      ← one folder per issue
│   └── Issue-02-sample/
│       ├── issue_meta.json      (issue identity + section list)
│       ├── articles/            (one .md per section)
│       └── images/              (image assets)
│
├── source/                      ← built artifacts go here
│   ├── Issue-02-sample_base.html  (built by Step 0)
│   └── Images/                  (shared image library)
│
└── output/                      ← final PDFs
```

## Two ways to build

### Mode A — From author articles (NEW ISSUES)

```bash
python make_magazine.py --from-issue issues/Issue-02-sample output/Vaigasi2026.pdf
```

Reads your `issues/Issue-XX/` folder, runs all 5 steps (build HTML →
fix → rebalance → audit → PDF).

### Mode B — From existing HTML (REVISIONS, ONE-OFFS)

```bash
python make_magazine.py --from-html source/some_base.html output/file.pdf
```

Skips Step 0 (HTML build), uses your HTML as-is. Useful when iterating
on layout fixes without re-running markdown parsing.

## Where to go next

| If you are | Read |
|---|---|
| Setting up | `GETTING_STARTED.md` |
| Producing a new issue | `PRODUCTION_WORKFLOW.md` |
| Writing an article | `docs/Author_Guide.docx` + `docs/MMD_Specification.md` |
| Editor doing review | `docs/Editor_Guide.docx` |
| Curious about internals | `docs/Architecture.md` |

## Quick reference

| Command | What it does |
|---|---|
| `python make_magazine.py --from-issue ISSUE_DIR OUT.pdf` | Build from markdown (recommended) |
| `python make_magazine.py --from-html FILE.html OUT.pdf` | Build from existing HTML |
| `... --theme peacock` | Use peacock teal theme |
| `... --theme blue/terracotta/saffron` | Other color themes |
| `... --format image` | Pixel-perfect image-PDF (larger, slower) |
| `... --skip-audit` | Skip integrity check |
| `... --keep-intermediates` | Keep step1/step2 HTML for debugging |
| `python build_issue_html.py ISSUE_DIR OUT.html` | Just Step 0 (no PDF) |
| `python mmd_parser.py ARTICLE.md` | Parse one article + print HTML output |
| `python validate_mmd.py ARTICLE.md --issue ISSUE_DIR` | Lint an article (run before submitting) |

## Pipeline timing

```
Step 0  build_issue_html.py    0.0s  — markdown → base HTML
Step 1  fix_html.py            0.1s  — corrections + CSS
Step 2  rebalance_sections.py  5.1s  — page count + content balance + TOC
Step 3  compare_html.py        0.2s  — integrity audit
Step 4  build_text_pdf.py      2.9s  — searchable PDF
                              ─────
                               8.3s total for a small 3-article test
```

A full 10-article issue typically builds in 15-20 seconds.
