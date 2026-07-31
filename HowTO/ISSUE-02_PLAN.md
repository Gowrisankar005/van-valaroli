# Issue 02 Production Plan — ஆடி 2026 (August 2026 release)

The step-by-step guide for producing Issue 02 using the HowTO toolkit.
Issue 01 (வைகாசி 2026) shipped June 1, 2026. The magazine is now
**bi-monthly**, so Issue 02 is **ஆடி 2026, releasing August 1, 2026**.

> General reference: `PRODUCTION_WORKFLOW.md` (any issue).
> This file is the concrete plan for Issue 02 specifically.

---

## 1. Issue identity

| Field | Value |
|---|---|
| Issue number | 2 |
| Tamil month | ஆடி 2026 |
| English dates | சூலை — ஆகத்து 2026 (Jul–Aug) |
| Release date | August 1, 2026 |
| Next issue (for teaser page) | புரட்டாசி 2026 — Oct 2026 |
| Theme color | default (green) — change with `--theme` if desired |

---

## 2. Section plan & topic assignments

Fill in the author column, confirm topics, then send briefs.
Suggested topics come from the Issue-rotation table (Editor_Guide.docx)
and the "அடுத்த இதழில்" teaser we printed in Issue 01.

| # | Section | File name | Topic for ஆடி 2026 | Author | Target pages |
|---|---|---|---|---|---|
| 1 | தலையங்கம் | `01-thalayangam.md` | *(editor's theme)* | மு. முத்துஜோதி | 2 |
| 2 | திருக்குறள் ஆய்வு | `02-thirukkural.md` | ஆறுவது சினம் — ஔவையார் ஆத்திசூடி vs. வள்ளுவர் வெகுளாமை அதிகாரம் | | 4–5 |
| 3 | சிறுகதை | `03-sirukathai.md` | "திறந்த ஜன்னல்" — புதுமைப்பித்தன் (மணிக்கொடி, 1934) — classic reprint, not a new story | | 3–4 |
| 4 | சங்க இலக்கியம் | `04-sangam.md` | பறவைகள் (birds) | | 5–6 |
| 5 | தமிழகக் கலைகள் | `05-kalai.md` | தமிழர் சிற்பக்கலையின் தொன்மை — கீழடி, ஆதிச்சநல்லூர், நடுகற்கள் (not மதுரை மீனாட்சி as originally planned) | | 5–7 |
| 6 | நூல் மதிப்புரை | `06-nuul.md` | *(book TBD)* | | 2–3 |
| 7 | ஓர் ஒழுக்கம் | `07-ozhukkam.md` | மல சலம் கழித்தல் — எருவாய்க்கான ஒழுக்கம் | | 3–4 |
| 8 | மனம் தொடர் (NEW series) | `08-manam.md` | மனதின் இயல்பு — பகுதி 1 | | 2 |
| 9 | அறநிலையச் செய்திகள் | `09-activities.md` | மே–ஜூன் 2026 VAN நிகழ்வுகள் + photos | குமாரவேல் | 2–3 |
| 10 | அடுத்த இதழில் | `10-closing.md` | புரட்டாசி 2026 teaser + வாசகர் குரல் | (editor) | 1 |

Optional swap-ins if an author drops out: இயற்கை தரும் இன்பம் (1 page photo
essay), கவிதைகள், நற்றமிழ் சொற்கள்.

**வாசகர் குரல்:** Issue 01's closing page promised reader letters — collect
any feedback received since June 1 and include the best in section 10.

---

## 3. Timeline (8-week bi-monthly cycle)

| Week | Dates | Milestone |
|---|---|---|
| 1 | Jun 1–7 | Confirm authors + topics; send briefs (Author_Guide.docx + MMD_Specification.md) |
| 2–4 | Jun 8–28 | Authors draft articles |
| 5 | Jun 29–Jul 5 | Editor first review; request revisions |
| 6 | Jul 6–12 | Authors finalize; submit images |
| 7 | Jul 13–19 | Run `validate_mmd.py` on everything; chase failures |
| 8 | Jul 20–26 | Build PDF, review, iterate |
| — | Jul 27–31 | Buffer + distribution prep |
| — | **Aug 1** | **Release** |

---

## 4. Mechanical steps (editor)

### 4.1 One-time issue setup

```bash
cd /Users/gowri/spaceclub/e-magazine/HowTO

# Create the issue folder from the sample
cp -r issues/Issue-02-sample issues/Issue-02
rm issues/Issue-02/articles/*.md          # sample articles out
```

Edit `issues/Issue-02/issue_meta.json`:

```json
{
  "issue_number": 2,
  "tamil_month": "ஆடி",
  "year": 2026,
  "year_tamil": "௨௦௨௬",
  "english_dates": "சூலை — ஆகத்து 2026",
  "special_label": "",
  "next_issue": { "tamil_month": "புரட்டாசி", "year": 2026 },
  "sections": [ ...the 10 rows from section 2 above... ]
}
```

Cover image: place as `issues/Issue-02/images/cover-image.jpeg`
(portrait, min ~1600×2200 px). **Longest lead-time item — commission early.**

### 4.2 As each article arrives

```bash
# 1. Save it
cp ~/Downloads/thirukkural-aaruvathu-sinam.md issues/Issue-02/articles/02-thirukkural.md

# 2. Save its images
cp ~/Downloads/*.jpg issues/Issue-02/images/

# 3. Lint immediately — catch problems while the author is still responsive
source .venv/bin/activate
python validate_mmd.py issues/Issue-02/articles/02-thirukkural.md --issue issues/Issue-02
```

The linter checks frontmatter, unclosed `:::` directives, missing image
files, English loan words, em-dash typos, and estimates page count.

### 4.3 Build

```bash
python validate_mmd.py issues/Issue-02/articles/*.md --issue issues/Issue-02   # all clean?
python make_magazine.py --from-issue issues/Issue-02 output/VAN_Vallaroli_Aadi2026.pdf
```

~15–20 seconds for a full 10-article issue. Add `--theme peacock` etc. to
try color variants; `--keep-intermediates` to debug layout.

### 4.4 Review checklist

- [ ] Cover: image, "இதழ் 2 · ஆடி 2026" pill, teaser list
- [ ] Page 2 imprint: `[ ஆகத்து — 2026 ]`, issue number 2
- [ ] Page 4 TOC: all 10 sections, sane page numbers
- [ ] Every footer: `இதழ் எண்: 2 | ஆடி 2026`, page number centered, footer pinned to bottom
- [ ] Spot-check 3 articles: byline visible, quotes green-barred, images 60×45mm with centered captions
- [ ] Last page: புரட்டாசி 2026 teaser + contact block
- [ ] Cmd+F search works; text selects as text
- [ ] No page with a large empty bottom (if found: that section's content is short — ask author to expand)

### 4.5 Iterate & ship

Edit markdown → re-run the same build command (idempotent). Then distribute:
email subscribers, upload to vallalar.org, print at original size (A4,
90 GSM, color, saddle-stitch).

### 4.6 Archive

```bash
mkdir -p archive/Aadi2026
cp -r issues/Issue-02 archive/Aadi2026/
cp output/VAN_Vallaroli_Aadi2026.pdf archive/Aadi2026/
```

---

## 5. What authors receive (the brief)

Send each author:

1. `docs/Author_Guide.docx` — writing contract (page budgets, image specs, செந்தமிழ் rules)
2. `docs/MMD_Specification.md` — the exact markdown format
3. Their row from the section-plan table (topic + target pages)
4. Deadline: **June 28, 2026** for first drafts

Submission format: one `.md` file per article + separate image files,
emailed to `vallalararanilayampdm@gmail.com` with subject
`[இதழ் 2] [section] — [author name]`.

---

## 6. Known watch-outs (lessons from Issue 01)

| Risk | Mitigation |
|---|---|
| Overfull pages silently clipping | Fixed in `build_text_pdf.py` (per-page zoom); verify "Zoomed N pages" appears in build log |
| Footer drifting up on short pages | Fixed (flex layout preserved in print CSS) — spot-check anyway |
| Portrait photos crop oddly at 60×45mm | Ask authors for subject-centered photos; swap image if crop loses the subject |
| Tamil typos (missing case suffixes, double letters) | Run the lint + a human proof-read pass before final build |
| Section too short → empty page bottom | Compare linter's ~pages estimate against the target BEFORE week 7 |
| Cover image late | Commission in week 1; it blocks nothing until build but always slips |
