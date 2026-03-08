# வான் வளரொளி இதழ் — IMPLEMENTED DESIGN SYSTEM
## Single source of truth for all design decisions
**Version:** 1.2 (சித்திரை 2026)
**Last updated:** 2026-03-09
**Source of truth:** `VAN_Vallaroli_TEMPLATE_v1.html` → `<style>` block

> ⚠️ This document reflects what is **actually implemented** in the codebase.
> Do not change CSS values without updating this document.
> Do not update this document without changing the CSS.

---

## 1. BRAND PALETTE

| Token | Hex | Used For |
|-------|-----|----------|
| `--van-green-bright` | `#8DC63F` | Header rule gradient, bullet dots, box borders |
| `--van-green-dark` | `#6BA82F` | Section header titles, TOC title, table headers |
| `--van-green-deep` | `#2d7a3e` | Page header text, page numbers, subheadings, sign-off |
| `--van-gold` | `#D4AF37` | Decorative rules, quote marks, section labels, accents |
| `--body-text` | `#2B2B2B` | All body paragraphs |
| `--subtle-text` | `#666666` | Sign titles, org names, captions |
| `--page-bg-top` | `#fffef5` | Page background gradient top |
| `--page-bg-bottom` | `#fef9f2` | Page background gradient bottom |
| `--cover-dark` | `rgba(8,38,18,0.97)` | Cover masthead / bottom band overlay |
| `--corner-motif` | `#8b6f47` @ 28% opacity | Decorative ❈ corner ornaments |

---

## 2. TYPOGRAPHY

| Element | Font | Size | Weight | Color |
|---------|------|------|--------|-------|
| Body text | Noto Sans Tamil | 12pt | 400 | `#2B2B2B` |
| Body line-height | — | — | — | 1.65 |
| Subheading | Noto Sans Tamil | 12.5pt | 700 | `#2d7a3e` |
| Section title (first page) | Noto Sans Tamil | 26pt | 900 | `#6BA82F` |
| Section label row | Noto Sans Tamil | 11pt | 600 | `#D4AF37` |
| TOC title | Noto Sans Tamil | 24pt | 900 | `#6BA82F` |
| Page header labels | Noto Sans Tamil | 9pt | 600 | `#2d7a3e` |
| Page number | Noto Sans Tamil | 11pt | 700 | `#2d7a3e` |
| Issue info (footer) | Noto Sans Tamil | 8pt | 400 | `#999` |
| Classical quote text | Noto Sans Tamil | 12pt | 600 italic | `#6BA82F` |
| Quote source | Noto Sans Tamil | 9pt | 600 | `#2d7a3e` |
| Highlights box title | Noto Sans Tamil | 10.5pt | 700 | `#2d7a3e` |
| Highlights list items | Noto Sans Tamil | 11pt | 400 | `#2B2B2B` |
| Cover magazine name | Noto Sans Tamil | 36pt | 900 | `#fff8e8` |
| Cover org name | Noto Sans Tamil | 8pt | 600 | `#D4AF37` |
| Cover tagline | Noto Sans Tamil | 8pt | 400 | `rgba(212,175,55,0.72)` |
| Cover teaser text | Noto Sans Tamil | 8.5pt | 600 | `rgba(255,255,255,0.85)` |
| Byline | Noto Sans Tamil | 9pt | 600 italic | `#6BA82F` |
| Salutation initial | Noto Sans Tamil | 15pt | 700 | `#6BA82F` |

**Minimum size rule:** Never below 11pt (senior accessibility requirement).

---

## 3. PAGE DIMENSIONS & LAYOUT

| Property | Value |
|----------|-------|
| Page size | A4 — 210mm × 297mm |
| Orientation | Portrait |
| Content padding L/R | 14mm (screen default) |
| Content padding top | 5mm (below header rule) |
| Content padding bottom | 3mm |
| Page header padding | 4mm 14mm 3.5mm |
| Page footer padding | 3mm 14mm 4.5mm |
| Header/footer rule | 1.5px gradient: transparent → #8DC63F → #D4AF37 → #8DC63F → transparent |
| Corner ornament | ❈ at 13pt, `#8b6f47` @ 28% opacity, 3.5mm from edges |

---

## 4. RESPONSIVE BREAKPOINTS

| Breakpoint | Rule | Behaviour |
|------------|------|-----------|
| ≤ 880px (tablet) | `@media screen` | Pages shrink to `min(210mm, 100%)`, aspect-ratio maintained |
| ≤ 600px (mobile) | `@media screen` | Full mobile-web layout (see below) |
| Print | `@media print` | Forces `210mm × 297mm`, no shadows, page-break-after: always |

**Mobile layout (≤ 600px):**
- Pages become continuous-scroll sections (no box-shadows, no rounded corners, no margins between pages)
- Cover uses `height: calc(100vw * 297/210)` — explicit A4 proportion
- Page chrome padding reduced to `4mm`
- Font scaling: `clamp(14pt, 5.5vw, 26pt)` for section titles, `clamp(14pt, 6vw, 24pt)` for TOC title
- Cover masthead: `height: auto` (grows to content)
- Pills: `flex-wrap: wrap` (never overflow)
- `html, body { overflow-x: hidden; max-width: 100%; }`

---

## 5. COMPONENT LIBRARY

### 5.1 Page Structure (every interior page)
```html
<div class="page">
  <div class="glossy"></div>
  <span class="corner-tl">❈</span>
  <span class="corner-br">❈</span>

  <div class="page-header">
    <span class="section-name">[SECTION_LABEL]</span>
    <span class="mag-name">வான் வளரொளி இதழ்</span>
  </div>

  <div class="content-area">
    <!-- content here -->
  </div>

  <div class="page-footer">
    <span class="issue-info">இதழ் எண்: [N] &nbsp;|&nbsp; [MONTH] [YEAR]</span>
    <span class="page-number">[N]</span>
    <img class="van-logo-footer" src="Images/VANLogoGold.jpg" alt="VAN">
  </div>
</div>
```

---

### 5.2 Section Header (first page of any section)
```html
<div class="section-header">
  <div class="topic-title">[ARTICLE TITLE]</div>
  <div class="section-label-row">
    <span class="lotus-icon">🪷</span>
    <span class="section-label">[SECTION LABEL]</span>
    <span class="lotus-icon">🪷</span>
  </div>
  <div class="title-underline"></div>
</div>
```

---

### 5.3 Continuation Banner (page 2+ of same section)
```html
<div class="continuation-banner">
  <span class="cont-section-name">[SECTION NAME]</span>
  <span class="cont-page-info">தொடர்ச்சி — பகுதி [X/Y]</span>
</div>
```

---

### 5.4 Body Text
```html
<div class="body-text">
  <p class="first-para">[First paragraph — gets 5mm text-indent]</p>
  <p>[Subsequent paragraphs]</p>
</div>
```

---

### 5.5 Subheading
```html
<div class="subhead">[SUBHEADING TEXT]</div>
```
Renders: 12.5pt bold, `#2d7a3e`, 3pt left border in `#8DC63F`.

---

### 5.6 Classical Quote (Thirukkural / Sangam verse)
```html
<div class="slim-quote">
  <div class="quote-text">
    [VERSE LINE 1]<br>
    [VERSE LINE 2]
  </div>
  <div class="quote-source">— திருக்குறள் [NUMBER], [அதிகாரம் NAME]</div>
</div>
```
Renders: centered, gold top/bottom borders, italic green text with ❝❞ marks.

---

### 5.7 Highlights / Key Points Box
```html
<div class="highlights-box">
  <div class="box-title">[BOX TITLE]</div>
  <ul>
    <li>[POINT 1]</li>
    <li>[POINT 2]</li>
  </ul>
</div>
```
Renders: light green background, 4pt left border, 🪷 bullet icons.

---

### 5.8 Numbered List
```html
<ol class="numbered-list">
  <li>[STEP 1]</li>
  <li>[STEP 2]</li>
</ol>
```

---

### 5.9 Comparison Table
```html
<table class="comparison-table">
  <tr>
    <th>[COL 1]</th>
    <th>[COL 2]</th>
  </tr>
  <tr>
    <td>[CELL]</td>
    <td>[CELL]</td>
  </tr>
</table>
```

---

### 5.10 Author Sign-off (closing block)
```html
<div class="closing">
  <p>[Closing paragraph]</p>
  <div class="sign-off">அன்புடன்,</div>
  <div class="sign-name">[AUTHOR NAME]</div>
  <div class="sign-title">[TITLE]</div>
  <div class="org-name">பெண்ணாடம் வள்ளலார் அறநிலையம்</div>
  <div class="lotus-end">🪷</div>
</div>
```

---

### 5.11 Section Divider
```html
<div class="section-divider">• &nbsp;&nbsp; • &nbsp;&nbsp; •</div>
```

---

### 5.12 Image Placeholder
```html
<div class="img-placeholder">
  <span class="img-icon">🖼</span>
  <span>[IMAGE DESCRIPTION]</span>
  <span class="img-caption">புகைப்படம்: [CREDIT]</span>
</div>
```
Replace with actual `<img>` tag once image is ready.

---

### 5.13 TOC Row
```html
<div class="toc-row [row-alt]">
  <div class="toc-accent" style="background: [COLOR];"></div>
  <div class="toc-content">
    <div class="toc-section">[SECTION NAME]</div>
    <div class="toc-desc">[DESCRIPTION]</div>
  </div>
  <div class="toc-dots"></div>
  <div class="toc-page" style="color:[COLOR];">[PAGE]</div>
</div>
```
Accent colors rotate: `#8DC63F` → `#6BA82F` → `#D4AF37` → `#2d7a3e` → repeat.
Add class `row-alt` on alternating rows for subtle gold tint background.

---

## 6. PRINT MEDIA QUERY (DO NOT REMOVE)

```css
@media print {
  body { background: none; padding: 0; margin: 0; }
  .cover-section { background: #6a6058; padding: 0; margin: 0; width: 210mm; }
  .cover, .page {
    width: 210mm; min-height: 297mm;
    box-shadow: none; border-radius: 0; margin: 0;
    page-break-after: always; break-after: page;
  }
  .glossy { display: none; }
}
@page { size: A4 portrait; margin: 0; }
```

---

## 7. IMAGE ASSETS

| File | Role | Used In |
|------|------|---------|
| `Images/VANLogoGold.jpg` | VAN logo (gold) | Every page footer |
| `Images/valarolilogogold01.jpg` | Vallalar logo (larger) | Cover publisher row, TOC banner |
| `Images/MagazineCoverImage01.jpg` | Cover background photo | Cover page only |

**Rule:** Images are stored in `Images/` subfolder. HTML references them as `src="Images/filename.jpg"`. Never embed as base64 in the template (bloats file size).

---

## 8. PRODUCTION WORKFLOW

### New Issue Checklist
```
1. cp VAN_Vallaroli_TEMPLATE_v1.html VAN_Vallaroli_[Month][Year]_v1_0_[YYYYMMDD].html
2. Find-replace all [N] → issue number
3. Find-replace all [TAMIL_MONTH] → new month
4. Find-replace all [YEAR] → year
5. Update cover image path (Images/[NewCoverImage].jpg)
6. Update [SPECIAL_LABEL] or remove .pill-special span
7. Add section pages (copy SECTION FIRST PAGE or CONTINUATION blocks)
8. Fill all [EDIT:] zones with Tamil content
9. Update TOC page numbers LAST
10. Run pre-publish checklist (see CLAUDE.md Part 6 Task E)
```

### Section Page Count Reference
| Section | Typical Pages | Notes |
|---------|--------------|-------|
| தலையங்கம் | 1 | Always page 3 |
| கருணைச் சோலை | 2–3 | |
| திருக்குறள் ஆய்வு | 2–4 | |
| சங்க இலக்கியம் | 1–2 | |
| மாணவர் வெற்றி | 1–2 | |
| நலவாழ்வு | 1–2 | |
| வீட்டுப்பெண்களுக்கு | 1–2 | |
| அறநிலைய செய்திகள் | 1–2 | |
| கோயில் கட்டமைப்பு | 1–2 | |
| கல்வெட்டு ஆய்வு | 1 | |
| தமிழிசை | 1 | |
| தமிழர் வாழ்வியல் | 1 | |
| நூல் மதிப்புரை | 1 | |
| தமிழ் எழுத்து வரலாறு | 1 | |
| அருளாளர்கள் | 1 | |
| நற்றமிழ் சொற்கள் | 0.5 | Often paired on one page |
| கவிதைகள் | 1 | |
| சிறுகதை | 1–2 | |
| ஒரு ஒழுக்கம் | 0.5 | Often paired on one page |
| இயற்கை உணவு | 0.5 | Often paired on one page |
| விவாதம் | 1–2 | |

---

## 9. DESIGN CHANGE PROTOCOL

When a design change is needed:
1. Make the change in `VAN_Vallaroli_TEMPLATE_v1.html` first
2. Test at 375px (mobile), 768px (tablet), 1280px (desktop), and print preview
3. Once approved, apply the same CSS change to the current issue file
4. Update this document (section, value, reason)
5. Commit both files together with a clear message

**Never change CSS in the issue file without updating the template.**

---

*Design System v1.2 — செந்தமிழில் அறம் வளர்க்கும் அறிவொளி இதழ் 🪷*
