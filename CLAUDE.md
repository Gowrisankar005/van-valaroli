# CLAUDE.md — வான் வளரொளி இதழ் Production System
## Instructions for Claude Code

> **Project:** வான் வளரொளி இதழ் (Van Vallaroli Magazine)
> **Publisher:** வள்ளலார் அறநிலையம் (VAN — Vallalar Aranilayam)
> **Claude Code's Role:** Maintainer and builder of the magazine's HTML output
> **Last Synced From:** Claude.ai project session — சித்திரை 2026

---

## PART 1: PROJECT ORIENTATION

### What This Magazine Is
வான் வளரொளி இதழ் is a monthly Tamil e-magazine published by பெண்ணாடம் வள்ளலார் அறநிலையம் (VAN). Its mission is to spread செந்தமிழ் (pure Tamil language), வள்ளலார்'s teachings on compassion and ethics, and Tamil cultural heritage.

- **Audience:** Tamil speakers 40+, வள்ளலார் followers, intergenerational Tamil families
- **Format:** A4 HTML → print-to-PDF, 15–25 pages, 15–20 sections per issue
- **Output file convention:** `VAN_Vallaroli_[Tamil Month][Year]_v[X.X]_[YYYYMMDD].html`
- **Current file (Issue 1):** `VAN_Vallaroli_Chittirai2026_v1_1_20260307.html` (34 pages)

### Gowri's Role (Your Human Collaborator)
Gowri is the publisher and coordinator. She reviews content, enforces செந்தமிழ் standards, manages contributors, and gives final editorial approval. She uses Claude.ai for content creation and asks Claude Code (you) for HTML maintenance, structural refactoring, and issue assembly.

---

## PART 2: CURRENT FILE ARCHITECTURE

### The Current Structure (Single Monolithic HTML)
The magazine is currently one self-contained HTML file where CSS, layout, and content are all embedded together. This is intentional for portability (single file = email-ready, no dependencies).

```
[single HTML file]
├── <head> — Google Fonts import (Noto Sans Tamil)
├── <style> — ALL CSS (~750 lines, embedded)
│   ├── Body/global styles
│   ├── Cover page styles (.cover, .masthead, .quote-float, etc.)
│   ├── TOC page styles (.toc-*, .issue-banner, etc.)
│   ├── Interior page styles (.page, .page-header, .page-footer, etc.)
│   ├── Content component styles (.section-header, .slim-quote, .highlights-box, etc.)
│   └── Print media queries
└── <body>
    ├── <!-- COVER PAGE --> div.cover (A4 210×297mm)
    ├── <!-- TOC PAGE --> div.page (பொருளடக்கம்)
    ├── <!-- PAGE 3 --> div.page (தலையங்கம் — Editorial)
    ├── <!-- PAGE 4 --> div.page (Section content...)
    ├── ... (pages 4–33 = content sections)
    └── <!-- PAGE 34 --> div.page (Next issue preview + contact)
```

### How Each Interior Page Is Built
Every content page follows this exact structure — learn it well:

```html
<div class="page">
  <div class="glossy"></div>
  <span class="corner-tl">❈</span>
  <span class="corner-br">❈</span>

  <!-- HEADER -->
  <div class="page-header">
    <span class="section-name">[SECTION NAME IN TAMIL]</span>
    <span class="mag-name">வான் வளரொளி இதழ்</span>
  </div>

  <!-- CONTENT -->
  <div class="content-area">

    <!-- Section title block — use for first page of a section -->
    <div class="section-header">
      <div class="topic-title">[ARTICLE TITLE]</div>
      <div class="section-label-row">
        <span class="lotus-icon">🪷</span>
        <span class="section-label">[SECTION LABEL]</span>
        <span class="lotus-icon">🪷</span>
      </div>
      <div class="title-underline"></div>
    </div>

    <!-- Continuation banner — use for page 2+ of same section -->
    <div class="continuation-banner">
      <span class="cont-section-name">[SECTION NAME]</span>
      <span class="cont-page-info">தொடர்ச்சி — பகுதி [X/Y]</span>
    </div>

    <div class="section-divider">&#x2022; &nbsp;&nbsp; &#x2022; &nbsp;&nbsp; &#x2022;</div>

    <div class="body-text">
      <!-- Body content goes here — see content components below -->
    </div>

  </div><!-- .content-area -->

  <!-- FOOTER -->
  <div class="page-footer">
    <span class="issue-info">இதழ் எண்: [N] &nbsp;|&nbsp; [Tamil Month] [Year]</span>
    <span class="page-number">[PAGE NUMBER]</span>
    <img class="van-logo-footer" src="VANLogoGold.jpg" alt="VAN">
  </div>

</div><!-- .page [N] -->
```

### Content Components (CSS Classes to Use)

| Component | HTML | When to Use |
|-----------|------|-------------|
| Body paragraph | `<p>text</p>` | All running text |
| Subheading | `<div class="subhead">text</div>` | Section sub-topics |
| Classical quote block | `<div class="slim-quote"><div class="quote-text">verse</div><div class="quote-source">source</div></div>` | Thirukkural, Sangam verses |
| Highlights box | `<div class="highlights-box"><div class="box-title">title</div><ul><li>item</li></ul></div>` | Key points, lists |
| Numbered list | `<ol class="numbered-list"><li>item</li></ol>` | Step-by-step instructions |
| Author byline | `<div class="author-byline">text</div>` | Article attribution |
| Section divider | `<div class="section-divider">• &nbsp; • &nbsp; •</div>` | Between sub-sections |

---

## PART 3: DESIGN SYSTEM — DO NOT ALTER THESE

### Brand Colors (Non-Negotiable)
```css
/* Primary greens */
--van-green-mid: #8DC63F;      /* Accent, subheadings */
--van-green-deep: #2d7a3e;     /* Page header text, page numbers */
--van-green-dark: #6BA82F;     /* Highlights box border, section labels */

/* Gold */
--van-gold: #D4AF37;           /* Decorative elements, pull quote lines */

/* Text */
--body-text: #2B2B2B;          /* All body paragraphs */
--subtle-text: #666666;        /* Sign titles, org names */

/* Page backgrounds */
--page-bg-top: #fffef5;
--page-bg-bottom: #fef9f2;
```

### Typography (Non-Negotiable)
- **Font:** Noto Sans Tamil (Google Fonts) — load via `<link>` in `<head>`
- **Body text:** 12–13pt, line-height 1.5, color `#2B2B2B`, justified
- **Subheadings:** 13–14pt, bold, color `#8DC63F` with left bar accent
- **Classical quotes:** Centered, 13–14pt, inside `.slim-quote` block
- **Minimum size:** 11pt (senior accessibility requirement)
- **Page header section name:** Color `#D4AF37` (gold)
- **Page number:** Color `#2d7a3e` (deep green)

### Page Dimensions
- **Size:** A4 = 210mm × 297mm
- **Content padding:** 14mm left/right, 5mm top (below header), 3mm bottom
- **All pages must include:** `.glossy` overlay, `corner-tl`/`corner-br` ❈ motifs
- **Decorative corners:** Color `#8b6f47`, opacity ~9%

### Print Media Query (Always Preserve)
```css
@media print {
  body { background: none; padding: 0; margin: 0; }
  .page { box-shadow: none; border-radius: 0; margin: 0; page-break-after: always; break-after: page; }
  .glossy { display: none; }
}
@page { size: A4 portrait; margin: 0; }
```

### Image Assets (Required Files in Same Directory)
```
VANLogoGold.jpg          — Footer logo on every page
valarolilogogold01.jpg   — Larger logo used on cover
MagazineCoverImage01.jpg — Cover background photo
```
If these files are missing or renamed, ALL page footers and the cover will break.

---

## PART 4: ISSUE METADATA — WHAT TO UPDATE EACH MONTH

When creating a new issue, these strings must be updated consistently throughout the entire HTML file. Use find-and-replace — they appear on every page.

| Field | Location | Example Current Value |
|-------|----------|-----------------------|
| Issue number | Every page footer `<span class="issue-info">` | `இதழ் எண்: 1` |
| Tamil month + year | Every page footer + cover masthead | `சித்திரை 2026` |
| Special issue label | Cover `.pill-special` span | `கல்வி சிறப்பிதழ்` |
| Issue number pill | Cover `.pill` span | `இதழ் 1 · சித்திரை 2026` |
| Next issue preview | Last content page | `வைகாசி 2026` |
| HTML `<title>` tag | `<head>` | `வான் வளரொளி இதழ் — சித்திரை ௨௦௨௬ — முழு இதழ்` |

**Tamil Numerals for Page Numbers and Years:**
```
௧=1  ௨=2  ௩=3  ௪=4  ௫=5  ௬=6  ௭=7  ௮=8  ௯=9  ௰=10
௨௦௨௬ = 2026   சித்திரை = Chittirai   வைகாசி = Vaigasi
கார்த்திகை = Karthigai   மார்கழி = Margazhi   ஐப்பசி = Aippasi
```

---

## PART 5: SECTION REGISTRY

The magazine has up to 21 section types. Each issue uses 15–20 of them. This is the master registry for naming, page-header labels, and typical page count.

| # | Section Tamil Name | Page Header Label | Typical Pages |
|---|--------------------|-------------------|---------------|
| 1 | தலையங்கம் | தலையங்கம் | 1 |
| 2 | கருணைச் சோலைக் கட்டுரை | கருணைச் சோலை | 2–3 |
| 3 | திருக்குறள் ஆய்வு | திருக்குறள் ஆய்வு | 2–4 |
| 4 | சங்க இலக்கியத் தொடர் | சங்க இலக்கியம் | 1–2 |
| 5 | மாணவர் கல்வி வெற்றித் தொடர் | மாணவர் வெற்றி | 1–2 |
| 6 | நலவாழ்வு / அறிவியல் | நலவாழ்வு | 1 |
| 7 | வீட்டுப்பெண்களுக்கு | வீட்டுப்பெண்களுக்கு | 1–2 |
| 8 | அறநிலைய செய்திகள் | அறநிலையச் செய்திகள் | 1–2 |
| 9 | தமிழகக் கோயில் கட்டமைப்பு | கோயில் கட்டமைப்பு | 1–2 |
| 10 | கல்வெட்டில் அறச் செய்திகள் | கல்வெட்டு ஆய்வு | 1 |
| 11 | தமிழிசை வரலாறு | தமிழிசை | 1 |
| 12 | தமிழர் வாழ்வியல் | தமிழர் வாழ்வியல் | 1 |
| 13 | நூல் மதிப்புரை | நூல் மதிப்புரை | 1 |
| 14 | தமிழ் எழுத்துக்களின் வரலாறு | தமிழ் எழுத்து வரலாறு | 1 |
| 15 | அருளாளர்களின் அறம் | அருளாளர்கள் | 1 |
| 16 | நற்றமிழ் சொற்கள் அறிவோம் | நற்றமிழ் சொற்கள் | 0.5 |
| 17 | கவிதைகள் | கவிதைகள் | 1 |
| 18 | சிறுகதை | சிறுகதை | 1–2 |
| 19 | ஒரு ஒழுக்கம் | ஒரு ஒழுக்கம் | 0.5 |
| 20 | இயற்கை உணவு | இயற்கை உணவு | 0.5 |
| 21 | விவாதம்: இரு பார்வை | விவாதம் | 1–2 |

**Fixed Structure (Always in this order):**
1. Cover page (`.cover` div — special structure, not `.page`)
2. பொருளடக்கம் (TOC — special structure)
3. தலையங்கம் (Editorial — page 3)
4. Content sections (pages 4 onward, in editorial order)
5. அடுத்த இதழில் / closing page (always last)

---

## PART 6: COMMON MAINTENANCE TASKS

### Task A: Update Issue Metadata for New Month
```bash
# In the HTML file, do these replacements (in order):
# 1. Update <title> tag
# 2. Update cover masthead pill text
# 3. Update cover special edition label (or remove if not applicable)
# 4. Find-replace all footer "issue info" spans
# 5. Update "அடுத்த இதழில்" (next issue preview) page
```

### Task B: Add a New Section Page
1. Locate the page comment block: `<!-- PAGE [N] — [section name] -->`
2. Copy the standard interior page template (Part 2 above)
3. Set the correct `section-name` in the `.page-header`
4. Use `section-header` block for the first page of any section
5. Use `continuation-banner` for page 2+ of the same section
6. Update the page footer with correct page number
7. Update the TOC page to include the new section with correct page number
8. Renumber all subsequent page footers if inserting mid-document

### Task C: Update the TOC
The TOC is on the second `<div class="page">` in the body. Each TOC row follows this structure:
```html
<div class="toc-row [row-alt?]">
  <div class="toc-accent" style="background: [color];"></div>
  <div class="toc-content">
    <div class="toc-section">[Section Tamil Name]</div>
    <div class="toc-desc">[Brief description or subtitle]</div>
  </div>
  <div class="toc-dots"></div>
  <div class="toc-page" style="color:[color];">[Tamil numeral page]</div>
</div>
```
TOC accent colors rotate through: `#8DC63F`, `#6BA82F`, `#D4AF37`, `#2d7a3e`

### Task D: Replace/Edit Content in an Existing Section
1. Find the section using the page comment: `Ctrl+F` / `grep` for `<!-- PAGE [N]`
2. Edit only within the `.body-text` div of that page
3. Never alter `.page-header`, `.page-footer`, `.section-header` structure
4. Preserve all CSS class names — the design is defined by classes, not inline styles
5. Exception: Inline `style=""` overrides on specific elements are acceptable for one-off adjustments

### Task E: Validate Before Handing Back
Run through this quick checklist before saving final output:
- [ ] Every `<div class="page">` has exactly one `.page-header`, one `.content-area`, one `.page-footer`
- [ ] Page numbers in footers are sequential (3, 4, 5... — cover and TOC don't have footers with numbers)
- [ ] Issue info string is identical across all footers
- [ ] `VANLogoGold.jpg` `src` attribute is present in every footer
- [ ] TOC page numbers match actual page positions
- [ ] `<title>` tag matches cover month/year
- [ ] No broken Tamil characters (no replacement characters ▯ or ? boxes)
- [ ] Print media query is intact at bottom of `<style>` block

---

## PART 7: BUILDING A NEW ISSUE FROM SCRATCH

### Step 1 — Create the new file
Copy the previous issue HTML as a starting template:
```bash
cp VAN_Vallaroli_Chittirai2026_v1_1_20260307.html VAN_Vallaroli_[NewMonth][Year]_v1_0_[YYYYMMDD].html
```

### Step 2 — Update global metadata (find-replace)
| Find | Replace With |
|------|-------------|
| `ஐப்பசி 2026` | `[New Tamil Month] [Year]` |
| `இதழ் எண்: 1` | `இதழ் எண்: [N]` |
| `இதழ் 1 &nbsp;·&nbsp; சித்திரை 2026` | `இதழ் [N] &nbsp;·&nbsp; [New Month] [Year]` |
| `கல்வி சிறப்பிதழ்` | `[New special label or remove .pill-special]` |

### Step 3 — Replace section content
For each section, receive the content from Gowri (as markdown or plain text), then:
- Convert to the appropriate HTML components (paragraphs, subheads, slim-quotes, highlights-boxes)
- Apply செந்தமிழ் vocabulary from Part 9 of this file
- Wrap in the standard page structure
- Set correct page numbers throughout

### Step 4 — Update TOC
After all pages are placed, count actual page numbers and update the TOC rows.

### Step 5 — Update next-issue preview
On the last content page, update the "அடுத்த இதழில்" section with content for the upcoming issue.

### Step 6 — Final validation
Run the Task E checklist (Part 6 above).

---

## PART 8: CONTENT FORMATTING RULES

### Thirukkural Citation Format
```html
<div class="slim-quote">
  <div class="quote-text">
    [Line 1 of Kural]<br>
    [Line 2 of Kural]
  </div>
  <div class="quote-source">— திருக்குறள் [NUMBER], [அதிகாரம் name]</div>
</div>
```
Always verify Thirukkural text and numbers from the canonical source. Do not paraphrase the verse itself.

### Sangam Literature Citation Format
```html
<div class="slim-quote">
  <div class="quote-text">[Verse lines]</div>
  <div class="quote-source">— [நூல் name], [பாடல் number] | புலவர்: [Name]</div>
</div>
```

### Highlights / Key Points Box
```html
<div class="highlights-box">
  <div class="box-title">[Box Title]</div>
  <ul>
    <li>[Point 1]</li>
    <li>[Point 2]</li>
  </ul>
</div>
```

### Multi-column Comparison Tables
```html
<table class="comparison-table">
  <tr>
    <th>[Col 1 Header]</th>
    <th>[Col 2 Header]</th>
  </tr>
  <tr>
    <td>[Cell]</td>
    <td>[Cell]</td>
  </tr>
</table>
```

### Author Sign-off (Editorial / Special Articles)
```html
<div class="closing">
  <p>[Closing paragraph]</p>
  <div class="sign-off">அன்புடன்,</div>
  <div class="sign-name">[Author Name in Tamil]</div>
  <div class="sign-title">[Title]</div>
  <div class="org-name">பெண்ணாடம் வள்ளலார் அறநிலையம்</div>
  <div class="lotus-end">🪷</div>
</div>
```

---

## PART 9: செந்தமிழ் STANDARDS — MANDATORY SUBSTITUTIONS

The magazine enforces pure Tamil vocabulary. These substitutions are non-negotiable. When converting content from markdown/plain text to HTML, apply all applicable substitutions automatically.

### Technology
| ❌ Avoid | ✅ Use Instead |
|---------|--------------|
| கம்ப்யூட்டர் | கணினி |
| லேப்டாப் | மடிக்கணினி |
| மொபைல் / போன் | கைப்பேசி / அலைபேசி |
| இன்டர்நெட் | இணையம் |
| இ-மெயில் | மின்னஞ்சல் |
| வெப்சைட் | இணையதளம் |

### Education
| ❌ Avoid | ✅ Use Instead |
|---------|--------------|
| ஸ்கூல் | பள்ளி |
| காலேஜ் | கல்லூரி |
| டீச்சர் | ஆசிரியர் / ஆசிரியை |
| ஸ்டூடென்ட் | மாணவர் / மாணவி |
| கிளாஸ் ரூம் | வகுப்பறை |

### Healthcare
| ❌ Avoid | ✅ Use Instead |
|---------|--------------|
| ஹாஸ்பிடல் | மருத்துவமனை |
| டாக்டர் | மருத்துவர் |
| நர்ஸ் | செவிலியர் |
| மெடிசின் | மருந்து |
| ஆப்பரேஷன் | அறுவை சிகிச்சை |

### Sanskrit Loan Words
| ❌ Avoid | ✅ Use Instead |
|---------|--------------|
| தர்மம் | அறம் |
| புண்ணியம் | நன்மை |
| சுத்தம் | தூய்மை |
| ஆரோக்கியம் | நலம் / நலனுடைமை |
| ஞானம் (OK to use) | அறிவொளி (preferred in headers) |

### Transport
| ❌ Avoid | ✅ Use Instead |
|---------|--------------|
| பஸ் | பேருந்து |
| டிரெய்ன் | தொடர்வண்டி |
| ரோடு | சாலை |
| ஏர்போர்ட் | விமான நிலையம் |

---

## PART 10: VAN VOICE — EDITORIAL STYLE GUIDE

Every article in this magazine must sound like it was written by a wise, warm, learned elder — not a textbook and not a clickbait blog. This is the "VAN Voice."

### Three Pillars
1. **சுஜாதா's clarity** — Simple explanations, real-world examples, no unnecessary complexity
2. **பாவண்ணன்'s grounding** — Deep respect for classical texts, tradition treated with reverence
3. **சிற்பி's compassion** — Warm, socially conscious, emotionally honest

### Characteristics
- Conversational yet respectful (like a learned elder speaking to family)
- Scholarly without being pedantic
- Uses storytelling and real-life examples
- Balances tradition with contemporary relevance
- Inspires without preaching
- Evidence-based yet spiritually aware

### Intergenerational Appeal Test
Before finalizing any article, ask:
- Would a 65-year-old வள்ளலார் devotee feel this speaks to their wisdom? ✓
- Would a 25-year-old Tamil professional feel this is relevant to their life? ✓

### What to Avoid
- Starting paragraphs with "நாம் அனைவரும் அறிவோம்..." (cliché)
- Preachy endings that moralize too directly
- Long Sanskrit-heavy passages without translation
- Academic jargon without explanation
- Mixing Tamil script with English words unnecessarily

---

## PART 11: WHAT GOWRI WILL PROVIDE AND WHAT YOU MUST DO

### Gowri Provides → You Convert to HTML
| What She Provides | What You Must Do |
|-------------------|-----------------|
| Markdown files (`.md`) | Convert to HTML components |
| Plain Tamil text | Wrap in correct CSS classes |
| Classical verse references | Format in `.slim-quote` blocks |
| Section order for new issue | Build TOC + page structure |
| Corrections/edits | Apply to specific sections by page number |
| New cover image filename | Update `cover-image` src on cover page |

### Content Conversion Rules
When converting markdown to HTML:
- `## Heading` → `<div class="subhead">Heading</div>`
- `**Bold text**` → `<strong>text</strong>` (use sparingly)
- `> Block quote` → `<div class="slim-quote">` structure
- `- List items` → `<ul>` inside `.highlights-box` if grouped, or `<ol class="numbered-list">` for steps
- Standard paragraphs → `<p>text</p>` inside `.body-text`
- Blank line between paragraphs → new `<p>` tag (no `<br>` for paragraph breaks)

### Never Do This
- Never alter the CSS `<style>` block without explicit instruction from Gowri
- Never remove the print media query
- Never change color values from the brand palette
- Never use inline styles for colors (use CSS classes)
- Never rename or move the image asset files
- Never use English headings or labels in Tamil content sections

---

## PART 12: FILE MANAGEMENT CONVENTIONS

### Naming Convention
```
VAN_Vallaroli_[TamilMonth][Year]_v[Major].[Minor]_[YYYYMMDD].html

Examples:
VAN_Vallaroli_Chittirai2026_v1_1_20260307.html  ← Issue 1 (current, v1.1)
VAN_Vallaroli_Vaigasi2026_v1_0_[YYYYMMDD].html  ← Issue 2 (next)
```

### Version Numbering
- `v1.0` = First draft of new issue
- `v1.1` = Minor corrections after first review
- `v2.0` = Major structural changes (new sections, layout overhaul)

### Tamil Month Reference
| Tamil Month | Approx English | Tamil Script |
|-------------|----------------|--------------|
| சித்திரை | Apr–May | சித்திரை |
| வைகாசி | May–Jun | வைகாசி |
| ஆனி | Jun–Jul | ஆனி |
| ஆடி | Jul–Aug | ஆடி |
| ஆவணி | Aug–Sep | ஆவணி |
| புரட்டாசி | Sep–Oct | புரட்டாசி |
| ஐப்பசி | Oct–Nov | ஐப்பசி |
| கார்த்திகை | Nov–Dec | கார்த்திகை |
| மார்கழி | Dec–Jan | மார்கழி |
| தை | Jan–Feb | தை |
| மாசி | Feb–Mar | மாசி |
| பங்குனி | Mar–Apr | பங்குனி |

---

## PART 13: KNOWN ISSUES IN CURRENT FILE (Issue 1) — OPEN ITEMS

1. **`comparison-table` CSS** is defined but not consistently applied across all pages — verify all data tables use this class before Issue 2 production begins
2. **TOC page numbers** should be re-verified against actual page positions any time content sections are added, removed, or reordered

> ✅ **Resolved:** Filename/metadata inconsistency (ஐப்பசி vs சித்திரை) — fully corrected in `v1_1_20260307`. Issue 1 is officially **சித்திரை 2026**. Issue 2 is **வைகாசி 2026**.

---

## PART 14: QUICK REFERENCE — TAMIL MONTH ISSUE ROTATION

Each issue has rotating topic themes for the recurring sections. Track what was used to avoid repetition:

| Section | Issue 1 (சித்திரை 2026) | Issue 2 (வைகாசி 2026) |
|---------|--------------------------|------------------------|
| திருக்குறள் ஆய்வு | கல்வி அதிகாரம் | நட்பு அதிகாரம் |
| சங்க இலக்கியம் | தாமரை (Lotus) | பறவைகள் (Birds) |
| கோயில் கட்டமைப்பு | Overview/Introduction | மதுரை மீனாட்சி — இசைத் தூண்கள் |
| நலவாழ்வு | பாலில்லா புரதம் + கால்சியம் | நீரிழிவு நோய் + இயற்கை உணவு |
| மனம் தொடர் | Not started (teaser only) | மனதின் இயல்பு (Part 1) |

---

## PART 15: CONTACT & VAN DETAILS (Use These Consistently)

```
அமைப்பு: பெண்ணாடம் வள்ளலார் அறநிலையம் (VAN)
தலைவர்: மு. முத்துஜோதி
இணையதளம்: www.vallalar.org
மின்னஞ்சல்: vallalararanilayampdm@gmail.com
```

These appear on the closing/contact page. Never change without Gowri's explicit instruction.

---

## START OF SESSION CHECKLIST

At the beginning of every Claude Code session on this project:

1. **Read this CLAUDE.md fully** before making any changes
2. **Identify the specific task:** maintenance of current issue, or building new issue?
3. **Check the file version** in the filename before editing
4. **Clarify scope** before touching the CSS block
5. **Output the updated file** with version number incremented in filename

---

*நன்றி! Together we illuminate minds with வான் வளரொளி. 🪷✨*
*CLAUDE.md — Synced from Claude.ai project — சித்திரை 2026*
