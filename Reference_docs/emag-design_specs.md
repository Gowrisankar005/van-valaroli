# வான் வளரொளி இதழ் — DESIGN ASSETS & BRAND SPECIFICATIONS
## Complete design reference — guidelines + implemented system
**Version:** 1.2 (சித்திரை 2026)
**Last updated:** 2026-03-09
**Implementation source:** `VAN_Vallaroli_TEMPLATE_v1.html` → `<style>` block

> This document has two parts:
> - **Part A (Sections 1–9):** Implemented design system — exact values in the codebase
> - **Part B (Sections 10–17):** Design guidelines — standards for content creators and future designers

---

# PART A — IMPLEMENTED DESIGN SYSTEM

## 1. BRAND IDENTITY

**Magazine Name:** வான் வளரொளி இதழ்
**Publisher:** வள்ளலார் அறநிலையம் (VAN)
**Tagline:** செந்தமிழில் அறம் வளர்க்கும் அறிவொளி இதழ்

**Symbolism:**
- **Lotus (தாமரை):** Wisdom, purity, spiritual awakening
- **சுடரொடு அகல் விளக்கு (Brightly lit lamp):** ஞானம் (enlightenment), knowledge, divine light

---

## 2. BRAND PALETTE

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
| `--highlight-bg` | `#f4fbe8` | Highlights box background |
| `--light-green-bg` | `#F0F8E8` | Sidebars, accent box backgrounds |

---

## 3. TYPOGRAPHY

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

## 4. PAGE DIMENSIONS & LAYOUT

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
| Page background | `linear-gradient(180deg, #fffef5 0%, #fef9f2 100%)` |

---

## 5. RESPONSIVE BREAKPOINTS

| Breakpoint | Rule | Behaviour |
|------------|------|-----------|
| ≤ 880px (tablet) | `@media screen` | Pages shrink to `min(210mm, 100%)`, A4 aspect-ratio maintained |
| ≤ 600px (mobile) | `@media screen` | True mobile-web layout — continuous scroll, no A4 box model |
| Print | `@media print` | Forces `210mm × 297mm`, no shadows, `page-break-after: always` |

**Mobile layout specifics (≤ 600px):**
- Cover: `height: calc(100vw * 297/210)` — explicit proportional height
- Pages: no box-shadows, no rounded corners, no margins between — become scroll sections
- Page chrome padding: reduced to `4mm`
- Font scaling: `clamp(14pt, 5.5vw, 26pt)` section titles; `clamp(14pt, 6vw, 24pt)` TOC
- Cover masthead: `height: auto` (grows to content, no clipping)
- Pills: `flex-wrap: wrap` (never overflow narrow screens)
- Root: `html, body { overflow-x: hidden; max-width: 100%; }`

---

## 6. COMPONENT LIBRARY

### 6.1 Page Structure (every interior page)
```html
<div class="page">
  <div class="glossy"></div>
  <span class="corner-tl">❈</span>
  <span class="corner-br">❈</span>
  <div class="page-header">
    <span class="section-name">[SECTION_LABEL]</span>
    <span class="mag-name">வான் வளரொளி இதழ்</span>
  </div>
  <div class="content-area"><!-- content --></div>
  <div class="page-footer">
    <span class="issue-info">இதழ் எண்: [N] &nbsp;|&nbsp; [MONTH] [YEAR]</span>
    <span class="page-number">[N]</span>
    <img class="van-logo-footer" src="Images/VANLogoGold.jpg" alt="VAN">
  </div>
</div>
```

### 6.2 Section Header (first page of any section)
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

### 6.3 Continuation Banner (page 2+ of same section)
```html
<div class="continuation-banner">
  <span class="cont-section-name">[SECTION NAME]</span>
  <span class="cont-page-info">தொடர்ச்சி — பகுதி [X/Y]</span>
</div>
```

### 6.4 Body Text
```html
<div class="body-text">
  <p class="first-para">[First paragraph — 5mm text-indent]</p>
  <p>[Subsequent paragraphs]</p>
</div>
```

### 6.5 Subheading
```html
<div class="subhead">[SUBHEADING TEXT]</div>
```
Renders: 12.5pt bold `#2d7a3e`, 3pt left border in `#8DC63F`.

### 6.6 Classical Quote (Thirukkural / Sangam verse)
```html
<div class="slim-quote">
  <div class="quote-text">[VERSE LINE 1]<br>[VERSE LINE 2]</div>
  <div class="quote-source">— திருக்குறள் [NUMBER], [அதிகாரம் NAME]</div>
</div>
```
Renders: centered, gold top/bottom borders, italic green text with ❝❞ marks.

### 6.7 Highlights Box
```html
<div class="highlights-box">
  <div class="box-title">[BOX TITLE]</div>
  <ul>
    <li>[POINT 1]</li>
    <li>[POINT 2]</li>
  </ul>
</div>
```
Renders: light green `#f4fbe8` background, 4pt `#6BA82F` left border, 🪷 bullet icons.

### 6.8 Numbered List
```html
<ol class="numbered-list">
  <li>[STEP 1]</li>
</ol>
```

### 6.9 Comparison Table
```html
<table class="comparison-table">
  <tr><th>[COL 1]</th><th>[COL 2]</th></tr>
  <tr><td>[CELL]</td><td>[CELL]</td></tr>
</table>
```
Renders: `#6BA82F` header row, alternating `#f9f9f5` rows, `#8DC63F` borders.

### 6.10 Author Sign-off
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

### 6.11 Section Divider
```html
<div class="section-divider">• &nbsp;&nbsp; • &nbsp;&nbsp; •</div>
```

### 6.12 Image Placeholder
```html
<div class="img-placeholder">
  <span class="img-icon">🖼</span>
  <span>[IMAGE DESCRIPTION]</span>
  <span class="img-caption">புகைப்படம்: [CREDIT]</span>
</div>
```
Replace with `<img>` tag once image is sourced.

### 6.13 TOC Row
```html
<div class="toc-row [row-alt on alternating rows]">
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

---

## 7. PRINT MEDIA QUERY (DO NOT REMOVE OR MODIFY)

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

## 8. IMAGE ASSETS

| File | Role | Used In |
|------|------|---------|
| `Images/VANLogoGold.jpg` | VAN logo (gold) | Every page footer |
| `Images/valarolilogogold01.jpg` | Vallalar logo (larger) | Cover publisher row, TOC banner |
| `Images/MagazineCoverImage01.jpg` | Cover background photo | Cover page only |

**Rule:** Always reference as `src="Images/filename.jpg"`. Never embed as base64 in the template.

---

## 9. PRODUCTION WORKFLOW

### New Issue Checklist
```
1. cp VAN_Vallaroli_TEMPLATE_v1.html  VAN_Vallaroli_[Month][Year]_v1_0_[YYYYMMDD].html
2. Find-replace [N]           → issue number
3. Find-replace [TAMIL_MONTH] → new month name
4. Find-replace [YEAR]        → year
5. Update cover image src (Images/[NewCoverImage].jpg)
6. Update [SPECIAL_LABEL] or remove .pill-special span if not a special issue
7. Add section pages (copy SECTION FIRST PAGE or CONTINUATION blocks from template)
8. Fill all <!-- EDIT: --> zones with Tamil content
9. Update TOC page numbers LAST (after all pages are placed)
10. Run pre-publish checklist (Section 15 below)
```

### Design Change Protocol
When a design change is needed:
1. Make the change in `VAN_Vallaroli_TEMPLATE_v1.html` first
2. Test at 375px (mobile), 768px (tablet), 1280px (desktop), and print preview
3. Once approved, apply the same CSS change to the current issue file
4. Update this document (section, value, reason for change)
5. Commit both template + issue file together

**Never change CSS in the issue file without first updating the template.**

---

---

# PART B — DESIGN GUIDELINES

## 10. VISUAL ELEMENTS

### Kolam Patterns *(future enhancement — not yet implemented in CSS)*
**Uses:** Page borders, section dividers, decorative frames

**Types to Use:**
- **மாவிலைக் கோலம் (Mango leaf kolam):** For auspicious sections
- **தாமரைக் கோலம் (Lotus kolam):** For spiritual/classical content
- **பூரண கும்பக் கோலம் (Full pot kolam):** For prosperity-related content
- **காலைக் கோலம் (Morning kolam):** Simple, geometric for clean aesthetics

**Application:**
- Borders: Thin (2–3mm), subtle, not overwhelming
- Corner decorations: Small (15mm × 15mm)
- Color: `#8DC63F` or `#D4AF37` (green or gold)
- Opacity: 40–60% (subtle, not distracting)

### Traditional Motifs *(future enhancement)*
**Motif Library:**
- **Lotus (தாமரை):** Single flower or blooming sequence
- **Oil Lamp (விளக்கு):** Traditional clay lamp with flame
- **Peacock (மயில்):** Tamil Nadu's state bird, symbol of beauty
- **Temple Gopuram:** Silhouette or simplified architectural outline
- **Mango Leaves (மாவிலை):** Auspicious garland
- **Paisley (மாங்காய் வடிவம்):** Traditional paisley motif
- **Tanjore Art Elements:** Gold work patterns, jewelry motifs
- **Bronze Sculpture Silhouettes:** Nataraja, dancing figures

**Application Guidelines:**
- Use sparingly (elegance over clutter)
- Monochrome or duotone (green/gold only)
- Size: Small to medium (10–30mm)
- Placement: Section breaks, beside titles, corner decorations

### செப்பேடு (Copper Plate) Style Frames
**For:** Classical quotes, திருக்குறள், Sangam verses, important announcements

**Characteristics:**
- Ornate border mimicking ancient copper plate inscriptions
- Aged/textured appearance (optional)
- Gold or bronze coloring (`#D4AF37`, `#CC7722`)
- Interior: Cream or light background (`#FFFEF0`)
- Text: Centered, traditional font style

---

## 11. COVER PAGE DESIGN

### Current Implemented Structure (v1.2)
1. **Masthead** (dark green top band, ~26% height)
   - Org name + magazine name + tagline + issue pills
2. **Cover image** (full-bleed background photograph)
3. **Floating quote** (centered over image, ~top 30%)
4. **Bottom band** (dark green, ~29% height) — teasers + publisher row

### Color Scheme Options
- **Option 1 (Current):** Dark green overlay bands, full-bleed photo, white text, gold accents
- **Option 2:** White background, green title, gold accents *(lighter, print-friendly)*
- **Option 3:** Cream/parchment background (`#FFFEF0`), traditional colors *(classical feel)*

### Cover Image Guidelines
- High-quality thematic photograph — relates to monthly theme or lead article
- Preferred: Tamil temples, classical art, nature from Sangam literature, VAN activities
- Must have enough dark/neutral areas for text overlay to remain readable

---

## 12. SECTION HEADER DESIGNS

### Standard (Implemented)
- Topic title: 26pt, 900 weight, `#6BA82F`, centered
- Label row: 🪷 `section-label` 🪷 with `#D4AF37` text
- Gradient underline: `transparent → #8DC63F → #D4AF37 → #8DC63F → transparent`

### Alternative: Minimalist Header *(not yet in CSS)*
- Title only: 16pt bold, `#6BA82F`
- Simple underline: 2pt solid `#8DC63F`
- White background, 10mm space above and below

### Standard Ornate Header *(design reference)*
```
┌────────────────────────────────────────┐
│  [Lotus icon] பகுதி தலைப்பு [Lamp icon] │
│  ════════════════════════════════════  │
└────────────────────────────────────────┘
```
- Background: Light green (`#F0F8E8`) or white with green border
- Border: 1pt solid `#8DC63F` OR decorative kolam pattern
- Title: Centered, 16pt bold, `#6BA82F`
- Icons: 12mm × 12mm flanking title

---

## 13. IMAGE GUIDELINES

### Technical Specifications
- **Resolution:** Minimum 300 DPI at final print size
- **Format:** JPEG (photos), PNG (graphics with transparency)
- **Color Mode:** CMYK for print; RGB acceptable for digital-only
- **File Size:** Balance quality and PDF file size

### Image Types & Uses
**Photography:**
- Tamil temples and architecture
- Classical art (Tanjore paintings, bronze sculptures)
- Nature (flowers, plants from Sangam literature)
- VAN social service activities (documentary style)
- Cultural events and festivals
- Traditional Tamil lifestyle

**Graphics/Illustrations:**
- Infographics explaining concepts (in Tamil)
- Diagrams for science articles
- Maps (historical Tamil regions, temple locations)
- Timelines and data visualizations

**Decorative:**
- Kolam patterns (vector or high-res raster)
- Traditional motifs, borders, frames, section icons

### Image Placement Rules
1. Minimum size: 40mm × 40mm (smaller = pixelated when printed)
2. Preferred sizes: Half-page (90mm wide) or full-page (170mm wide)
3. Alignment: Centered or aligned with text column
4. Text clearance: 5mm minimum around any image
5. Caption: Always below image, 10pt, credited

### Caption Format
```
[Image description in Tamil]
புகைப்படம்: [Photographer name] / [Source]
```

### Image Sourcing
- **Original photography:** VAN archives, contributors
- **Public domain:** Wikimedia Commons, Tamil temple archives
- **Licensed:** Credit clearly, confirm usage rights before publishing
- **Never:** Use copyrighted images without permission

---

## 14. COLOR USAGE GUIDELINES

### Background Colors
- **Primary:** White-tinted warm cream (`#fffef5` → `#fef9f2`) — all interior pages
- **Accent boxes:** Light green (`#F0F8E8`) — sidebars, highlights boxes
- **Classical sections:** Cream/Parchment (`#FFFEF0`) — optional for quote-heavy pages
- **Avoid:** Dark backgrounds (hard to read, not senior-friendly)

### Text Colors
- **Body text:** Charcoal `#2B2B2B` only — never pure black
- **Headers:** Deep green `#2d7a3e` or medium green `#6BA82F`
- **Highlights/accents:** VAN green `#8DC63F` — used sparingly
- **Captions/Secondary:** Medium gray `#5A5A5A` or `#999`
- **Avoid:** Light text on white, low-contrast combinations

### Accent Colors
- **Borders:** `#8DC63F` (1–2pt width)
- **Dividers:** `#8DC63F` or gold `#D4AF37`
- **Icons:** `#8DC63F` or gold, depending on context
- **Pull quotes:** Green or gold borders with cream fill

### Accessibility Standards
- **Contrast ratio:** Minimum 4.5:1 for body text (WCAG AA)
- **Test:** Print in grayscale to ensure readability
- **Color-blindness friendly:** Never rely on color alone to convey information

---

## 15. BRAND CONSISTENCY CHECKLIST

Run this before marking any issue as final:

**Content:**
- [ ] VAN logo appears on cover and in footer of every interior page
- [ ] Lotus 🪷 symbol used at least in section labels
- [ ] Color palette used correctly: `#8DC63F`, `#6BA82F`, `#D4AF37`, `#2d7a3e`
- [ ] Tamil numerals used for page numbers in footers
- [ ] Issue number and Tamil month consistent across all footers and cover
- [ ] TOC page numbers match actual page positions
- [ ] All செந்தமிழ் substitutions applied (see `senthamizh_guide.md`)

**Typography:**
- [ ] All body text minimum 12pt, no exceptions
- [ ] No text below 11pt anywhere in the document
- [ ] Consistent font (Noto Sans Tamil) throughout
- [ ] Classical quotes italicized in `.slim-quote` blocks

**Design:**
- [ ] Senior-friendly readability: 12pt+, high contrast, generous margins
- [ ] Generous white space — no cluttered pages
- [ ] Traditional aesthetic maintained (lotus, gold accents, green palette)
- [ ] Professional, dignified appearance appropriate for VAN

**Technical:**
- [ ] Every `<div class="page">` has exactly one `.page-header`, `.content-area`, `.page-footer`
- [ ] `VANLogoGold.jpg` src present in every footer
- [ ] `<title>` tag matches cover month/year
- [ ] No broken Tamil characters (no replacement characters ▯ or ? boxes)
- [ ] Print media query intact at bottom of `<style>` block
- [ ] Images referenced as `Images/filename.jpg` (not base64)

---

## 16. DESIGN DON'Ts

**Avoid:**
- ❌ Overly busy layouts (confusing for senior readers)
- ❌ Low contrast color combinations
- ❌ Text smaller than 11pt anywhere
- ❌ More than 2–3 font styles on a single page
- ❌ Clipart or unprofessional graphics
- ❌ Stretched or distorted images
- ❌ Cluttered pages without white space
- ❌ Trendy designs that clash with the traditional Tamil aesthetic
- ❌ Dark backgrounds with light text (except the cover overlay bands)
- ❌ Excessive use of decorative elements — elegance through simplicity

**Remember:** Less is more. Every element must earn its place.

---

## 17. ACCESSIBILITY NOTES

**For Senior Readers (primary audience, 40+):**
- Large, clear fonts — 12pt body minimum
- High contrast — body text `#2B2B2B` on near-white backgrounds
- Simple, predictable navigation — consistent header/footer placement
- No small reversed text (white on dark), except cover overlay areas
- Clear section breaks between topics
- Consistent layout — readers know where to find headers, footers, page numbers

**For Print Accessibility:**
- Test-print pages to ensure Tamil characters render at target printer
- Check that green shades (`#8DC63F`, `#6BA82F`) print clearly — not too light
- Verify images are sharp at 300 DPI when printed
- Grayscale test: print one page in B&W — must still be fully readable

---

## 18. FILE SPECIFICATIONS

### Final Output Requirements

**For Email Distribution (web PDF):**
- File size: Target under 10 MB
- Resolution: 150 DPI (acceptable for screen reading)
- Compression: Medium JPEG quality for images
- Fonts: Embedded
- Color space: RGB

**For Print / High-Quality Archive:**
- File size: No limit — quality is priority
- Resolution: 300 DPI
- Compression: Minimal or none
- Fonts: Embedded and outlined if possible
- Color space: CMYK preferred
- Bleed: 3mm if printing professionally

### File Naming Convention
```
HTML source:
VAN_Vallaroli_[Month][Year]_v[Major]_[Minor]_[YYYYMMDD].html

PDF output:
VAN_Vallaroli_[Year]_[Month]_Issue[N]_Web.pdf       ← email distribution
VAN_Vallaroli_[Year]_[Month]_Issue[N]_Print.pdf     ← high-quality/archive
```

---

## 19. PRINT SPECIFICATIONS

### Paper (if physically printing)
- **Type:** Matte or semi-gloss (better readability than glossy for seniors)
- **Weight:** 100–120 GSM (substantial but not too heavy)
- **Color:** White or natural cream
- **Finish:** Smooth (not textured — seniors' eyes)

### Binding
- **Saddle stitch:** For 15–25 pages (cost-effective)
- **Perfect binding:** For thicker issues (more professional)
- **Spiral/Wire-O:** Lays flat — best for ease of reading

### Cover
- **Paper:** 200–250 GSM (heavier than interior)
- **Finish:** Matte lamination (durable, less glare)
- **Optional:** Spot UV on logo/title for premium look

---

*Design System v1.2 — செந்தமிழில் அறம் வளர்க்கும் அறிவொளி இதழ் 🪷*
*Original guidelines preserved + implementation details added — do not split these documents.*
