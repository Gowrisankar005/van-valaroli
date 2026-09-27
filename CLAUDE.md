# CLAUDE.md — வான் வளரொளி இதழ் Production System
## Instructions for Claude Code

> **Project:** வான் வளரொளி இதழ் (Van Vallaroli Magazine)
> **Publisher:** பெண்ணாடம் வள்ளலார் அறநிலையம் (VAN — Vallalar Aranilayam)
> **Claude Code's role:** Maintainer and builder of the magazine's HTML/PDF output
> **Cadence:** Bi-monthly since Issue 02 (ஆடி 2026)

---

## PART 0: BEHAVIORAL GUIDELINES

Adapted from [andrej-karpathy-skills](https://github.com/multica-ai/andrej-karpathy-skills) — merge with the project-specific rules below. These bias toward caution over speed; use judgment on trivial edits.

### 1. Think Before Coding
Don't assume. Don't hide confusion. Surface tradeoffs.
- State assumptions explicitly (e.g. "which issue folder", "which pipeline version"). If uncertain, ask.
- If multiple interpretations exist, present them — don't pick silently.
- If something is unclear (a section mapping, a stale file, an ambiguous instruction), stop and name what's confusing.

### 2. Simplicity First
Minimum change that solves the problem. Nothing speculative.
- No new CSS components, pipeline steps, or abstractions beyond what's asked.
- No "flexibility" that wasn't requested (e.g. don't add a new theme or section type unless asked).
- No error handling for scenarios the pipeline can't hit.

### 3. Surgical Changes
Touch only what you must. Clean up only your own mess.
- Don't "improve" adjacent CSS, templates, or scripts while doing a content edit.
- Match existing style in `magazine-toolkit/*.py` and `templates/*.html`, even if you'd do it differently.
- If you notice unrelated dead/stale content (old drafts, orphaned issue folders), mention it — don't delete it without asking.
- Every changed line should trace to the user's actual request.

### 4. Goal-Driven Execution
Define success criteria; loop until verified.
- "Fix the PDF cut-off" → find the page, reproduce visually (screenshot/PDF page), then confirm it's gone.
- "Add a section" → build with `make_magazine.py`, open the PDF, check the Phase 5 checklist below.
- For multi-step work (new issue, pipeline change), state a brief plan with checkpoints before starting.

---

## PART 1: TWO SYSTEMS IN THIS REPO — READ THIS FIRST

This repo contains **two generations** of the same magazine. Know which one you're touching.

### A. Legacy monolithic HTML (Issue 01, சித்திரை/வைகாசி 2026) — FROZEN
Root-level files like `VAN_Vallaroli_Chittirai2026_v4_6_20260512.html` are single self-contained HTML documents: CSS, layout, and content all embedded together, built by hand/iteratively (v1.0 → v4.6+). This is how Issue 01 shipped.
- Governed by `Reference_docs/validate_template.py` (structural + brand-color validator).
- Enforced by `.git/hooks/pre-commit` (blocks commit on FAIL) and `.github/workflows/validate.yml` (CI).
- **Treat these root `.html` files as historical artifacts.** Only edit one if Gowri explicitly asks for a correction to a shipped/in-flight issue built this way. Don't use this as the template for new issues.
- Full structural reference (page anatomy, CSS class table, section registry) is preserved in **PART 2 below** since the design system it encodes is still the single source of truth for visual style.

### B. magazine-toolkit/ — ACTIVE, use this for all new issues
`magazine-toolkit/` is a self-contained build system: **author markdown (MMD) → templated HTML → auto-paginated PDF.** This is what Issue 02 (ஆடி 2026) onward uses. (Renamed from `HowTO/` — same system, clearer name.)

```
magazine-toolkit/
├── GETTING_STARTED.md        ← one-time machine setup + smoke test
├── setup.sh                  ← bash installer (venv, deps, Playwright Chromium)
├── make_magazine.py          ← ONE-COMMAND ENTRY POINT
├── build_issue_html.py       ← Step 0 — MMD → base HTML (uses mmd_parser.py)
├── validate_mmd.py           ← Pre-flight lint for author articles
├── fix_html.py               ← Step 1 — image paths, CSS injection, layout fixes
├── rebalance_sections.py     ← Step 2 — Playwright-measured pagination + TOC
├── compare_html.py           ← Step 3 — integrity audit (order/content/images preserved)
├── build_text_pdf.py         ← Step 4 — Playwright → searchable text-PDF (default)
├── build_screenshot_pdf.py   ←   (fallback — image-based PDF)
├── templates/                ← _base.html, cover.html, toc.html, article_page.html,
│                                masthead.html, imprint.html, magazine.css (~1540 lines)
│   └── assets/               ← the only 2 truly-shared static files (van-logo.jpg,
│                                vallaroli-logo.jpg) — everything else is per-issue
├── docs/                     ← Author_Guide.docx, Editor_Guide.docx,
│                                MMD_Specification.md, Architecture.md
├── issues/
│   ├── _starter-template/    ← copy this to start a new issue (has its own README)
│   ├── Issue-NN/              ← the currently active issue being built
│   │   └── _drafts/          ← gitignored raw-submission staging (docx → pandoc →
│   │                            hand-cleaned into articles/*.md — see PRODUCTION_WORKFLOW.md)
│   └── released/              ← completed, shipped issues (full recipe + final/ output)
├── source/                   ← build scratch, fully gitignored — regenerated per build,
│                                nothing here is durable (durable copy lives in
│                                issues/released/Issue-NN/final/)
└── output/                   ← final PDFs before manual promotion to issues/released/
```

**One command builds an entire issue:**
```bash
cd magazine-toolkit && source .venv/bin/activate
python make_magazine.py --from-issue issues/Issue-02 output/VAN_Vallaroli_Aadi2026.pdf
```

- `magazine-toolkit/templates/*.html` are page **fragments**, not full documents (no `<style>` block, no full class set — they're assembled at build time). The pre-commit hook explicitly skips them; don't expect them to pass `validate_template.py`.
- Full technical deep-dive: `magazine-toolkit/docs/Architecture.md`. Full per-issue checklist: `magazine-toolkit/PRODUCTION_WORKFLOW.md`.
- Author-facing content format is **MMD (Magazine Markdown)** — see PART 2A below. Authors never touch HTML or CSS.

**When Gowri says "build the issue" / "make the PDF" / gives you a new issue's content → use System B.**
**When Gowri says "fix Issue 01" / references a specific `.html` filename at the repo root → use System A, and be extra careful (Lessons Learned in PART 9 apply directly).**

---

## PART 2: LEGACY SYSTEM (A) — HTML PAGE ANATOMY

### Every Content Page
```html
<div class="page">
  <div class="glossy"></div>
  <span class="corner-tl">❈</span>
  <span class="corner-br">❈</span>

  <div class="page-header">
    <span class="section-name">[SECTION NAME IN TAMIL]</span>
    <span class="mag-name">வான் வளரொளி இதழ்</span>
  </div>

  <div class="content-area">
    <!-- First page of a section: -->
    <div class="section-header">
      <div class="topic-title">[ARTICLE TITLE]</div>
      <div class="section-label-row">
        <span class="lotus-icon">❀</span>
        <span class="section-label">[SECTION LABEL]</span>
        <span class="lotus-icon">❀</span>
      </div>
      <div class="title-underline"></div>
    </div>
    <!-- Page 2+ of same section, instead: -->
    <div class="continuation-banner">
      <span class="cont-section-name">[SECTION NAME]</span>
      <span class="cont-page-info">தொடர்ச்சி — பகுதி [X/Y]</span>
    </div>

    <div class="section-divider">&#x2022; &nbsp;&nbsp; &#x2022; &nbsp;&nbsp; &#x2022;</div>
    <div class="body-text"><!-- content components below --></div>
  </div>

  <div class="page-footer">
    <span class="issue-info">இதழ் எண்: [N] &nbsp;|&nbsp; [Tamil Month] [Year]</span>
    <span class="page-number">[PAGE NUMBER]</span>
    <img class="van-logo-footer" src="VANLogoGold.jpg" alt="VAN">
  </div>
</div>
```

### Content Components (CSS classes to use)

| Component | HTML | When to use |
|-----------|------|-------------|
| Body paragraph | `<p>text</p>` | All running text |
| Lead paragraph | `<p class="lead-para">text</p>` | Opening paragraph of each article only |
| Subheading | `<div class="subhead">text</div>` | Section sub-topics |
| Classical quote | `<div class="slim-quote"><div class="quote-text">verse</div><div class="quote-source">source</div></div>` | Thirukkural, Sangam verses |
| Highlights box | `<div class="highlights-box"><div class="box-title">title</div><ul><li>item</li></ul></div>` | Key points, lists |
| Numbered list | `<ol class="numbered-list"><li>item</li></ol>` | Step-by-step instructions |
| Author byline | `<div class="author-byline">text</div>` | Article attribution |
| Section divider | `<div class="section-divider">• &nbsp; • &nbsp; •</div>` | Between sub-sections |
| Image — float right | `<figure class="article-figure img-right"><img src="..." alt="[Tamil]"><figcaption class="img-caption">[Tamil]</figcaption></figure>` | Portraits, illustrations (62mm, text wraps left) |
| Image — float left | same with `.img-left` | Same, text wraps right |
| Image — full banner | `.img-banner` | Temple exteriors, landscapes (full width, 75mm cover crop) |
| Image — full width, natural height | `.img-banner.img-banner-full` | Same width as a banner; height follows the photo. For a picture that is not a wide panorama |
| Image — half centered | `.img-half` | Diagrams, single objects (100mm centered) |

**Image size guide:** float 62mm (min 370×280px, ideal 730×550px) · banner 182mm (min 1080×400px, ideal 2150×790px) · half 100mm (min 590×440px, ideal 1180×870px).
Never place a float immediately after another float — use a `section-divider` between them.

### Section Registry (extended menu — up to 21 types; an issue typically uses 10)

| # | Tamil Name | Page-Header Label | Typical Pages |
|---|---|---|---|
| 1 | தலையங்கம் | தலையங்கம் | 1–2 |
| 2 | கருணைச் சோலைக் கட்டுரை | கருணைச் சோலை | 2–3 |
| 3 | திருக்குறள் ஆய்வு | திருக்குறள் ஆய்வு | 4–5 |
| 4 | சங்க இலக்கியத் தொடர் | சங்க இலக்கியம் | 5–6 |
| 5 | மாணவர் கல்வி வெற்றித் தொடர் | மாணவர் வெற்றி | 1–2 |
| 6 | நலவாழ்வு / அறிவியல் | நலவாழ்வு | 1 |
| 7 | வீட்டுப்பெண்களுக்கு | வீட்டுப்பெண்களுக்கு | 1–2 |
| 8 | அறநிலைய செய்திகள் | அறநிலையச் செய்திகள் | 2–3 |
| 9 | தமிழகக் கோயில் கட்டமைப்பு / தமிழகக் கலைகள் | கோயில் கட்டமைப்பு | 5–7 |
| 10 | கல்வெட்டில் அறச் செய்திகள் | கல்வெட்டு ஆய்வு | 1 |
| 11 | தமிழிசை வரலாறு | தமிழிசை | 1 |
| 12 | தமிழர் வாழ்வியல் | தமிழர் வாழ்வியல் | 1 |
| 13 | நூல் மதிப்புரை | நூல் மதிப்புரை | 2–3 |
| 14 | தமிழ் எழுத்துக்களின் வரலாறு | தமிழ் எழுத்து வரலாறு | 1 |
| 15 | அருளாளர்களின் அறம் | அருளாளர்கள் | 1 |
| 16 | நற்றமிழ் சொற்கள் அறிவோம் | நற்றமிழ் சொற்கள் | 0.5 |
| 17 | கவிதைகள் | கவிதைகள் | 1 |
| 18 | சிறுகதை | சிறுகதை | 3–4 |
| 19 | ஒரு ஒழுக்கம் | ஒரு ஒழுக்கம் | 3–4 |
| 20 | இயற்கை உணவு / இயற்கை தரும் இன்பம் | இயற்கை உணவு | 0.5–1 |
| 21 | விவாதம்: இரு பார்வை | விவாதம் | 1–2 |
| — | மனம் தொடர் (new, from Issue 02) | மனம் தொடர் | 2 |
| — | அடுத்த இதழில் (always last) | — | 1 |

**Fixed structure, both systems:** cover → TOC/imprint/masthead → content sections in editorial order → அடுத்த இதழில் / closing page (always last).

---

## PART 2A: MMD AUTHORING FORMAT (System B — how content becomes HTML)

Full spec: `magazine-toolkit/docs/MMD_Specification.md`. One `.md` file per article, saved to `issues/Issue-NN/articles/`.

```markdown
---
section: திருக்குறள் ஆய்வு
title: நட்பு — ஓர் ஆய்வு
subtitle: திருவள்ளுவர் காட்டும் நட்பின் இலக்கணம்
author: திருமுருகன்
---

முதல் பத்தி (இது தானாக lead-para ஆகும்).

## முன்னுரை

இரண்டாம் பத்தி.

:::quote source="திருக்குறள் 781"
செயற்கரிய யாவுள நட்பின் அதுபோல
வினைக்கரிய யாவுள காப்பு.
:::

:::box title="இந்த இதழில்..."
- திருக்குறள் ஆய்வு
- சங்க இலக்கியம்
:::

:::image src="lotus-01.jpg" caption="கோயில் குளத்தில் தாமரை" type="float"
:::

:::closing
நாம் மேலும் வளர்வோம்.
— திருமுருகன்
:::
```

| Directive | Maps to | Notes |
|---|---|---|
| `## Heading` through `###### Heading` | `.subhead` | 2–6 per article typical; all levels render identically (one visual style) — use deeper levels only to signal nesting in source |
| `**bold**` | `<strong>` | Inline only, works in paragraphs/list items/box items; no other inline emphasis supported |
| `- item` | `<ul>` list | |
| `1. item` | `<ol class="numbered-list">` | Exact `N. ` prefix required |
| `:::quote source="..."` | `.slim-quote` | Each non-blank line → its own verse line |
| `:::box title="..."` | `.highlights-box` | Bulleted items inside |
| `:::image src="..." caption="..." type="float\|float-left\|banner\|banner-full\|half\|portrait"` | `.article-figure img-*` | `float`=60×45mm right, `float-left`=same but left (alternate with `float` — never stack two same-side floats back to back), `banner`=full-width with a 75mm cover crop, `banner-full`=full width at the photo's own height (no crop; use when the picture is not a wide panorama), `half`=80mm centered no border (diagrams/artifacts), `portrait`=45mm centered no border (author/subject headshot, use this NOT `half` for portraits). `src` must exist in issue's `images/` folder |
| `:::closing` | sign-off block | Heuristic: prose lines ending in `./!/?` stay plain text; the first line that ISN'T a full sentence starts the signature (sign-off → name → title → org) — no `—` marker required, though one still works |

**Rules:** Tamil only (செந்தமிழ் substitutions apply — PART 4), em-dash `—` (U+2014) for citations never `--`/`----`, no manual page breaks (pagination is automatic via `rebalance_sections.py`, which now includes a real-rendered-gap backfill pass — see PART 9), no raw HTML, `section:` frontmatter must exactly match a `section_name` in `issue_meta.json`.

Before handing an issue to the pipeline, run:
```bash
python magazine-toolkit/validate_mmd.py issues/Issue-NN/articles/*.md
```

---

## PART 3: DESIGN SYSTEM — DO NOT ALTER WITHOUT EXPLICIT INSTRUCTION

### Brand Colors (CSS custom properties — see PART 3A)
```
--van-primary / --van-green-mid:  #8DC63F   accent, subheadings
--van-deep / --van-green-deep:    #2d7a3e   page header text, page numbers
--van-dark / --van-green-dark:    #6BA82F   highlights-box border, section labels
--van-gold:                       #D4AF37   decorative elements, pull-quote lines
--body-text:                      #2B2B2B   all body paragraphs
--subtle-text:                    #666666   sign titles, org names
--page-bg-top / --page-bg-bottom: #fffef5 / #fef9f2
```

### Typography
- Font: Noto Sans Tamil (Google Fonts), loaded via `<link>` in `<head>`
- Body text: 12–13pt (11pt minimum — senior accessibility requirement), line-height 1.5, `#2B2B2B`, justified
- Subheadings: 13–14pt bold, `#8DC63F` with left-bar accent
- Classical quotes: centered, 13–14pt, inside `.slim-quote`
- Page header section name: gold `#D4AF37`. Page number: deep green `#2d7a3e`

### Page Dimensions
- A4 = 210mm × 297mm. Content padding 14mm left/right, 5mm top (below header), 3mm bottom
- Every page: `.glossy` overlay + `corner-tl`/`corner-br` ❈ motifs (color `#8b6f47`, ~9% opacity)

### Print Media Query (always preserve)
```css
@media print {
  body { background: none; padding: 0; margin: 0; }
  .page { box-shadow: none; border-radius: 0; margin: 0; page-break-after: always; break-after: page; }
  .glossy { display: none; }
}
@page { size: A4 portrait; margin: 0; }
```

### Required Image Assets
```
VANLogoGold.jpg          — footer logo, every page
valarolilogogold01.jpg   — larger logo on cover
MagazineCoverImage01.jpg — cover background photo
```
If missing/renamed, every footer and the cover break.

---

## PART 3A: THEME SYSTEM — CSS CUSTOM PROPERTIES

```css
:root {
  --van-primary:   #8DC63F;
  --van-deep:      #2d7a3e;
  --van-dark:      #6BA82F;
  --van-gold:      #D4AF37;
  --van-deepest:   #0a2616;   /* masthead gradient */
  --van-deeper:    #0d3320;
  --van-brown:     #8b6f47;   /* corner motifs */
  --van-bg-light:          #f4fbe8;
  --van-bg-gradient-start: #f0f7e6;
  --van-bg-gradient-end:   #e8f5d0;
  --van-text-on-dark:      #fff8e8;
  --page-bg-top:           #fffef5;
  --page-bg-bottom:        #fef9f2;
}
/* + [data-theme="peacock/blue/terracotta/saffron"] override blocks */
```
System B supports building all 5 themes: `python make_magazine.py --from-issue issues/Issue-NN out.pdf --theme <name>`.

**DO:** use `var(--van-primary)` etc. in any new CSS — never hardcode hex values.
**NEVER:** run a global string/regex replacement across the *entire* CSS block including `:root {}` and `[data-theme]` blocks — see Lesson 1 in PART 9. Only replace within the rules body, never inside variable definitions.

---

## PART 4: செந்தமிழ் STANDARDS — MANDATORY SUBSTITUTIONS

Applies when converting any content (both systems) to output. Non-negotiable.

| Category | ❌ Avoid | ✅ Use |
|---|---|---|
| Technology | கம்ப்யூட்டர் / லேப்டாப் / மொபைல் / இன்டர்நெட் / இ-மெயில் / வெப்சைட் | கணினி / மடிக்கணினி / கைப்பேசி / இணையம் / மின்னஞ்சல் / இணையதளம் |
| Education | ஸ்கூல் / காலேஜ் / டீச்சர் / ஸ்டூடென்ட் / கிளாஸ் ரூம் | பள்ளி / கல்லூரி / ஆசிரியர்(ஆசிரியை) / மாணவர்(மாணவி) / வகுப்பறை |
| Healthcare | ஹாஸ்பிடல் / டாக்டர் / நர்ஸ் / மெடிசின் / ஆப்பரேஷன் | மருத்துவமனை / மருத்துவர் / செவிலியர் / மருந்து / அறுவை சிகிச்சை |
| Sanskrit loans | தர்மம் / புண்ணியம் / சுத்தம் / ஆரோக்கியம் | அறம் / நன்மை / தூய்மை / நலம்(நலனுடைமை) |
| Transport | பஸ் / டிரெய்ன் / ரோடு / ஏர்போர்ட் | பேருந்து / தொடர்வண்டி / சாலை / விமான நிலையம் |

`ஞானம்` is acceptable; prefer `அறிவொளி` in headers.

**Exception — reprinted classic texts** (e.g. the Pudhumaipithan சிறுகதை series): keep the author's original words, including loan words (நர்ஸ், டாக்டர், ஆஸ்பத்திரி…). Do not "fix" them; `validate_mmd.py` will still print loan-word warnings for these files — that is expected. The செந்தமிழ் substitutions apply to new writing by VAN authors.

---

## PART 5: VAN VOICE — EDITORIAL STYLE

Every article should sound like a wise, warm, learned elder — not a textbook, not a blog.

**Three pillars:** சுஜாதா's clarity (simple, concrete examples) + பாவண்ணன்'s grounding (reverence for classical texts) + சிற்பி's compassion (warm, socially conscious, emotionally honest).

**Intergenerational test:** would a 65-year-old வள்ளலார் devotee feel this speaks to their wisdom, AND would a 25-year-old Tamil professional feel it's relevant to their life?

**Avoid:** opening with "நாம் அனைவரும் அறிவோம்..." · preachy/moralizing endings · long untranslated Sanskrit-heavy passages · academic jargon · unnecessary English-Tamil script mixing.

---

## PART 6: ISSUE METADATA & FILE NAMING

### Fields to update every issue (both systems)
| Field | System A location | System B location |
|---|---|---|
| Issue number | every footer `.issue-info` | `issue_meta.json → issue_number` |
| Tamil month + year | footers + cover masthead | `issue_meta.json → tamil_month, year, year_tamil` |
| Special issue label | cover `.pill-special` | `issue_meta.json → special_label` |
| Next issue preview | last content page | `issue_meta.json → next_issue` |
| `<title>` tag | `<head>` | generated by `build_issue_html.py` |
| Masthead/editor names | contact page | `issue_meta.json → masthead.roles` |

### Tamil Numerals & Months
```
௧=1 ௨=2 ௩=3 ௪=4 ௫=5 ௬=6 ௭=7 ௮=8 ௯=9 ௰=10   ௨௦௨௬ = 2026
சித்திரை(Apr–May) வைகாசி(May–Jun) ஆனி(Jun–Jul) ஆடி(Jul–Aug) ஆவணி(Aug–Sep)
புரட்டாசி(Sep–Oct) ஐப்பசி(Oct–Nov) கார்த்திகை(Nov–Dec) மார்கழி(Dec–Jan)
தை(Jan–Feb) மாசி(Feb–Mar) பங்குனி(Mar–Apr)
```

### Naming Convention
- System A: `VAN_Vallaroli_[TamilMonth][Year]_v[Major].[Minor]_[YYYYMMDD].html`
- System B: `magazine-toolkit/issues/Issue-NN/` (source) → `magazine-toolkit/output/VAN_Vallaroli_[TamilMonth][Year].pdf` (build output)
- Version bumps (System A only): `v1.0` first draft · `v1.1` minor corrections · `v2.0` structural changes

### Issue Rotation Tracker (avoid repeating topics)
| Section | Issue 1 (வைகாசி 2026) | Issue 2 (ஆடி 2026) | Issue 3 (புரட்டாசி 2026 — Oct 2026 release) |
|---|---|---|---|
| திருக்குறள் ஆய்வு | அறிவுடைமை — பத்துக் குறட்பாக்கள் | அறம் செய விரும்பு — பாரி · பேகன் (கடையெழு வள்ளல்கள்), குறள் 211 | ஆறுவது சினம் — நாவினால் சுட்ட வடு (குறள் 129, 305, 306) |
| சிறுகதை | பால்வண்ணம் பிள்ளை — புதுமைப்பித்தன் | திறந்த ஜன்னல் — புதுமைப்பித்தன் (மணிக்கொடி, 1934) | கட்டில் பேசுகிறது — புதுமைப்பித்தன் (மணிக்கொடி, 1934) |
| தமிழகக் கலைகள் | கோயிற் கட்டிடக்கலை — ஓர் அறிமுகம் | தமிழர் சிற்பக்கலையின் தொன்மை — கீழடி, ஆதிச்சநல்லூர், நடுகற்கள் | மரம் முதல் கற்றளி வரை (Issue 02 தொடர்ச்சி) |
| சங்க இலக்கியம் | தாமரை மலரின் அறச்செய்தி (Lotus) | மலர் சூடிய நாகரிகம் — சங்க இலக்கியத்தில் மலர்களின் பெருமையும் அறமும் | காந்தள் மலரின் அறம் — செங்காந்தள் (தமிழ்நாட்டின் மாநில மலர்) |
| ஓர் ஒழுக்கம் | அதிகாலை துயில் எழல் — வள்ளலாரின் நெறி | மல சலம் கழித்தல் — எருவாய்க்கான ஒழுக்கம் | தந்த சுத்தி — வழலை நீக்கல் |
| நூல் மதிப்புரை | வாசிப்பது எப்படி? — செல்வேந்திரன் | தமிழர் வீரம் — முனைவர் ரா.பி. சேதுப்பிள்ளை | (TBD) |
| மனம் தொடர் | Not started (teaser only) | மனதின் இயல்பு (Part 1) — shipped | மனம் எனும் ஏணி (Part 2) — series continues |
| இயற்கை தரும் இன்பம் | Not started | Photo essay — shipped (new section, added mid-issue) | (TBD) |

Note: சிறுகதை is an ongoing series of Pudhumaipithan's classic short stories (Issues 1–3) — accepted by Gowri, no reprint flag needed. Keep the classic text as written.

---

## PART 7: CONTACT & VAN DETAILS

```
அமைப்பு: பெண்ணாடம் வள்ளலார் அறநிலையம் (VAN)
தலைவர்: மு. முத்துஜோதி
இணையதளம்: www.vallalar.org
மின்னஞ்சல்: vallalararanilayampdm@gmail.com
```
Never change without Gowri's explicit instruction.

---

## PART 8: QUALITY GATES

### System A (root HTML files)
```bash
python3 Reference_docs/validate_template.py <file>.html   # 0 FAIL expected
python3 Reference_docs/validate_template.py --self-test   # if you touched the validator
python3 Reference_docs/validate_template.py --all
```
Enforced by `.git/hooks/pre-commit` (blocks on FAIL; skips `Archive/**` and `magazine-toolkit/templates/**`) and `.github/workflows/validate.yml` (CI on push/PR touching root `*.html`). **Never use `git commit --no-verify`.**

### System B (magazine-toolkit pipeline)
```bash
python magazine-toolkit/validate_mmd.py issues/Issue-NN/articles/*.md   # pre-flight lint
# compare_html.py runs automatically as pipeline Step 3 — integrity audit:
#   section order preserved, all paragraphs preserved, byline on each section's
#   first page, image count consistent with page delta
```
Then eyeball the PDF against the Phase 5 checklist in `magazine-toolkit/PRODUCTION_WORKFLOW.md` (cover, imprint, masthead, TOC, spot-check 3 articles, Cmd+F search works, file size 5–20MB).

---

## PART 9: LESSONS LEARNED — NEVER REPEAT THESE

Real production bugs. Read before touching CSS, `magazine.css`, or any script that does bulk text replacement in either system.

### ❌ Lesson 1 — Never run color replacement across the entire CSS block
A script replaced hex values throughout the whole `<style>` block, including inside `:root {}`. `--van-primary: #8DC63F` became `--van-primary: var(--van-primary)` — a circular self-reference. CSS silently falls back to `black`. Every font color turned black; the old validator missed it because it only checked variable *names*, not resolved values.
**Rule:** exclude `:root {}` and all `[data-theme]` blocks from any bulk replacement. Only touch the CSS rules body.

### ❌ Lesson 2 — Never restructure CSS via slice/cursor without verifying length
A fix script found the end of the last `[data-theme]` block by brace-counting and returned `CORRECT_ROOT + css[cut_point:]`. A logic error made the cut point wrong, silently deleting ~900 lines of CSS. Looked fine until length was checked.
**Rule:** after any CSS restructuring script, assert `after_lines >= before_lines - 10`.

### ❌ Lesson 3 — Spacing variations break targeted string replacement
An exact-string fix for `:root` (`'--van-gold:       var(--van-gold);'`, 7 spaces) missed the same circular ref in `[data-theme="blue"]` with 5 spaces.
**Rule:** after targeted CSS replacement, re-search with a flexible-whitespace regex (`r'--van-\w+:\s*var\(--van-\w+\)'`) and assert nothing remains.

### ❌ Lesson 4 — Validator gaps are silent
`check_brand_colors` and `check_theme_system` tested whether a variable *name* was present anywhere in the CSS — including as a circular definition. Both passed on broken CSS.
**Rule:** every check must test *semantic meaning*, not presence of a string. When adding a new check, write a self-test with bad input that should fail it — if the self-test passes, the check is incomplete.

### System B (magazine-toolkit pipeline) — Lessons Learned (found during Issue 02)

All fixed at the shared-script level, not patched per-page — that is the standing rule for this pipeline: a bug found on one issue's page must be fixed so it can't recur on any future issue, not worked around for the page it was found on.

### ❌ Lesson 5 — Never measure element heights via a `/tmp/` scratch file
`rebalance_sections.py`'s Playwright measurement step wrote its temp HTML to a hardcoded `/tmp/rebalance_measure.html`, breaking every relative `Images/...` src in it. Broken images render at fallback size, so every image's height was undercounted by 60-70% — the root cause of most "unexplained" blank space at page bottoms that session. It looked like a pagination bug for a long time before the actual cause (a path bug) was found.
**Rule:** any script that writes a temp copy of the HTML for Playwright measurement must write it *next to* the real source file (same directory), never to `/tmp` or any other directory — relative asset paths must still resolve. Clean up with `unlink(missing_ok=True)` after.

### ❌ Lesson 6 — `!important` in a stylesheet silently defeats inline-style safety nets
`build_text_pdf.py` had an auto-zoom-to-fit step: measure overflow, then set `element.style.maxHeight`/`.height` inline to shrink it. `magazine.css` had `!important` on those same properties, so the inline styles were silently ignored — the safety net looked wired up but never actually fired, and pages kept overflowing. No error, no warning — it just quietly did nothing.
**Rule:** when a script must override CSS from JS/Python-injected inline styles, use `element.style.setProperty(prop, val, 'important')`, never bare `element.style.prop = val`, whenever there's any chance the stylesheet also sets that property with `!important`.

### ❌ Lesson 7 — `display:block` silently breaks flex-dependent layouts
A print-CSS override forced `.page, .cover { display: block !important }` for print pagination. But the footer's "stick to page bottom" positioning depended on the page being a flex column. Forcing `block` looked harmless (block is the "normal" default) but silently broke footer placement — footers floated up next to content instead of pinning to the bottom.
**Rule:** when a print/measurement override touches `display`, check what layout mode (flex/grid) the element's children depend on first — don't assume `block` is a safe default.

### ❌ Lesson 8 — A 20%-overfill-and-shrink tolerance hides real pagination bugs
`adjust_page_count()` tolerated sections up to 20% over their page-capacity estimate, relying on `build_text_pdf.py`'s per-page zoom to visually compress the overflow. This is what produced "small font + big empty margin" pages — zoom shrank dense pages fine, but on pages where the *measurement* was itself wrong (see Lesson 5), the zoom had nothing to compress and the tail end just sat blank.
**Rule:** tolerance was tightened to 3% — prefer adding a page over shrinking text. A page-count/pagination algorithm should not lean on a downstream visual hack to paper over its own estimation error.

### ❌ Lesson 9 — Subhead-adjacency edge case in logical-unit splitting
`split_logical_units()` glued a subhead to the content immediately following it (so a heading never lands alone at a page bottom) — but didn't check whether that "following content" was *itself* another subhead (e.g. `##` immediately followed by `###`), so nested headings got mis-glued together as one unit, sometimes stranding the deeper heading anyway.
**Rule:** any "glue heading to next unit" logic needs a second pass that also merges any unit which turns out to be *entirely* headings/dividers (no real content) forward into the next unit — checking adjacency once, at construction time, isn't enough.

### ❌ Lesson 10 — A page-layout function that assumes one page shape breaks on others
`reorganize_activities_page()` (the "group all photos into a 2-col grid" fixup) originally grouped **every** image on the page into a single grid regardless of position, which scrambled multi-subsection pages where images were meant to stay next to their own paragraph. Fixed to only group images that are *immediately consecutive* in document order. The fixed-crop `object-fit:cover` grid it used was also unsafe to reuse for content with wildly different aspect ratios (a 0.54 vs 1.24 ratio pair badly cropped) — a separate `.image-pair-row` class using `object-fit:contain` with a height cap (no cropping) was added instead of forcing everything through the same grid.
**Rule:** a DOM-restructuring fixup written for one page's shape will silently misfire on a differently-shaped page using the same section type. Scope the match condition (e.g. "consecutive same-type figures") narrowly, and don't reuse a fixed-crop grid for photos whose aspect ratios you don't control.

### ❌ Lesson 11 — Screen-media measurement can diverge from print-media render
Playwright measured page heights with the browser in default (screen) media, but `page.pdf()` renders in `print` media — if any `@media print` CSS rule changes layout (and one did, see Lesson 7), the measured heights don't match what actually gets printed.
**Rule:** call `page.emulate_media(media='print')` immediately after `page.goto()`, before any measurement, whenever the same Playwright page is later used to produce the PDF.

### ❌ Lesson 12 — A line ending in ":" can be stranded from the list or quote it introduces
`split_logical_units()` treated every paragraph as its own unit, so an intro line like "பல்லவர்களின் காலத்தில்:" could sit at the bottom of one page while its numbered list started on the next. Separately, the backfill pass refused to pull content off a section's *last* page (its "net-improvement" guard), although blank space at the end of an article is natural — so a page-bottom gap stayed even when a short paragraph would have fit.
**Rule:** a paragraph ending in `:` is glued to the element right after it; backfill may pull content from a last page as long as that page stays reasonably filled (`LAST_PAGE_MAX_GAP_PX`). Content-side tip: photo pairs and lists are unbreakable blocks — to close a gap before one, move a nearby paragraph above it or use `float`/`float-left` photos so they sit beside text.
**Side effect:** rebuilding an already-released issue keeps its text identical (`compare_html.py` clean) but pagination can shift slightly. `issues/released/Issue-NN/final/` is the authoritative record of what shipped.

### ℹ️ Note — WeasyPrint was evaluated and rejected for PDF generation
When asked to switch the PDF step to WeasyPrint, we recommended staying on the Playwright-based `build_text_pdf.py` instead: WeasyPrint substitutes fonts it can't find (risk of breaking Tamil glyph rendering) and computes `height:auto` layout independently of the Playwright-measured HTML the rebalance step already tuned, reopening every pagination bug this section describes. Playwright renders with the same Chromium engine used for measurement, so what was measured is what gets printed.

---

## SESSION CHECKLIST

1. Identify which system you're in (PART 1) before editing anything.
2. If System A: run `validate_template.py --self-test`, then the target file, to establish baseline.
3. If System B: check `issue_meta.json` matches the plan doc, run `validate_mmd.py` on touched articles.
4. Make the change — surgically (PART 0.3).
5. Re-validate (System A) or rebuild + spot-check PDF (System B) before reporting done. System B: run the full pipeline through `build_text_pdf.py`, then `compare_html.py` as an integrity check — don't call a build final on `rebalance_sections.py` output alone. If a page still looks underfilled after `rebalance_sections.py`'s `[3/5] Backfilled N element(s)` line ran, check whether it's genuinely a bug or just the natural end of a section/article.
6. Commit only when asked; never `--no-verify`.
7. If you hit a new bug worth remembering, add it to PART 9 — don't let it repeat.

---

## CLAUDE.md MAINTENANCE TRIGGERS

Update this file when the change affects *future Claude Code behavior* — design rules, quality gates, hard-won lessons, component/MMD patterns. Do **not** update it for one-off content edits, single-issue fixes, or temporary workarounds — those belong in issue-specific plan doc inside `issues/released/Issue-NN/`, `Reference_docs/content_tracker.md`, or commit messages.

| What changed | Update here |
|---|---|
| New MMD directive or component | PART 2A table |
| New CSS component/class | PART 2 components table |
| Brand color added/renamed | PARTs 3 & 3A |
| New theme added | PART 3A |
| New section type | PART 2 section registry |
| New bug found and fixed | PART 9 |
| Pipeline step added/changed in `magazine-toolkit/` | PART 1B + `magazine-toolkit/docs/Architecture.md` |
| New issue started | PART 6 rotation tracker |
| VAN contact details change | PART 7 |

*நன்றி! Together we illuminate minds with வான் வளரொளி. ❀✨*
