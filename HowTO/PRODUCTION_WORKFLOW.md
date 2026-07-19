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
- Optionally update `masthead.roles` if editorial team changes

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
| 1 | `fix_html.py` — image paths, hanging subheads, image grids, CSS | 0.1 s |
| 2 | `rebalance_sections.py` — per-section page count + content distribution + TOC | 4-6 s |
| 3 | `compare_html.py` — integrity audit | 0.3 s |
| 4 | `build_text_pdf.py` — Playwright → searchable text-PDF | 3-6 s |

## Phase 5 — Review PDF

Open `output/VAN_Vallaroli_<Month><Year>.pdf` and verify:

### Cover & front matter
- [ ] Cover image displays correctly
- [ ] Issue number + Tamil month + year on cover pill
- [ ] Teaser list shows first 6 article titles
- [ ] Page 2 (imprint) — issue info correct
- [ ] Page 3 (masthead) — editor names + contact correct
- [ ] Page 4 (TOC) — every section listed with reasonable page number

### Articles (spot-check 3)
- [ ] Section title big and visible on page 1
- [ ] Author byline visible on page 1
- [ ] Body text reads naturally, no orphan subheads
- [ ] Slim quotes: green left bar, italic verse, source citation
- [ ] Images: uniform 60×45mm with caption centered below
- [ ] Page footers: number centered, issue info left, logo right

### PDF integrity
- [ ] Cmd+F search works (try a known Tamil word)
- [ ] Text select-and-copy works
- [ ] File size 5–20 MB (depending on image count)

## Phase 6 — Iterate if needed

Make changes to the markdown / images, then re-run:

```bash
python make_magazine.py --from-issue issues/Issue-03 output/VAN_Vallaroli_Aani2026.pdf
```

Common fixes:

| Issue | Fix |
|---|---|
| Empty space at page bottom | Ask author to expand that section |
| Section content overflows | Trim text or split into more pages (auto-handled by rebalance) |
| Wrong section page in TOC | Re-run pipeline; TOC is auto-generated |
| Image cropped weirdly | Replace photo with one centered better |
| Tiny text on a few pages | Section is over-dense; consider splitting |
| Quote/image overlap | Should never happen — file a bug |

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
