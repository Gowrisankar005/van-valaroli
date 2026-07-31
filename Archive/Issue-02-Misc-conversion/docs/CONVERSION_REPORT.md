# Issue-02 Word → MMD conversion report

Date: 2026-07-26  
Source folder: `HowTO/issues/Issue-02/articles/`  
Output: `.md` articles + images under `images/`

## Source inventory

| Source file | Type | Unique? | Converted to |
|---|---|---|---|
| `02-thirukkural.docx` | Word | yes | `articles/02-thirukkural.md` |
| `03-sirukathai.docx` | Word | **NO — byte-identical to 05-kalai.docx** | `articles/03-sirukathai.md` (same body as 05) |
| `05-kalai.docx` | Word | yes (same as 03) | `articles/05-kalai.md` |
| `07-ozhukkam.docx` | Word | yes | `articles/07-ozhukkam.md` |
| `09-activities` (no extension) | Word | yes | `articles/09-activities.md` + `09-activities.docx` copy |

## Content vs `issue_meta.json` (labeling issues — content not rewritten)

| File | Planned section / topic | Actual document title / topic |
|---|---|---|
| `02-thirukkural` | திருக்குறள் ஆய்வு — நட்பு அதிகாரம் | **ஆறுவது சினம்** (ஔவையார் story + குறள் 129/305/306 comparison) |
| `03-sirukathai` | சிறுகதை | **Same as 05-kalai** (not a short story) |
| `05-kalai` | தமிழகக் கலைகள் — மதுரை மீனாட்சி இசைத் தூண்கள் | **தமிழர் சிற்பக்கலையின் தொன்மை** (கீழடி / ஆதிச்சநல்லூர் / நடுகற்கள்) |
| `07-ozhukkam` | ஓர் ஒழுக்கம் | **மல சலம் கழித்தல்** (matches series) |
| `09-activities` | அறநிலையச் செய்திகள் | **அறநிலைய நிகழ்வுகள்** (May–Jun 2026) |

**Action needed from editor:** replace the mislabeled/wrong-topic sources when the real சிறுகதை and நட்பு-அதிகாரம் drafts arrive. `03` currently has no independent content.

## What was preserved (no editorial rewrite)

- All body paragraphs, bullet lists, and verse lines from the Word sources
- Source typos kept as-is (e.g. `ஒஒவ்வொன்றாகப்`, `The Hindu an Times of India`, `U-tube`, `zoom`)
- English loan words and mixed script left unchanged (conversion only, not senthamizh edit)
- Quote blocks mapped to `:::quote` (source citation in attribute when present)
- Headings mapped to `##` / `###`
- Images mapped to `:::image` with captions from Word alt text when available

## Structural MMD mapping (not content change)

| Word | MMD |
|---|---|
| Document title | YAML `title` (+ first body line when it was repeated) |
| Bold section labels | `##` subheads |
| Block verses | `:::quote source="…"` |
| Embedded pictures | `:::image src="…" caption="…" type="…"` |
| Decorative `────` lines | omitted (layout only) |
| Highlight/mark runs | plain text (MMD has no highlight) |

## Images extracted → `images/`

### From 02 (story illustrations; same PNG reused 4× in Word)

| File | Notes |
|---|---|
| `02-aruvathu-sinam-nails.png` | fence/nails scene (unique media image1) |
| `02-aruvathu-sinam-scars.png` | scars/lesson scene (unique media image2) |

### From 05 / 03 (sculpture article)

| File | Caption / subject |
|---|---|
| `05-keezhadi-terracotta-01.jpeg` | கீழடியில் கிடைத்த சுடுமண் சிற்பம் |
| `05-adichanallur-mother-goddess-02.jpeg` | Mother Goddess, Adichanallur / Egmore |
| `05-adichanallur-figurine-03.jpeg` | (no Tamil caption in source) |
| `05-adichanallur-excavation-04.jpeg` | ஆதிச்சநல்லூர் - அகழாய்வு |
| `05-indus-valley-figurine-05.jpeg` | சிந்துவெளி நாகரீகம் |
| `05-pulimankombai-nadukal-06.jpeg` | புலிமான்கோம்பை நடுகற்கள் |

### From 09 (events)

| File | Subject |
|---|---|
| `09-header-logo-01.jpeg` | small header logo |
| `09-header-logo-02.jpeg` | small header logo |
| `09-homoeopathy-camp-01.jpeg` / `-02.jpeg` | free homeopathy camp |
| `09-poosam-lamplit-01.jpeg` | மாதப்பூசம் lamp |
| `09-poosam-annadanam-02.jpeg` | annadanam |
| `09-poosam-worship-03.jpeg` | worship |
| `09-neyveli-bookfair-01..03.jpeg` | Neyveli book fair |
| `09-student-health-check-01..03.jpeg` | student medical / blood check |

All `:::image src=…` references resolve to files under `images/`.

## Verification summary

| Article | Key phrases | Image refs | Notes |
|---|---|---|---|
| 02 | all present | 5 placements / 2 unique files | Title in YAML; kural numbers in `source=` |
| 03 | same as 05 | same as 05 | **duplicate of 05** |
| 05 | all present | 6/6 | English image alts kept as captions |
| 07 | all present (incl. source typo) | none | no media in Word |
| 09 | all present | 13/13 | Windows path alts discarded; descriptive names used |

Automated window-match scores are slightly under 100% because MMD splits title / `source=` / `caption=` into attributes; every checked content phrase still appears in the markdown.

## Still missing for Issue-02 (not in this batch)

Per `issue_meta.json`, no Word sources yet for:

- `01-thalayangam.md`
- `04-sangam.md`
- `06-nuul.md`
- `08-manam.md`
- `10-closing.md`
- Real `03-sirukathai` (short story)
- Planned thirukkural topic “நட்பு அதிகாரம்” if different from the “ஆறுவது சினம்” draft

## Working files

- `_convert/` — intermediate pandoc/plain + unpacked Word media (safe to delete after review)
- Original `.docx` files left in place (not deleted)
