# Production Workflow — Per Issue

Step-by-step checklist for producing each magazine issue from scratch.

## Phase 1 — Plan & collect (weeks 1-3)

1. Decide which sections appear in this issue (check the rotation tracker in
   CLAUDE.md PART 6 first — don't repeat a topic still fresh from last issue,
   and note any series, like மனம் தொடர், that owes a next part)
2. Assign one author per article
3. Send `docs/Author_Guide.docx` + `docs/MMD_Specification.md` to each author
4. Set submission deadline (allow 1 week for revisions)

### Default sections (11, matching Issue 02's actual final shape)

| # | Section | Typical pages |
|---|---|---|
| 1 | தலையங்கம் (Editorial) | 2 |
| 2 | திருக்குறள் ஆய்வு | 4–5 |
| 3 | சிறுகதை | 3–4 |
| 4 | சங்க இலக்கியம் | 5–6 |
| 5 | தமிழகக் கலைகள் | 5–7 |
| 6 | நூல் மதிப்புரை | 2–3 |
| 7 | ஓர் ஒழுக்கம் | 3–4 |
| 8 | மனம் தொடர் | 2 |
| 9 | இயற்கை தரும் இன்பம் | 1 |
| 10 | அறநிலையச் செய்திகள் | 2–3 |
| 11 | அடுத்த இதழில் | 1 |

You can change this list per issue — just update `issue_meta.json`.

## Phase 2 — Set up the issue folder

```bash
cd van-valaroli/magazine-toolkit   # or wherever you cloned the repo

# Copy a template — issues/_starter-template is a minimal 3-article skeleton
# (good for a quick trial run, and has its own README); issues/released/Issue-02
# is the full, validated 11-article issue (better as a real reference for
# issue_meta.json's schema, masthead override shape, and article/image naming
# conventions)
cp -r issues/_starter-template issues/Issue-03
# then delete the sample articles/images you don't need and add your own
```

If you copy from `issues/released/Issue-NN` instead (to reuse its structure as
a closer starting point), **delete its `final/` folder and `ISSUE-NN_PLAN.md`
first** — those are that specific issue's shipped output and production plan,
not part of a fresh issue's starting skeleton.

Edit `issues/Issue-03/issue_meta.json`:
- Bump `issue_number`
- Set `tamil_month`, `year`, `year_tamil`, `english_dates`
- Update the `sections` list to match this issue's content
  (cover teasers are **auto-built** from each section's `topic_title` —
  no separate teaser list needed; optional `cover_teasers` override in meta)
- Masthead senior roles / publisher can stay as in the previous issue;
  **தொகுப்பாசிரியர்கள்** are shared for every issue via
  `magazine-toolkit/magazine_defaults.json` (edit there once, not per issue)

## Phase 3 — Drop in author content

Authors rarely send clean MMD directly — usually a `.docx` or plain text,
sometimes a revised version of something they sent before. Stage and convert
it first, then promote the cleaned result into the real `articles/`.

### 3a. Stage the raw submission

```bash
mkdir -p issues/Issue-03/_drafts/02-thirukkural
cp ~/Downloads/thirukkural-draft.docx issues/Issue-03/_drafts/02-thirukkural/source.docx
```

`_drafts/` is gitignored — it's intake scratch, never a deliverable. **If the
author sends a revised version, overwrite `source.docx` in place** — don't
keep `source-v2.docx`, `source-v3.docx` etc. sitting alongside old ones; a
revision replaces the draft, it doesn't append to it.

### 3b. Convert to a rough MMD draft

```bash
pandoc issues/Issue-03/_drafts/02-thirukkural/source.docx \
    -t markdown \
    --extract-media=issues/Issue-03/_drafts/02-thirukkural/images \
    -o issues/Issue-03/_drafts/02-thirukkural/converted.md
```

This is the same technique used for Issue 02's conversion (see
`Archive/Issue-02-Misc-conversion/docs/CONVERSION_REPORT.md` for a worked
example, including how mismatches between the docx's actual content and the
planned topic were tracked). Re-run this step fresh every time `source.docx`
is replaced — don't hand-edit `converted.md` before checking the new source
in, or your edits get silently lost on the next conversion.

### 3c. Hand-clean into real MMD, then promote

Editor turns `converted.md`'s raw pandoc output into proper MMD syntax
(frontmatter, `##` subheads, `:::quote`/`:::box`/`:::image`/`:::closing`
directives — see `docs/MMD_Specification.md`), then:

1. Save the cleaned result as `issues/Issue-03/articles/NN-name.md`
2. Copy the final images (from `_drafts/.../images/`, cropped/renamed as
   needed) into `issues/Issue-03/images/`
3. Ensure the `section` field in the frontmatter exactly matches the
   `section_name` in `issue_meta.json`

### 3d. Verify integrity post-conversion

```bash
python validate_mmd.py issues/Issue-03/articles/NN-name.md --issue issues/Issue-03
```

Checks frontmatter completeness, section-name match, referenced images
actually exist, செந்தமிழ் loan-word violations, em-dash typos, and unclosed
`:::` directives — run this on every promoted article before it's considered
done, not just at the end of the issue.

### Article folder example

Based on Issue 02's actual (validated, shipped) layout — `issues/released/Issue-02/`
is a working reference if you want to see real examples of each piece below:

```
issues/Issue-03/
├── issue_meta.json
├── articles/
│   ├── 01-thalaiyangam.md
│   ├── 02-thirukkural.md
│   ├── 03-sirukathai.md
│   ├── 04-sangailakkiyam.md
│   ├── 05-kalai.md
│   ├── 06-nool-mathippurai.md
│   ├── 07-ozhukkam.md
│   ├── 08-manam.md
│   ├── 09-activities.md
│   ├── 10-closing.md
│   └── 11-iyarkai.md
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
    output/VAN_Vallaroli_Purattasi2026.pdf
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
python make_magazine.py --from-issue issues/Issue-03 output/VAN_Vallaroli_Purattasi2026.pdf
```

Common fixes:

| Issue | Fix |
|---|---|
| Empty space at page bottom, mid-section | Should mostly self-correct via the `rebalance_sections.py` backfill pass — re-check the log for `Backfilled N element(s)`. If the gap remains because the next page's first block is one large paragraph (too big to move whole), split that paragraph at a natural sentence break in the source `.md` — the pipeline doesn't split paragraphs automatically, that's an intentional limit on the pagination rule (never split a paragraph mid-sentence programmatically) |
| Gap before a photo pair or a list | Those are unbreakable blocks. Move a nearby paragraph above the photos, or use `float` / `float-left` so the photos sit beside text (alternate sides). A line ending in `:` now stays glued to the list/quote after it automatically |
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

## Phase 9 — Promote to released

```bash
git mv issues/Issue-03 issues/released/Issue-03
mkdir -p issues/released/Issue-03/final
mv source/VAN_Vallaroli_Purattasi2026*.html issues/released/Issue-03/final/
cp output/VAN_Vallaroli_Purattasi2026.pdf issues/released/Issue-03/final/
```

See `issues/released/README.md` for the full shape. This is the durable
record of what shipped — `source/` and `output/` are both gitignored build
scratch, regenerated fresh on the next build, so nothing there survives
long-term unless it's copied in here.

Update the issue rotation table in root `CLAUDE.md` PART 6 and
`docs/Editor_Guide.docx` so future editors know which topics were covered.

## Issue cadence (monthly)

| Week | Activity |
|---|---|
| 1 | Send call for submissions; assign topics |
| 2 | Authors draft articles |
| 3 | Receive articles + images; first round editing |
| 4 | Run pipeline, review, iterate, distribute by month-end |
