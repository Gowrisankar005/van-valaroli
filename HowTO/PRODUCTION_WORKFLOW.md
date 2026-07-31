# Production Workflow — Per Issue

Step-by-step checklist for producing each magazine issue from scratch.

## Phase 1 — Plan & collect (weeks 1-3)

1. Decide which 10 sections appear in this issue
2. Assign one author per article
3. Send `docs/Author_Guide.docx` + `docs/MMD_Specification.md` to each author
4. Set submission deadline (allow 1 week for revisions)

### Default 10 sections

| # | Section | Typical pages |
|---|---|---|
| 1 | தலையங்கம் (Editorial) | 2 |
| 2 | திருக்குறள் ஆய்வு | 4–5 |
| 3 | சிறுகதை | 3–4 |
| 4 | சங்க இலக்கியம் | 5–6 |
| 5 | தமிழகக் கலைகள் | 5–7 |
| 6 | நூல் மதிப்புரை | 2–3 |
| 7 | ஓர் ஒழுக்கம் | 3–4 |
| 8 | இயற்கை தரும் இன்பம் | 1 |
| 9 | அறநிலையச் செய்திகள் | 2–3 |
| 10 | அடுத்த இதழில் | 1 |

You can change this list per issue — just update `issue_meta.json`.

## Phase 2 — Set up the issue folder

```bash
cd /Users/gowri/spaceclub/e-magazine/HowTO

# Copy the skeleton
cp -r issues/Issue-02-sample issues/Issue-03    # use existing as template
# or
cp -r examples/Issue-NN-skeleton issues/Issue-03
```

Edit `issues/Issue-03/issue_meta.json`:
- Bump `issue_number`
- Set `tamil_month`, `year`, `year_tamil`, `english_dates`
- Update the `sections` list to match this issue's content
  (cover teasers are **auto-built** from each section's `topic_title` —
  no separate teaser list needed; optional `cover_teasers` override in meta)
- Masthead senior roles / publisher can stay as in the previous issue;
  **தொகுப்பாசிரியர்கள்** are shared for every issue via
  `HowTO/magazine_defaults.json` (edit there once, not per issue)

## Phase 3 — Drop in author content

For each section:

1. Save the author's `.md` file as `issues/Issue-03/articles/NN-name.md`
2. Save referenced images into `issues/Issue-03/images/`
3. Ensure the `section` field in each article's frontmatter exactly matches the `section_name` in `issue_meta.json`

### Article folder example

```
issues/Issue-03/
├── issue_meta.json
├── articles/
│   ├── 01-thalayangam.md
│   ├── 02-thirukkural.md
│   ├── 03-sirukathai.md
│   ├── 04-thamarai.md
│   ├── 05-kalai.md
│   ├── 06-nuul.md
│   ├── 07-ozhukkam.md
│   ├── 08-iyarkai.md
│   ├── 09-activities.md
│   └── 10-closing.md
└── images/
    ├── cover-image.jpeg     ← cover background (required)
    ├── lotus-pond-01.jpg
    ├── madurai-pillar.jpg
    └── ... (all images referenced by articles)
```

## Phase 4 — Build the magazine (~15 seconds)

```bash
source .venv/bin/activate

python make_magazine.py \
    --from-issue issues/Issue-03 \
    output/VAN_Vallaroli_Aani2026.pdf
```

This runs all 5 steps automatically:

| Step | What happens | Time |
|---|---|---|
| 0 | `build_issue_html.py` — Magazine Markdown → base HTML | <1 s |
| 1 | `fix_html.py` — image paths, hanging subheads, image grids/pairing, CSS | 0.1 s |
| 2 | `rebalance_sections.py` — per-section page count + content distribution + real-rendered-gap backfill + TOC | 4-6 s |
| 3 | `compare_html.py` — integrity audit | 0.3 s |
| 4 | `build_text_pdf.py` — Playwright → searchable text-PDF | 3-6 s |

If you'd rather run the stages by hand (useful when debugging one stage), the
equivalent manual sequence is:
```bash
python build_issue_html.py issues/Issue-03 source/VAN_Vallaroli_<Month><Year>_base.html
python fix_html.py source/VAN_Vallaroli_<Month><Year>_base.html source/VAN_Vallaroli_<Month><Year>_fixed.html
python rebalance_sections.py source/VAN_Vallaroli_<Month><Year>_fixed.html source/VAN_Vallaroli_<Month><Year>.html
python build_text_pdf.py source/VAN_Vallaroli_<Month><Year>.html output/VAN_Vallaroli_<Month><Year>.pdf
python compare_html.py source/VAN_Vallaroli_<Month><Year>_fixed.html source/VAN_Vallaroli_<Month><Year>.html
```

## Phase 5 — Review PDF

Open `output/VAN_Vallaroli_<Month><Year>.pdf` and verify:

### Cover & front matter
- [ ] Cover image displays correctly
- [ ] Issue number + Tamil month + year on cover pill
- [ ] Teaser list shows up to 6 dynamic lines (`section — topic_title` from this issue)
- [ ] Page 2 (imprint) — issue info correct
- [ ] Page 3 (masthead) — senior roles + **தொகுப்பாசிரியர்கள்** + contact correct
- [ ] Page 4 (TOC) — every section listed with reasonable page number

### Articles (spot-check 3)
- [ ] Section title big and visible on page 1
- [ ] Author byline visible on page 1
- [ ] Body text reads naturally, no orphan subheads
- [ ] Slim quotes: green left bar, italic verse, source citation
- [ ] Images: portraits use `type="portrait"` (45mm, no border) — never `type="half"`, which is for diagrams/artifacts (80mm, no border)
- [ ] No two same-side floats (`float`/`float-left`) stacked back to back — check the alternation held
- [ ] Page footers: number centered, issue info left, logo right
- [ ] No page has a large blank area at the bottom mid-article (the `rebalance_sections.py` backfill pass should have caught this — see below). A blank area right at a section's *last* page, after a natural closing/rating line, is fine.

### PDF integrity
- [ ] Cmd+F search works (try a known Tamil word)
- [ ] Text select-and-copy works
- [ ] File size 5–20 MB (depending on image count)

### Pipeline log sanity check
While the build runs, glance at the `rebalance_sections.py` output:
- `[3/5] Verifying real rendered fill + backfilling underfilled pages…` should print
  `✓ Backfilled N element(s)` lines if any page had genuine slack — 0 is fine too,
  it just means nothing needed moving.
- If a page still looks empty at the bottom *after* this step ran, it's most likely
  the natural end of that section (confirm by checking the last visible line isn't
  cut off), not a bug — but if in doubt, re-run with `--keep-intermediates` and
  inspect `_pipeline_step2.html` for that page directly.

## Phase 6 — Iterate if needed

Make changes to the markdown / images, then re-run:

```bash
python make_magazine.py --from-issue issues/Issue-03 output/VAN_Vallaroli_Aani2026.pdf
```

Common fixes:

| Issue | Fix |
|---|---|
| Empty space at page bottom, mid-section | Should mostly self-correct via the `rebalance_sections.py` backfill pass — re-check the log for `Backfilled N element(s)`. If the gap remains because the next page's first block is one large paragraph (too big to move whole), split that paragraph at a natural sentence break in the source `.md` — the pipeline doesn't split paragraphs automatically, that's an intentional limit on the pagination rule (never split a paragraph mid-sentence programmatically) |
| Empty space at bottom of a section's *last* page | Usually just the natural end of the article — not a bug. Confirm the last visible line ends the piece (closing sign-off, rating, etc.) |
| Section content overflows | Trim text or split into more pages (auto-handled by rebalance) |
| Wrong section page in TOC | Re-run pipeline; TOC is auto-generated |
| Image cropped weirdly | Check `type=` — `half`/`portrait` never crop (contain, no border); `float`/`float-left`/`banner` do object-fit crop, so pick a photo that's already close to the target aspect ratio |
| Two images look squeezed with a narrow ragged text column between them | You have two same-side floats back to back — alternate `float`/`float-left`, or move one to `half`/`portrait` |
| Tiny text on a few pages | Section is over-dense; consider splitting. (Page-count tolerance is 3% over capacity before a new page is added — this should be rare now) |
| Quote/image overlap | Should never happen — file a bug |
| Footer not pinned to page bottom in the PDF | A print-CSS `display` override broke the page's flex layout — see CLAUDE.md PART 9, System B Lesson 7 |

## Phase 7 — Try different themes

```bash
# Generate all 5 theme variants
for theme in default peacock blue terracotta saffron; do
    python make_magazine.py \
        --from-issue issues/Issue-03 \
        output/VAN_Vallaroli_${theme}.pdf \
        --theme $theme
done
```

## Phase 8 — Distribute

| Channel | Action |
|---|---|
| Email | Attach `output/VAN_Vallaroli_<Month><Year>.pdf` to subscriber list |
| Web | Upload PDF + HTML to vallalar.org |
| Print | Send PDF to printer at original size (no scaling) — A4 90 GSM, color, saddle-stitch |

## Phase 9 — Archive

```bash
ISSUE="Aani2026"
mkdir -p archive/$ISSUE
cp -r issues/Issue-03 archive/$ISSUE/
mv output/VAN_Vallaroli_*.pdf archive/$ISSUE/
```

Update the issue rotation table in `docs/Editor_Guide.docx` so future
editors know which topics were covered.

## Issue cadence (monthly)

| Week | Activity |
|---|---|
| 1 | Send call for submissions; assign topics |
| 2 | Authors draft articles |
| 3 | Receive articles + images; first round editing |
| 4 | Run pipeline, review, iterate, distribute by month-end |
