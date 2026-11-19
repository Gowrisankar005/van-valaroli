# Issue 04 Production Tracker — கார்த்திகை 2026 (Dec 2026 release)

Live checklist for building Issue 04. Status: ⬜ not started · 🔄 in progress · ✅ done · ⛔ blocked.
General reference: `PRODUCTION_WORKFLOW.md`. Moves into `issues/released/Issue-04/` when shipped.

## 1. Issue identity

| Field | Value | Status |
|---|---|---|
| Issue number | 4 | ✅ set in `issue_meta.json` |
| Tamil month / year | கார்த்திகை 2026 (Nov–Dec) | ✅ |
| Release date | 1 டிசம்பர் 2026 | ✅ |
| Next issue (closing-page teaser) | தை 2027 — இதழ் 5, வெளியீடு 1 பிப்ரவரி 2027 | ✅ in meta; ⬜ write `11-closing.md` |
| Theme | default (green) | ⬜ confirm |

The next release is 1 பிப்ரவரி 2027. That date falls in தை, so the teaser is தை 2027, not மார்கழி. Issue 03's first scaffold named the following Tamil month (ஐப்பசி) and had to be corrected the same way.

Already promised in Issue 03's closing page: மனம் தொடர் Part 3 (ம. அபிராமி; Part 2 ends on மனம் versus உள்ளம்), the next ஒழுக்கம் (ஏ. ஹரிஹரன்; the 4th of வள்ளலார்'s 28, name not chosen), and a flower a reader names for சங்க இலக்கியம். Fiction is still open: Issue 03 editorial note E7 says another author; the புதுமைப்பித்தன் series is not assumed.

## 2. Content tracker (one row per article)

Columns: Draft in · MMD · Lint · Images · Proof · Final. Open topics stay TBD — check the rotation tracker in root `CLAUDE.md` PART 6 before assigning. Standing series authors are named below; they are not a new assignment.

| # | Section | File | Topic | Author | Draft in | MMD | Lint | Images | Proof | Final |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | தலையங்கம் | `01-thalaiyangam.md` | TBD | TBD | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| 2 | திருக்குறள் ஆய்வு | `02-thirukkural.md` | TBD | TBD | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| 3 | சிறுகதை | `03-sirukathai.md` | Open — another author, or the next புதுமைப்பித்தன் story (E7) | TBD | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| 4 | சங்க இலக்கியம் | `04-sangailakkiyam.md` | A flower a reader names (not தாமரை, Issue 02's flower essay, or செங்காந்தள்) | TBD | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| 5 | தமிழகக் கலைகள் | `05-kalai.md` | TBD | TBD | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| 6 | நூல் மதிப்புரை | `06-nool-mathippurai.md` | TBD | TBD | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| 7 | ஓர் ஒழுக்கம் | `07-ozhukkam.md` | 4th of the 28; name not chosen | ஏ. ஹரிஹரன் (lessons 1–3) | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| 8 | மனம் தொடர் | `08-manam.md` | Part 3 — மனமும் உள்ளமும் | ம. அபிராமி (parts 1–2) | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| 9 | இயற்கை தரும் இன்பம் | `09-iyarkai.md` | TBD | TBD | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| 10 | அறநிலையச் செய்திகள் | `10-activities.md` | அறநிலைய நிகழ்வுகள் — அக்டோபர்-நவம்பர் 2026 | TBD | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| 11 | அடுத்த இதழில் | `11-closing.md` | தை 2027 — இதழ் 5 | ஆசிரியர் குழு | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |

Carry-over lessons from Issue 03: cover image must differ from Issue 03's (`md5` check); verify every Kural/verse against a canonical edition; re-check `section:` strings exactly match `issue_meta.json`.

---

## 3. Steps & checklist

### Phase A — Setup

| # | Step | What to check | Status |
|---|---|---|---|
| A1 | Scaffold issue folder from `_starter-template` | `issues/Issue-04/` exists; sample articles/images removed | ✅ |
| A2 | Set issue identity in `issue_meta.json` | number 4, கார்த்திகை, `year_tamil` ௨௦௨௬, dates, `next_issue` தை 2027 | ✅ |
| A3 | Section list matches the 11-section shape | every `file` + `section_name` present | ✅ |
| A4 | Confirm topics with authors | no `(TBD)` left in `topic_title`; rotation tracker Issue 4 column filled with the real topics | ⬜ |

### Phase B — Content intake (per article)

| # | Step | What to check | Status |
|---|---|---|---|
| B1 | Stage raw submission | saved as `_drafts/NN-slug/source.docx`; a revised draft **replaces** it (no v2/v3 copies) | ⬜ |
| B2 | Convert with pandoc | `converted.md` regenerated after every new `source.docx`; extracted images in `_drafts/.../images/` | ⬜ |
| B3 | Hand-clean into MMD | frontmatter (`section`, `title`, `subtitle`, `author`); subheads `##`; `:::quote` / `:::box` / `:::image` / `:::closing` used per `docs/MMD_Specification.md` | ⬜ |
| B4 | `section:` matches `issue_meta.json` | exact string match, including spacing | ⬜ |
| B5 | Kural / verse citations | every quote has `source="திருக்குறள் NN"` (with number); verse text checked against a canonical edition — சொல் spelling (ன்/ண், ற்/ட்) is easy to get wrong | ⬜ |
| B6 | செந்தமிழ் check | no loan words (e.g. தர்மம் → அறம்); `validate_mmd.py` flags most, but read for the rest | ⬜ |
| B7 | Lint each article as it lands | `python validate_mmd.py issues/Issue-04/articles/NN-*.md --issue issues/Issue-04` → 0 errors | ⬜ |
| B8 | Length vs target | linter's `~pages` close to plan; too short → empty page bottoms | ⬜ |

### Phase C — Images

| # | Step | What to check | Status |
|---|---|---|---|
| C1 | Cover image | `images/cover-image.jpeg`, portrait, ≥ ~1600×2200 px; **not a copy of a previous issue's cover** (Issue 02's was byte-identical to Issue 01's until caught — compare with `md5`) | ⬜ |
| C2 | Author/subject portraits | use `type="portrait"` (45mm, no border) — never `half` | ⬜ |
| C3 | Artifact/diagram photos | `type="half"` (80mm centered) | ⬜ |
| C4 | Two images in a row | alternate `float` / `float-left`; never two same-side floats back to back | ⬜ |
| C5 | Baked-in white borders | open each image; crop white padding out of the file itself (CSS can't fix it) | ⬜ |
| C6 | Every `src=` exists in `images/` | linter reports missing files | ⬜ |
| C7 | Alt/caption text | Tamil caption on every figure | ⬜ |

### Phase D — Front matter & closing page

| # | Step | What to check | Status |
|---|---|---|---|
| D1 | Masthead names | `magazine_defaults.json` roles + தொகுப்பாசிரியர்கள் still current | ⬜ |
| D2 | `11-closing.md` teaser text | says **தை 2027 — இதழ் 5**, and the contact box says **தை 2027 — பிப்ரவரி 2027** (1 பிப்ரவரி 2027). The printed line names the month, as Issue 03 did. | ⬜ |
| D3 | வாசகர் குரல் | real reader quotes gathered, no placeholder text left | ⬜ |
| D4 | Signature block | short label-like lines (not full sentences) so the parser finds the signature | ⬜ |

### Phase E — Build & verify

| # | Step | What to check | Status |
|---|---|---|---|
| E1 | Lint everything | `python validate_mmd.py issues/Issue-04/articles/*.md --issue issues/Issue-04` → 0 errors, 0 warnings | ⬜ |
| E2 | Build | `python make_magazine.py --from-issue issues/Issue-04 output/VAN_Vallaroli_Karthigai2026.pdf` completes | ⬜ |
| E3 | Integrity audit (Step 3 in log) | all ✓: section order, paragraphs preserved, bylines on first pages, image count | ⬜ |
| E4 | Pagination log | `[3/5] Backfilled N element(s)` present; note "Zoomed N pages" count | ⬜ |
| E5 | Page count sane | roughly 32–36 pages; TOC page numbers match | ⬜ |

### Phase F — PDF review (open the PDF, page by page)

| # | Check | Status |
|---|---|---|
| F1 | Cover: image, "இதழ் 4 · கார்த்திகை 2026" pill, teaser list (max 6) | ⬜ |
| F2 | Page 2 imprint: issue 4, திருவள்ளுவர் ஆண்டு **2057**, release month | ⬜ |
| F3 | Page 3 masthead: roles, தொகுப்பாசிரியர்கள், contact | ⬜ |
| F4 | Page 4 TOC: all 11 sections listed, page numbers correct | ⬜ |
| F5 | Every footer: `இதழ் எண்: 4 \| கார்த்திகை 2026`, number centered, footer pinned to bottom | ⬜ |
| F6 | Every section start: big title + author byline | ⬜ |
| F7 | No hanging subhead alone at a page bottom | ⬜ |
| F8 | No large empty gap mid-article (end-of-section gaps are fine) | ⬜ |
| F9 | Quotes: green bar, italic, citation present | ⬜ |
| F10 | Images: correct type/size/alignment, no cropped faces, no squeezed text column | ⬜ |
| F11 | Text is real text: Cmd+F finds a Tamil word; select/copy works | ⬜ |
| F12 | File size 5–20 MB | ⬜ |
| F13 | Full proof-read pass of the built PDF (read it as a reader — Issue 02's last typos were only caught here) | ⬜ |

### Phase G — Revisions & sign-off

| # | Step | What to check | Status |
|---|---|---|---|
| G1 | Fix content in the `.md` only, then rebuild | never hand-edit built HTML; rebuild reproduces the fix | ⬜ |
| G2 | After each fix round | re-run E1–E3; compare page count against previous build | ⬜ |
| G3 | Pipeline bug found? | fix it in the shared script, add a lesson to root `CLAUDE.md` PART 9 | ⬜ |
| G4 | Editor + Gowri final approval | | ⬜ |

### Phase H — Release & wrap-up

| # | Step | What to check | Status |
|---|---|---|---|
| H1 | Final build from the committed source | commit articles/images/meta first, then build the release PDF | ⬜ |
| H2 | Distribute | email list, vallalar.org upload, print copy (A4, 90 GSM, colour, saddle-stitch) | ⬜ |
| H3 | Invitation/welcome message | drafted and sent with the PDF | ⬜ |
| H4 | Promote to released | `git mv issues/Issue-04 issues/released/Issue-04`; add `final/` with shipped HTML + PDF | ⬜ |
| H5 | Update trackers | root `CLAUDE.md` PART 6 rotation tracker (fill the Issue 4 column with the shipped topics); create `issues/Issue-05` from `_starter-template` | ⬜ |
| H6 | Merge `issue-04` → `main`, push | after H4, once the release is confirmed | ⬜ |
| H7 | Clear `Archive/` (local only) | Gowri planned to delete it after Issue 04 — confirm nothing depends on it first | ⬜ |

---

