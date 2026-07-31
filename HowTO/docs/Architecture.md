# Architecture — How the toolkit works

Technical overview for developers maintaining or extending the system.

## End-to-end flow

```
SOURCE (author MMD or hand-built HTML)
      │
      ▼
┌──────────────────────────────────────────────────────────────────┐
│  Step 0 — build_issue_html.py (MMD mode only)                     │
│  • Parses issue_meta.json + articles/*.md via mmd_parser.py       │
│  • Renders page fragments (templates/*.html) through an in-house  │
│        template engine — {{ var }}, {% for %} (balanced nested-   │
│        block matching), {% if %} (supports literal % in condition │
│        expressions, e.g. loop.index0 % 2)                         │
│  • Computes derived fields: tiruvalluvar_year, release_month       │
│  • Merges magazine_defaults.json masthead roles                   │
│  • Assembles cover/imprint/masthead/TOC/article pages → base HTML │
└──────────────────────────────────────────────────────────────────┘
      │
      ▼
┌──────────────────────────────────────────────────────────────────┐
│  Step 1 — fix_html.py                                             │
│  • Image path rewrite (Issue-NN/ → Images/)                       │
│  • Hanging-subhead detection + move-to-next-page                  │
│  • '----' caption normalization → .subhead-caption                │
│  • Activities-page image grid creation (2-col) — only groups      │
│        immediately-consecutive same-direction floats, not every   │
│        image on the page (see Architecture note below)            │
│  • Adjacent .img-half pairing into .image-pair-row (side-by-side, │
│        height-capped, object-fit:contain — never crops)           │
│  • Sangam section tagging (alternating image floats)               │
│  • Top-right + bottom-left corner motifs (full set of 4)          │
│  • CSS injection: 11pt body, slim-quote redesign, image sizing    │
│  • Stray trailing character cleanup                               │
└──────────────────────────────────────────────────────────────────┘
      │
      ▼
┌──────────────────────────────────────────────────────────────────┐
│  Step 2 — rebalance_sections.py (uses Playwright for measurement)│
│  • Measure each element's rendered height in real browser —       │
│        temp measurement file is written NEXT TO the source HTML   │
│        (never to /tmp), so relative Images/ paths still resolve   │
│  • Per-section page count adjustment using capacity model:         │
│        section_start_capacity = 850px, continuation = 990px;      │
│        3% overfill tolerance before adding a page (not 20% —      │
│        no longer relies on visual zoom-shrink to hide overflow)   │
│  • Content redistribution (greedy with overshoot/underfill        │
│        heuristic, respecting logical units)                       │
│  • Logical-closure rules: never split a quote/highlights-box;     │
│        keep subheads with their following content — including a  │
│        second pass that merges any subhead-only unit (no real     │
│        content, e.g. a nested ## immediately before a ###) into   │
│        the next unit, so a heading can never end up stranded      │
│        alone at a page bottom; prefer breaks after section-divider │
│  • Backfill pass: after redistribution, re-measure REAL rendered  │
│        gaps in the browser and greedily pull the next page's      │
│        first block forward into any page with real slack — only   │
│        when it's a genuine net improvement (never just relocating │
│        the same deficit to the following page)                    │
│  • Page renumbering across whole document                         │
│  • TOC auto-update from new section start positions               │
└──────────────────────────────────────────────────────────────────┘
      │
      ▼
┌──────────────────────────────────────────────────────────────────┐
│  Step 3 — compare_html.py (integrity audit)                       │
│  • Page count delta (informational — expected for adjustments)    │
│  • Section order preserved (✓ required)                           │
│  • Section content (all paragraphs preserved per section, ✓ req)  │
│  • Bylines on each section's first page (✓ required)              │
│  • Image count consistent with page delta (✓ required)            │
└──────────────────────────────────────────────────────────────────┘
      │
      ▼
┌──────────────────────────────────────────────────────────────────┐
│  Step 4 — build_text_pdf.py (DEFAULT) or build_screenshot_pdf.py │
│                                                                   │
│  TEXT-PDF (default):                                              │
│  • Playwright opens HTML in headless Chromium                     │
│  • page.emulate_media('print') set immediately, BEFORE any        │
│        measurement — so measured heights match what page.pdf()    │
│        actually renders under @media print rules                  │
│  • Inject @page A4 + page-break CSS (flex column layout, not      │
│        block — block silently breaks footer-pinned-to-bottom)     │
│  • Per-page zoom for residual overfill (measures total page H,    │
│        shrinks body-text by exact overshoot amount) — applied via │
│        element.style.setProperty(prop, val, 'important'), since   │
│        magazine.css sets these same properties with !important    │
│        and a bare inline-style assignment is silently ignored     │
│  • page.pdf() → Chrome print engine → searchable text-PDF         │
│                                                                   │
│  IMAGE-PDF (--format image):                                      │
│  • Same browser setup + zoom logic                                │
│  • Per-element screenshot to PNG (1588×2246 at 2× device scale)   │
│  • PIL normalises all PNGs to exact A4 dimensions                 │
│  • img2pdf assembles with forced A4 page size (no margins)        │
└──────────────────────────────────────────────────────────────────┘
      │
      ▼
   OUTPUT.pdf
```

For the concrete bugs each of these fixes traces back to, see CLAUDE.md
PART 9 "System B (HowTO pipeline) — Lessons Learned".

## Why the pipeline is split this way

- **Step 1 (fix)** is HTML-structural. Pure DOM manipulation. Fast.
- **Step 2 (rebalance)** needs RENDERED measurements — requires headless browser. Slow (4s) because Playwright spin-up.
- **Step 3 (audit)** is read-only verification. Fast.
- **Step 4 (PDF)** also needs browser. Slow (6s).

Splitting them lets you:
- Debug each stage independently by inspecting `step1.html` and `step2.html` (use `--keep-intermediates`)
- Re-run only the cheap stages when tweaking content
- Replace any single stage without affecting others

## Key data structures

### .page div (the magazine page)

```html
<div class="page sangam-section">   <!-- optional: section-specific tag -->
    <div class="glossy"></div>      <!-- hidden in print -->
    <span class="corner-tl">❈</span>
    <span class="corner-tr">❈</span>
    <span class="corner-bl">❈</span>
    <span class="corner-br">❈</span>
    <div class="page-header">       <!-- section name + magazine name -->
        <span class="section-name">…</span>
        <span class="mag-name">வான் வளரொளி இதழ்</span>
    </div>
    <div class="content-area">
        <div class="section-header"> <!-- ON FIRST PAGE OF SECTION -->
            ...big title block...
        </div>
        <!-- OR -->
        <div class="continuation-banner">  <!-- ON SUBSEQUENT PAGES -->
            <span class="cont-section-name">…</span>
            <span class="cont-page-info">தொடர்ச்சி</span>
        </div>
        <div class="section-divider">• • •</div>
        <div class="body-text">     <!-- the actual content -->
            <div class="author-byline">…</div>   <!-- page 1 only -->
            <p class="lead-para">…</p>
            <p>…</p>
            <div class="subhead">…</div>
            <p>…</p>
            <div class="slim-quote">
                <div class="quote-text">…</div>
                <div class="quote-source">…</div>
            </div>
            <figure class="article-figure img-right">
                <img src="Images/..." alt="…">
                <figcaption class="img-caption">…</figcaption>
            </figure>
        </div>
    </div>
    <div class="page-footer">
        <span class="issue-info">இதழ் எண்: N | Month Year</span>
        <span class="page-number">N</span>
        <img class="van-logo-footer" src="Images/van-logo.jpg" alt="VAN">
    </div>
</div>
```

### page-capacity model (used by rebalance)

- A4 in CSS: 794 × 1123 px @ 96 DPI
- Section-start body-text budget: ~850 px (after section-header)
- Continuation body-text budget: ~990 px (after small banner)
- Total page height target: 1115 px (1% under 1123 for safety)

When content exceeds capacity, `build_text_pdf.py` applies a per-page `zoom`
on the `.body-text` element by exactly the overshoot amount.

## Adding a new feature

### To add a new section type

1. Pick a unique CSS class for the section tag (e.g. `kavithai-section`)
2. Add tagging logic in `fix_html.py` → `tag_*_section()` function pattern
3. Add any section-specific CSS in the `CSS_INJECTION` constant
4. No other changes — `rebalance_sections.py` is section-agnostic

### To change body text styling

Edit `CSS_INJECTION` in `fix_html.py`. The `.body-text { font-size: 11pt }`
declaration is the magic. Changing this affects everything downstream
because `rebalance_sections.py` measures real rendered heights.

### To support a new image layout

1. Define class (e.g. `.img-quartet` for 4-image grid)
2. Add CSS in `fix_html.py` `CSS_INJECTION`
3. Add detection + DOM-restructure function in `fix_html.py`
4. Wire into `main()` as a new step

### To add a new color theme

1. Add `[data-theme="newname"]` CSS variable block to source HTML
   (or via `fix_html.py` CSS_INJECTION if non-issue-specific)
2. Add `'newname'` to the `--theme` choices in `build_text_pdf.py`,
   `build_screenshot_pdf.py`, and `make_magazine.py`

## Why text-PDF is the default

| Property | Image-PDF | Text-PDF |
|---|---|---|
| File size | 34 MB | **18 MB** |
| Build time | 20 s | **6 s** |
| Searchable | ❌ | ✅ |
| Selectable | ❌ | ✅ |
| Vector rendering | ❌ | ✅ |
| Accessible | ❌ | ✅ |
| Pixel fidelity | 100% | 98% |

The 2% pixel-fidelity difference is invisible at print resolution.
Text-PDF wins on all other measures.

## What's intentionally NOT in the toolkit

- **No author-facing web preview server** — authors/editors open the built
  HTML or PDF directly to review. `validate_mmd.py` catches format errors
  pre-flight but there's no live-preview-while-typing tool.
- **No automated upload/email** — distribution (Phase 8 of
  `PRODUCTION_WORKFLOW.md`) is a manual step.

## Future roadmap (suggested)

`build_issue_html.py` + MMD spec/templates + `validate_mmd.py`, wired into
`make_magazine.py` as Step 0, are all built and in active use since Issue 02
— that closes what used to be Phases 1-3 here. Remaining optional ideas:

| Idea | Effort |
|---|---|
| `preview_article.py` — live-render a single article's HTML for an author without running the full pipeline | ~2 hours |
| Web-based preview server | ~4 hours |
| Auto-distribution scripts (email/upload) | ~2 hours |

See `README.md` for the high-level architecture diagram.
