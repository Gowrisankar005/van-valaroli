# வான் வளரொளி இதழ் — Production Workflow
**E-Magazine Creation Workflow for Consistency, Design Integrity & Quality**
*பெண்ணாடம் வள்ளலார் அறநிலையம் (VAN)*

---

## Overview

This document defines the end-to-end production pipeline for each monthly issue of **வான் வளரொளி இதழ்**. It is a living document — update it as the pipeline matures.

```
PHASE 1: Planning → PHASE 2: Content → PHASE 3: Assembly → PHASE 4: QA → PHASE 5: Publication
    ↓ Gate 1             ↓ Gate 2           ↓ Gate 3            ↓ Gate 4
 Issue brief         Content freeze      HTML complete       Final approval
```

**Key roles:**
- **Gowri** — Editorial lead. Approves everything. Provides content, enforces செந்தமிழ் standards.
- **Claude Code** — Technical production partner. Converts content to HTML, validates, maintains design system.

---

## PHASE 1 — Planning (Week 1)

### 1.1 Define the Issue

Open `Reference_docs/content_tracker.md` and fill in the issue metadata:

| Field | Source | Example |
|-------|--------|---------|
| Issue number | Sequential | `இதழ் எண்: 2` |
| Tamil month | Calendar | `வைகாசி 2026` |
| Special theme label | Gowri decides | `நட்பு சிறப்பிதழ்` (or none) |
| Target page count | 15–25 pages | `18 பக்கங்கள்` |
| Publication target date | Tamil month start ±1 week | `2026 மே 15` |

### 1.2 Select Sections

Review the Section Registry in `CLAUDE.md Part 5` and select 15–20 sections for the issue. Use `Reference_docs/content_tracker.md` to log the selection.

**Rules:**
- Sections 1 (தலையங்கம்) and 5 (closing page) are **always included** — mandatory
- Cross-check `CLAUDE.md Part 14` (topic rotation) to avoid repeating same themes
- Balance long sections (2–4pp) with short sections (0.5–1pp) to hit page target
- If a new series starts (e.g., மனம் தொடர்), note the part number in tracker

### 1.3 Assign Contributors

For each section, log in `content_tracker.md`:
- Author name (Tamil)
- Draft deadline
- Review deadline
- Any special instructions (word count, verse citations needed, etc.)

### ✅ Gate 1 — Planning Complete
- [ ] `content_tracker.md` filled: issue metadata + section list + contributors
- [ ] Section rotation cross-checked (no theme repeated from previous issue)
- [ ] Page count estimate is within 15–25 pages
- [ ] Gowri has approved the section plan

---

## PHASE 2 — Content Creation (Weeks 1–3)

### 2.1 Draft Format

Contributors submit content in one of these formats:
- **Preferred:** Markdown (`.md`) — easiest for Claude Code to convert
- **Acceptable:** Plain text / Word document
- **Not accepted:** PDF (requires manual extraction)

### 2.2 செந்தமிழ் Review (Mandatory)

Before passing content to Claude Code, Gowri reviews each article for pure Tamil vocabulary. Reference: `Reference_docs/senthamizh_guide.md`

**Common substitutions to enforce (CLAUDE.md Part 9):**
- கம்ப்யூட்டர் → கணினி | லேப்டாப் → மடிக்கணினி | இன்டர்நெட் → இணையம்
- ஹாஸ்பிடல் → மருத்துவமனை | டாக்டர் → மருத்துவர்
- தர்மம் → அறம் | ஆரோக்கியம் → நலம் | சுத்தம் → தூய்மை
- பஸ் → பேருந்து | ரோடு → சாலை

### 2.3 Classical Source Verification

For any Thirukkural or Sangam verse citations:
- Verify kural number and exact text against canonical sources
- Never paraphrase the verse itself (commentary is OK)
- Use exact citation format from `CLAUDE.md Part 8`

### 2.4 Content Handoff to Claude Code

Gowri provides Claude Code with:
1. The approved markdown/text for each section
2. The section order for this issue
3. Any special instructions (images, callout boxes, etc.)
4. New cover image filename if changed

### ✅ Gate 2 — Content Freeze
- [ ] All article drafts received and approved by Gowri
- [ ] செந்தமிழ் vocabulary reviewed — no loan words
- [ ] Thirukkural/Sangam citations verified against canonical sources
- [ ] Section order confirmed and logged in `content_tracker.md`
- [ ] Estimated page count still within 15–25 pages
- [ ] All contributor credits (bylines) confirmed

---

## PHASE 3 — HTML Assembly (Week 3–4)

### 3.1 Create the New Issue File

```bash
# Copy the production template (NOT the previous issue file)
cp VAN_Vallaroli_TEMPLATE_v1.html VAN_Vallaroli_[TamilMonth][Year]_v1_0_[YYYYMMDD].html

# Example:
cp VAN_Vallaroli_TEMPLATE_v1.html VAN_Vallaroli_Vaigasi2026_v1_0_20260501.html
```

> **Why template, not previous issue?**
> The template has zero content clutter, clean placeholder markers, and no leftover previous-issue data to accidentally leave in.

### 3.2 Update Global Metadata (Find-Replace in Order)

Open the new file and perform these replacements throughout the entire document:

| Find (placeholder) | Replace with | Where it appears |
|---------------------|--------------|-----------------|
| `[ISSUE NUMBER]` | `இதழ் எண்: 2` | Every page footer |
| `[TAMIL MONTH YEAR]` | `வைகாசி 2026` | Footer, cover, title tag |
| `[SPECIAL LABEL]` | Theme label or remove `.pill-special` | Cover only |
| `[ISSUE PILL]` | `இதழ் 2 &nbsp;·&nbsp; வைகாசி 2026` | Cover `.pill` |
| `[NEXT ISSUE]` | `ஆனி 2026` | Closing page preview |
| `[HTML TITLE]` | `வான் வளரொளி இதழ் — வைகாசி ௨௦௨௬ — முழு இதழ்` | `<title>` tag |

Reference `CLAUDE.md Part 4` for Tamil numeral reference (௧ ௨ ௩...) for years in the title tag.

### 3.3 Build Section Pages

For each section (in editorial order), following `CLAUDE.md Part 2`:

**Step A — Choose the right page template:**
- First page of a section → use `section-header` block
- Continuation page (page 2+) of same section → use `continuation-banner` block
- TOC is a fixed structure — update entries, do not rebuild

**Step B — Convert content to HTML components:**

| Markdown source | HTML component |
|----------------|---------------|
| `## Subheading` | `<div class="subhead">Subheading</div>` |
| Standard paragraph | `<p>text</p>` |
| `> Classical verse` | `<div class="slim-quote">` block |
| `- Bullet list` (grouped key points) | `<div class="highlights-box"><ul>` |
| `1. Numbered steps` | `<ol class="numbered-list">` |
| Author name | `<div class="author-byline">` |
| Data comparison | `<table class="comparison-table">` |

See `CLAUDE.md Part 11` for full conversion rules and `Part 8` for citation formats.

**Step C — Set page header and footer:**
```html
<!-- Page header -->
<span class="section-name">[SECTION NAME IN TAMIL]</span>

<!-- Page footer -->
<span class="issue-info">இதழ் எண்: [N] &nbsp;|&nbsp; [Tamil Month] [Year]</span>
<span class="page-number">[PAGE NUMBER]</span>
```

Use the Section Registry in `CLAUDE.md Part 5` for correct page-header labels.

**Step D — Apply செந்தமிழ் substitutions** (even if Gowri reviewed — validator will catch stragglers)

### 3.4 Build / Update the TOC

After all content pages are placed:
1. Count actual page positions for every section
2. Update each `<div class="toc-row">` with the correct Tamil numeral page number
3. TOC colors rotate: `#8DC63F`, `#6BA82F`, `#D4AF37`, `#2d7a3e`

See `CLAUDE.md Part 6 Task C` for exact TOC row HTML structure.

### 3.5 Build the Closing Page

Last page must include:
- அடுத்த இதழில் (next issue preview) — list 3–5 teasers for the upcoming issue
- VAN contact details (from `CLAUDE.md Part 15`)
- Page footer with correct page number

### 3.6 Image Assets

Verify all three required images exist in `Images/`:
```
Images/VANLogoGold.jpg          ← Required in every page footer
Images/valarolilogogold01.jpg   ← Cover logo
Images/MagazineCoverImage01.jpg ← Cover background (or new image for this issue)
```

If the cover image changes, update `src` in the `.cover` div and update `content_tracker.md`.

> **Do not embed images as base64 in the file body.** Reference them via file path.
> (The validator will flag inline base64 in the body as a failure.)

### ✅ Gate 3 — HTML Assembly Complete
- [ ] File named correctly: `VAN_Vallaroli_[Month][Year]_v1_0_[YYYYMMDD].html`
- [ ] All global metadata updated (no placeholder tokens remain)
- [ ] All sections assembled in editorial order
- [ ] TOC page numbers match actual page positions
- [ ] Every page has: `.glossy`, corner motifs ❈, `.page-header`, `.content-area`, `.page-footer`
- [ ] `VANLogoGold.jpg` in every page footer
- [ ] Closing page has next-issue preview and VAN contact details

---

## PHASE 4 — Quality Assurance (Week 4)

### 4.1 Run the Automated Validator

```bash
cd /Users/gowri/spaceclub/e-magazine
python3 Reference_docs/validate_template.py VAN_Vallaroli_[Month][Year]_v1_0_[YYYYMMDD].html
```

**Expected result: 20/20 PASS (zero failures)**

Interpret results:
| Status | Meaning | Action |
|--------|---------|--------|
| ✅ PASS | Check passed | Nothing required |
| ⚠️ WARN | Minor issue, non-blocking | Review and fix if feasible |
| ❌ FAIL | Must fix before publication | Fix and re-run validator |

Common failure causes and fixes:

| Failure | Fix |
|---------|-----|
| Unfilled placeholder tokens | Search `[SLOT]` — fill or remove all |
| Base64 image in body | Replace with `src="Images/filename.jpg"` |
| Footer logo count mismatch | Check every `.page-footer` has `VANLogoGold.jpg` |
| Banned loan word (செந்தமிழ்) | Find the word, apply substitution from senthamizh_guide.md |
| Missing brand color | Do not alter CSS; if color is missing, check for accidental deletion |
| Missing responsive CSS | Ensure mobile `@media` blocks are in the `<style>` section |

### 4.2 Visual Browser Check

Open the file in Chrome or Firefox (not Safari — print rendering differs):

**Desktop check (1280px+):**
- [ ] Cover page renders as a clean A4 portrait layout
- [ ] All text is readable — no overlap, no clipping
- [ ] Colors match brand palette visually
- [ ] TOC is legible — no garbled Tamil characters (▯ or ? boxes)
- [ ] All body pages flow correctly

**Mobile check (375px — Chrome DevTools or phone):**
- [ ] Cover stacks and scrolls — no horizontal overflow
- [ ] Masthead text does not overflow its container
- [ ] Pills wrap cleanly (no text cut off)
- [ ] Body pages are readable continuous-scroll layout
- [ ] Footer logo visible on each page

**Print preview check (Ctrl+P / Cmd+P):**
- [ ] Pages break cleanly at A4 boundaries
- [ ] No blank pages inserted unexpectedly
- [ ] Headers and footers appear on every page
- [ ] Images print (not showing as broken)

### 4.3 Content Quality Review (Gowri)

Gowri reviews the rendered HTML:

- [ ] All articles present and in correct order
- [ ] No missing paragraphs or truncated content
- [ ] Classical verse citations are exact (compare against source)
- [ ] Author bylines are correct
- [ ] No English words mixed in Tamil text body
- [ ] TOC descriptions match actual article content
- [ ] Next issue preview is accurate

### 4.4 Iteration

If changes needed after review:
1. Make corrections in the HTML file
2. Increment version: `v1_0 → v1_1` (minor fix) or `v2_0` (structural change)
3. Re-run validator to confirm no regressions
4. Repeat visual check for changed pages

### ✅ Gate 4 — Final Approval
- [ ] Validator: 20/20 PASS (zero failures)
- [ ] Desktop visual check: all items cleared
- [ ] Mobile visual check: all items cleared
- [ ] Print preview check: clean page breaks
- [ ] Gowri editorial approval: signed off
- [ ] Version number is correct (v1.1 for first-corrected draft)
- [ ] Filename reflects final version number and date

---

## PHASE 5 — Publication (Publication Week)

### 5.1 Generate the PDF

1. Open the final HTML file in **Google Chrome**
2. Go to **File → Print** (Cmd+P / Ctrl+P)
3. Settings:
   - **Destination:** Save as PDF
   - **Layout:** Portrait
   - **Paper size:** A4
   - **Margins:** None (the HTML file manages its own margins)
   - **Background graphics:** ✅ Enabled (essential for colors and gradients)
4. Save as: `VAN_Vallaroli_[Month][Year]_v[X.X]_[YYYYMMDD].pdf`

> Safari may not render colors correctly. Use Chrome for all PDF exports.

### 5.2 PDF Quality Check

Open the generated PDF:
- [ ] All 34 pages present (or correct count for this issue)
- [ ] Cover image and colors print correctly
- [ ] No text cut off at page edges
- [ ] Page numbers in footers are sequential (3, 4, 5… — Cover and TOC have no numbers)
- [ ] Footer logo (VANLogoGold.jpg) visible on every content page
- [ ] Tamil text is not garbled in the PDF

### 5.3 Archive

```bash
# In the project folder — keep both HTML and PDF for every issue
VAN_Vallaroli_Chittirai2026_v1_1_20260307.html   ← archive (DO NOT EDIT)
VAN_Vallaroli_Chittirai2026_v1_1_20260307.pdf    ← archive PDF
VAN_Vallaroli_Vaigasi2026_v1_1_20260515.html     ← current issue (after QA)
VAN_Vallaroli_Vaigasi2026_v1_1_20260515.pdf      ← current issue PDF
```

### 5.4 Git Commit

```bash
cd /Users/gowri/spaceclub/e-magazine

# Stage the new issue files
git add VAN_Vallaroli_[Month][Year]_v[X.X]_[YYYYMMDD].html
git add Reference_docs/content_tracker.md   # update tracker with final data

# Commit
git commit -m "Issue [N] — [TamilMonth] [Year] final (v[X.X])"

# Push to GitHub
git push origin main
```

### 5.5 Distribution

Gowri handles distribution via:
- மின்னஞ்சல் (email) list — `vallalararanilayampdm@gmail.com`
- WhatsApp groups
- `www.vallalar.org` website (if applicable)

Claude Code does **not** handle distribution — only the HTML/PDF output.

### ✅ Gate 5 — Issue Published
- [ ] PDF generated from Chrome — clean output
- [ ] PDF quality check passed
- [ ] HTML and PDF archived in project folder
- [ ] Git commit made with correct message
- [ ] Pushed to GitHub: `https://github.com/gowrishankar005/van-valaroli.git`
- [ ] `content_tracker.md` updated with final data for this issue
- [ ] Gowri has the PDF for distribution

---

## Tools Reference

| Tool | File | Purpose |
|------|------|---------|
| Production template | `VAN_Vallaroli_TEMPLATE_v1.html` | Starting point for every new issue |
| Design specifications | `Reference_docs/emag-design_specs.md` | CSS values, component library, brand rules |
| Validator script | `Reference_docs/validate_template.py` | Automated QA — run before every release |
| செந்தமிழ் guide | `Reference_docs/senthamizh_guide.md` | Pure Tamil vocabulary reference |
| Content tracker | `Reference_docs/content_tracker.md` | Monthly planning and progress tracking |
| VAN Voice guide | `CLAUDE.md Part 10` | Editorial tone and style standards |
| Section registry | `CLAUDE.md Part 5` | Section names, labels, typical page counts |
| Topic rotation log | `CLAUDE.md Part 14` | Track themes used to avoid repetition |

---

## Version History of This Document

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-03-09 | Initial creation — five-phase pipeline |

---

*இந்த ஆவணம் தொடர்ந்து புதுப்பிக்கப்படும். | This document will be continuously updated.*
*வான் வளரொளி இதழ் — பெண்ணாடம் வள்ளலார் அறநிலையம் 🪷*
