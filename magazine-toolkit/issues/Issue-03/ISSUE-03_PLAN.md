# Issue 03 Production Tracker — புரட்டாசி 2026 (Oct 2026 release)

Live checklist for building Issue 03. Update the **Status** column as work
moves: ⬜ not started · 🔄 in progress · ✅ done · ⛔ blocked (add a note).
General reference: `PRODUCTION_WORKFLOW.md`. When the issue ships, this file
moves with the issue into `issues/released/Issue-03/` (see step H4).

## 1. Issue identity

| Field | Value | Status |
|---|---|---|
| Issue number | 3 | ✅ set in `issue_meta.json` |
| Tamil month / year | புரட்டாசி 2026 (Sep–Oct) | ✅ |
| Release date | 1 அக்டோபர் 2026 | ✅ |
| Next issue (closing-page teaser) | கார்த்திகை 2026 — இதழ் 4, வெளியீடு 1 டிசம்பர் 2026 | ✅ in meta and `11-closing.md` |
| Theme | default (green) | ✅ |

---

## 2. Content tracker (one row per article)

Columns: **Draft in** = author's submission received · **MMD** = converted to
`articles/*.md` · **Lint** = `validate_mmd.py` clean · **Images** = all present
+ correct `type=` · **Proof** = human proof-read done · **Final** = editor sign-off.

| # | Section | File | Topic | Author | Draft in | MMD | Lint | Images | Proof | Final |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | தலையங்கம் | `01-thalaiyangam.md` | ஒழுக்கமே உலக நலம் | மு. முத்துஜோதி | ✅ | ✅ | ✅ | — | ⬜ | ⬜ |
| 2 | திருக்குறள் ஆய்வு | `02-thirukkural.md` | நாவினால் சுட்ட வடு (ஆறுவது சினம்) | வெ. வானதி | ✅ | ✅ | ✅ | ✅ | ⬜ | ⬜ |
| 3 | சிறுகதை | `03-sirukathai.md` | கட்டில் பேசுகிறது — புதுமைப்பித்தன் சிறுகதைத் தொடர் (accepted) | புதுமைப்பித்தன் | ✅ | ✅ | ✅ (loan-word warnings expected) | — | ⬜ | ⬜ |
| 4 | சங்க இலக்கியம் | `04-sangailakkiyam.md` | காந்தள் மலரின் அறம் | இரா. கௌரிசங்கர் | ✅ | ✅ | ✅ | ✅ | ⬜ | ⬜ |
| 5 | தமிழகக் கலைகள் | `05-kalai.md` | மரம் முதல் கற்றளி வரை (Issue 02 தொடர்ச்சி) | கு. திருமுருகன் | ✅ | ✅ | ✅ | ✅ (5/5, verified via isolated build render) | ⬜ | ⬜ |
| 6 | நூல் மதிப்புரை | `06-nool-mathippurai.md` | வள்ளலார் பார்வையில் சனாதனம் | எம்.ஜோதிமணி | ✅ | ✅ | ✅ | ✅ | ⬜ | ⬜ |
| 7 | ஓர் ஒழுக்கம் | `07-ozhukkam.md` | தந்த சுத்தி — வழலை நீக்கல் | ஏ. ஹரிஹரன் | ✅ | ✅ | ✅ | — | ⬜ | ⬜ |
| 8 | மனம் தொடர் | `08-manam.md` | மனம் எனும் ஏணி (பகுதி 2) | ம. அபிராமி | ✅ | ✅ | ✅ | — | ⬜ | ⬜ |
| 9 | இயற்கை தரும் இன்பம் | `09-iyarkai.md` | குறிஞ்சி நிலம் — மலையும் ஏரியும் (உதகமண்டலம்) | தொகுப்பு: ஆசிரியர் குழு | ✅ | ✅ | ✅ | ✅ | ⬜ | ⬜ |
| 10 | அறநிலையச் செய்திகள் | `10-activities.md` | ஆகஸ்ட்-செப்டம்பர் 2026 நிகழ்வுகள் | க. குமாரவேல் | ✅ | ✅ | ✅ | ✅ (14/14 captioned) | ✅ | ✅ |
| 11 | அடுத்த இதழில் | `11-closing.md` | கார்த்திகை 2026 teaser + வாசகர் குரல் | ஆசிரியர் குழு | ✅ | ✅ | ✅ | — | ⬜ | ⬜ |

Update `topic_title` in `issue_meta.json` as each topic is confirmed — the
cover teasers and TOC subtitles are built from it.

---

## 3. Steps & checklist

### Phase A — Setup (done)

| # | Step | What to check | Status |
|---|---|---|---|
| A1 | Scaffold issue folder from `_starter-template` | `issues/Issue-03/` exists; sample articles/images removed | ✅ |
| A2 | Set issue identity in `issue_meta.json` | number 3, புரட்டாசி, `year_tamil`, dates, `next_issue` | ✅ |
| A3 | Section list matches the 11-section shape | every `file` + `section_name` present | ✅ |
| A4 | Confirm topics with authors | no `(TBD)` left in `topic_title` (6 of 11 set); rotation tracker in root `CLAUDE.md` PART 6 updated | 🔄 |

### Phase B — Content intake (per article)

| # | Step | What to check | Status |
|---|---|---|---|
| B1 | Stage raw submission | saved as `_drafts/NN-slug/source.docx`; a revised draft **replaces** it (no v2/v3 copies) | 🔄 |
| B2 | Convert with pandoc | `converted.md` regenerated after every new `source.docx`; extracted images in `_drafts/.../images/` | 🔄 |
| B3 | Hand-clean into MMD | frontmatter (`section`, `title`, `subtitle`, `author`); subheads `##`; `:::quote` / `:::box` / `:::image` / `:::closing` used per `docs/MMD_Specification.md` | 🔄 |
| B4 | `section:` matches `issue_meta.json` | exact string match, including spacing | ⬜ |
| B5 | Kural / verse citations | every quote has `source="திருக்குறள் NN"` (with number); verse text checked against a canonical edition — சொல் spelling (ன்/ண், ற்/ட்) is easy to get wrong | ⬜ |
| B6 | செந்தமிழ் check | no loan words (e.g. தர்மம் → அறம்); `validate_mmd.py` flags most, but read for the rest | ⬜ |
| B7 | Lint each article as it lands | `python validate_mmd.py issues/Issue-03/articles/NN-*.md --issue issues/Issue-03` → 0 errors | 🔄 (6 in: 0 errors; 4 loan-word warnings in 03) |
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
| D2 | `11-closing.md` teaser text | says **கார்த்திகை 2026 — இதழ் 4**, and the contact box says **கார்த்திகை 2026 — டிசம்பர் 2026** (1 டிசம்பர் 2026). The printed line names the month, as Issue 02 did. | ✅ |
| D3 | வாசகர் குரல் | real reader quotes gathered, no placeholder text left | ⬜ |
| D4 | Signature block | short label-like lines (not full sentences) so the parser finds the signature | ⬜ |

### Phase E — Build & verify

| # | Step | What to check | Status |
|---|---|---|---|
| E1 | Lint everything | `python validate_mmd.py issues/Issue-03/articles/*.md --issue issues/Issue-03` → 0 errors, 0 warnings | ⬜ |
| E2 | Build | `python make_magazine.py --from-issue issues/Issue-03 output/VAN_Vallaroli_Purattasi2026.pdf` completes | ⬜ |
| E3 | Integrity audit (Step 3 in log) | all ✓: section order, paragraphs preserved, bylines on first pages, image count | ⬜ |
| E4 | Pagination log | `[3/5] Backfilled N element(s)` present; note "Zoomed N pages" count | ⬜ |
| E5 | Page count sane | roughly 32–36 pages; TOC page numbers match | ⬜ |

### Phase F — PDF review (open the PDF, page by page)

| # | Check | Status |
|---|---|---|
| F1 | Cover: image, "இதழ் 3 · புரட்டாசி 2026" pill, teaser list (max 6) | ⬜ |
| F2 | Page 2 imprint: issue 3, திருவள்ளுவர் ஆண்டு **2057**, release month | ⬜ |
| F3 | Page 3 masthead: roles, தொகுப்பாசிரியர்கள், contact | ⬜ |
| F4 | Page 4 TOC: all 11 sections listed, page numbers correct | ⬜ |
| F5 | Every footer: `இதழ் எண்: 3 \| புரட்டாசி 2026`, number centered, footer pinned to bottom | ⬜ |
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
| H4 | Promote to released | `git mv issues/Issue-03 issues/released/Issue-03`; add `final/` with shipped HTML + PDF | ⬜ |
| H5 | Update trackers | root `CLAUDE.md` PART 6 rotation tracker (Issue 3 column); create `issues/Issue-04` from `_starter-template` | ⬜ |
| H6 | Merge `issue-03` → `main`, push | after H4, once the release is confirmed | ⬜ |
| H7 | Clear `Archive/` (local only) | Gowri planned to delete it after Issue 03 — confirm nothing depends on it first | ⬜ |

---

## 4. Timeline (fill in dates)

| Milestone | Target date | Status |
|---|---|---|
| Topics + authors confirmed | | ⬜ |
| First drafts in | | 🔄 |
| Cover image ready | | ⬜ |
| All articles converted + linted | | 🔄 |
| First full build + review | | ⬜ |
| Proof-read rounds complete | | ⬜ |
| **Release** | | ⬜ |

---

## 5. Watch-outs carried over from Issue 02

| Risk | Mitigation |
|---|---|
| Typos slip through to the released PDF (Issue 02 needed 2 post-build proof rounds) | Proof-read the *built PDF* as a reader, not just the markdown; keep a change log |
| Kural quote text or number wrong | Check each against a canonical source; always cite `திருக்குறள் NN` |
| Revised draft arrives after conversion | Replace `source.docx`, re-convert, re-diff against the current `.md` — don't lose earlier hand edits |
| Cover image duplicated from a previous issue | `md5` compare against `issues/released/*/images/cover-image.*` |
| Section too short → empty page bottom | Check linter's `~pages` against target before final build; split a long paragraph at a sentence break if needed |
| Portrait used as `half` | Use `portrait` |
| "Next issue" text stale in closing article | D2 above |
| Loan-word warnings in a reprinted classic story | Expected — keep the author's original words (see root `CLAUDE.md` PART 4) |
| Working in the wrong checkout | Issue 03 work happens in `/Users/gowri/spaceclub/e-magazine-issue-03` (branch `issue-03`) |

---

## 6. Editorial desk — before 1 October 2026

From the full read of `output/VAN_Vallaroli_Purattasi2026.pdf` (27 Sep build).
Two items from that read are already done and are not in this list: the masthead YouTube address is one line, and ஜோதிமணி அம்மா’s letter is out of `11-closing.md`. Do not rewrite an author’s wording until the action below says the sentence is approved. 15.08.2026 as the 80th Independence Day matches India’s count — leave it. MD, NMMS, UKG, ரூபாய், and WhatsApp match Issue 02 — leave them.

| # | Where | What is wrong | Action | Status |
|---|---|---|---|---|
| E1 | `02-thirukkural.md`, pp. 8–11 | The nail-and-fence story is printed as ஔவையாரின் கதை, and the essay says she compressed it into "ஆறுவது சினம்". குறள் 129, 305, 306 are correct. The subhead கற்றல் வெளிப்பாடு sounds like a school worksheet. | Reframe the story as a modern tale that illuminates the ஆத்திசூடி line and the three kurals. Do not attribute the story to ஔவையார். Keep the kural text. Rename or remove கற்றல் வெளிப்பாடு. Show Gowri the replacement sentences before they replace வானதி’s lines. | ⬜ |
| E2 | `02-thirukkural.md`, pp. 8–10 | Four staged porch frames (father, son, hammer, paling). One has a guitar behind the father. They were added on purpose as a 4-panel comic. They sit in a different world from the Tamil cover. | Editor chooses: keep all four, or keep one and delete the other image directives. Do not crop the files. Name which `src` stays before editing. | ⬜ |
| E3 | `01-thalaiyangam.md`, pp. 6–7 | The Zen tale makes the loser cut his own throat. It sits under எல்லா உயிர்களும் இன்புற்று வாழ்க. The leap to வால்மீகி is told as history. | மு. முத்துஜோதி rereads those pages. If the tale stays, add one clause that it is a story from a Zen book, and the same for வால்மீகி. No edit until he supplies or approves the words. | ⬜ |
| E4 | `01-thalaiyangam.md`, p. 5 | நற்குடி / தீய குடி says conduct follows birth. The book review later says birth-rank must go. | Same reread. If he wants the lines softened, he supplies the sentences. Do not rewrite them unasked. | ⬜ |
| E5 | `04-sangailakkiyam.md` | The printed author is இரா. கௌரிசங்கர், who is also பதிப்பாசிரியர் on page 3. | Confirm with Gowri that this byline stays. Change nothing until that yes. | ⬜ |
| E6 | `06-nool-mathippurai.md`, p. 26 | The review asks grandparents to tell the நங்கேலி history to grandchildren. The history itself can stay for adult readers. | Replace only the "share this with grandchildren" instruction with a line for adult readers, after Gowri approves the sentence. Leave the historical paragraph. | ⬜ |
| E7 | `03-sirukathai.md`, p. 14 | After மணிக்கொடி, 13,5,1934 a life-sketch (dates, 108 stories, 2002, magazine list) answers the bed. The story’s own language, including its loan words, stays. A duplicate date line is already flagged in the change log. | End the piece on the nurse and the boots. Keep one date line. Get a yes before cutting the biography, in case it was added on purpose. Issue 4 fiction: another author — this is a note, not an edit to this file. | ✅ story ends on the nurse and the boots; subtitle keeps the one date line; life-sketch is two sentences. Issue 4 fiction note still open. |
| E8 | `08-manam.md`, pp. 30–31 | The lead states that தொல்காப்பியர் was 3300 years before டார்வின். Page 31 prints சலிப்பு (Boredom). "ஏழு திரைகள்" around the Buddha has no source. The ladder and the four practices are the part to keep. | Ask அபிராமி / the editor which of the three to soften. Edit only after they choose. Do not invent a date for தொல்காப்பியம். | ⬜ |
| E9 | `05-kalai.md`, p. 23 | Three temple photos, then a source line naming இணையக் காணொளிகள் and விக்கிப்பீடியா, then a large empty lower half. Pages 21–22 read as a numbered syllabus. | Editor decides. If yes: delete the video / Wikipedia credit. Leave the five photos and the history text unless a separate voice pass is requested. | ⬜ |
| E10 | `09-iyarkai.md`, p. 33 | One Ooty lake photograph and four lines. Usable as a pause. Thin beside the six-page flower essay. | Editor chooses. If it stays a pause, no edit. If not, add a short paragraph in the magazine’s voice (the byline is ஆசிரியர் குழு). Do not crop the lake. | ⬜ |
| E11 | `11-closing.md`, pp. 38–39 | Three long letters can still fill one page and leave the contact box alone on the last page. ஜெயலட்சுமி says "இதுவரை தெரியாத நிறைய தகவல்கள்" twice. சித்ரா writes பாரி–வேளிர்; the other letter writes பாரி–பேகன். The title promises இதழ் 4 and does not say what continues. | Add one line naming what continues: மனம் தொடர், the next ஒழுக்கம், and a flower name from a reader. Trim ஜெயலட்சுமி’s repeated sentence. Leave பாரி–வேளிர் as she wrote it. | ✅ |
| E12 | `10-activities.md`, p. 34 | The news states இது பக்க விளைவுகள் இல்லாத மருத்துவமாகும். | Replace that sentence with a report that தயவு மருத்துவர் அருள் MD saw patients and gave medicine. Confirm the sentence with குமாரவேல் / Gowri; this article’s wording was preserved on purpose. | ✅ already in the article and the PDF: மருத்துவம் பார்க்கப்பட்டு மருந்துகளும் இலவசமாக வழங்கப்பட்டது. 80-வது சுதந்திர தினம் left as printed. |
| E13 | `07-ozhukkam.md`, p. 28 | The index finger is called தர்சனி விரல். Optional. | If the editor wants செந்தமிழ் here, change that one phrase to ஆள்காட்டி விரல். Leave ஜீவகாருண்யம் — it is வள்ளலார்’s term, and the article explains it. | ✅ phrase changed. ஜீவகாருண்யம் left. |

---

## 7. Change log

| Date | Change |
|---|---|
| 2026-09-28 | E13: `07-ozhukkam.md` கட்டை விரலில் (தர்சனி விரல்) → கட்டை விரலில் (ஆள்காட்டி விரல்). ஜீவகாருண்யம் unchanged. |
| 2026-09-28 | 03-sirukathai: story ends on the nurse and the boots. Dropped the repeated `மணிக்கொடி, 13,5,1934` line (subtitle keeps it) and the catalog after it (108 stories, magazine list, 2002, 2000). Two-sentence life-sketch remains. His wording untouched. |
| 2026-09-28 | E12 closed: `10-activities.md` and the built PDF already report that தயவு மருத்துவர் அருள் MD saw patients and gave medicine. The side-effect claim is not in the file. |
| 2026-09-28 | 11-closing: dropped ஜெயலட்சுமி’s second “தெரியாத தகவல்கள்” sentence; added one line that கார்த்திகை continues மனம் தொடர், the next ஒழுக்கம், and a flower name from a reader. பாரி–வேளிர் left as சித்ரா wrote it. |
| 2026-09-28 | Masthead YouTube address kept on one line (`.masthead-url`, 7pt, no mid-word break). ஜோதிமணி அம்மா’s letter removed from `11-closing.md`; the other three letters unchanged. Editorial desk list added as section 6 (E1–E13), not yet edited. |
| 2026-09-26 | Articles 01, 02, 03, 05, 07, 08 converted. Fixes applied after first review: editorial `@`→`;`, signature moved into `:::closing`, typos; anger story — comic split into 4 cropped panels (`half`), kural citations → `திருக்குறள் NN`, `வெகுளாமை` chapter name; temple article — numbered era list, 5 photos → `half` (paired), Tamil-only source line (Chat GPT credit dropped); ஓர் ஒழுக்கம் — English removed, ஜீவகாருண்யம்/அருட்பெருஞ்ஜோதி spellings unified; மனம் Part 2 — `மன்-மனம்-மனிதன்` to match Issue 02. Titles set in `issue_meta.json`. |
| 2026-09-26 | Decided: சிறுகதை is an ongoing Pudhumaipithan series (accepted); classic-text loan words stay as written. Titles changed: தலையங்கம் → ஒழுக்கமே உலக நலம்; மனம் → மனம் எனும் ஏணி. |
| 2026-09-27 | 10-activities finalized: honorific fixed to "தயவு மருத்துவர் அருள் MD," (dropped "Dr."); all bold removed to match Issue 02's plain style (9 spans, 18 markers); 10-poosam-03.jpeg captioned "மாதப்பூசம் அன்னதானம்" (confirmed by Gowri). Ready to publish. |
| 2026-09-27 | 10-activities shortened per Gowri: removed 3 of 17 images (10-independence-03/04 — near-duplicate angles of 01; 10-nmms-03 — the one photo we couldn't identify/caption, so also resolves that open question). Orphan "புத்தகம் வாசிப்பு..." line folded into the intro paragraph instead of sitting alone. Length: ~4.4 est. pages -> ~3.8 est., 5 physical pages -> 4 in an isolated build (confirmed by rendering, not just the estimate). 14 images remain, 12 captioned (2 header logos + 10-poosam-03 still open). |
| 2026-09-27 | 10-activities reviewed: 13 of 17 images captioned (2 header logos intentionally left uncaptioned, matching Issue 02); missing spaces after Tamil punctuation fixed throughout; hyphens -> em-dash for subhead date ranges; typos மருத்துவோம்->மருத்துவம், சுற்றுசூழல்->சுற்றுச்சூழல் fixed; duplicate "மாதப்பூசம்" in one subhead removed; ரூபாய்.1000 -> ரூபாய் 1000. Still open for final review: "தயவு திரு.Dr.அருள்" honorific (match Issue 02's "மருத்துவர் அருள் MD"?), "(Zoom)" -> plain "மெய்நிகர் தளத்திலும்" (already applied, dropped the brand name) — confirm OK; heavy/inconsistent **bold** on dates and numbers (Issue 02 used almost none); article runs ~4.4 pages vs the 2-3 typical budget (5 events vs Issue 02's 4) — trim or accept the extra length?; the orphan line about reading practice (no image/subhead) — fold into another section?; captions for 10-poosam-03.jpeg and 10-nmms-03.jpeg still unknown — need Gowri to say what each photo shows. |
| 2026-09-27 | 06-nool-mathippurai reviewed: நாஞ்சிலி -> நங்கேலி (correct historical name), அற நிலையம் -> அறநிலையம் spacing fixed, topic_title set. No rating line — decided against for now. Pulled "கலையுரைத்த கற்பனையே..." into a proper :::quote block for visual consistency with the rest of the issue (Gowri's call, per suggestion); other Vallalar quotes kept inline as written (well-known, accurate as given). Byline "M.ஜோதிமணி" and the content-sensitivity note (names காஞ்சி மகாபெரியவர் directly) deferred to final review. |
| 2026-09-27 | 06-nool-mathippurai content-sensitivity note resolved: softened the காஞ்சி மகாபெரியவர் reference — removed the named attribution and direct quote, kept the book's actual argument (it historically refutes a common claim about religious conversion) intact. Lint clean, 2.6 pages, unchanged. Still open: byline "M.ஜோதிமணி" formatting. |
| 2026-09-26 | Temple-article page gap fixed: two Mahendravarman photos → side floats, Pancha Ratha paragraph moved above its photo (text unchanged). Pipeline: a `:`-intro line stays glued to its list; backfill may pull from a last page (CLAUDE.md Lesson 12). |
| open | 03 story: duplicate date line at the end, bold drop-cap `**க**` · editorial page 1 and ஓர் ஒழுக்கம் have ~15–20% bottom gaps from long paragraphs (split at a sentence if wanted) |
| 2026-09-27 | 04-sangailakkiyam written: காந்தள் (Gloriosa superba, TN state flower), author இரா. கௌரிசங்கர். Structured around 6 verbatim Sangam quotes with citations (குறுந்தொகை 284 & 265, புறநானூறு 144 & 168, திருமுருகாற்றுப்படை, பரிபாடல் 18), opens by referencing Issue 02's "காந்தள் போன்ற கைகள்" line for continuity. 3 images added from Gowri's own photos (`_drafts/kandhal-01/02/03.jpg` → `04-kandhal-viral.jpg` float, `04-kandhal-muruga.jpg` float-left, `04-kandhal-banner.jpg` banner). Lint clean, 4.4 est. pages — matches Issue 02's matching article almost exactly. `topic_title` set in `issue_meta.json`. Still open: proof-read + final sign-off. |
| 2026-09-27 | Separate review draft only: `articles/04-sangailakkiyam_grok.md`. Same prose. Photos placed by what each frame shows — `04-kandhal-flame.jpg` banner after the look paragraph, `04-kandhal-hill.jpg` half-width in பாறைமேல், `04-kandhal-viral.jpg` right float in the finger section. Not the build file. `issue_meta.json` still points at `04-sangailakkiyam.md`. |
| 2026-09-27 | Collision resolved on the live build file (`04-sangailakkiyam.md`): the grok draft's image layout had briefly overwritten it. Compared both layouts with real preview builds (Claude's original banner+float+float-left vs. the grok layout's banner+half+float) — found CSS force-crops/caps every image type (`float`/`float-left`→60×45mm `object-fit:cover`, `banner`→full-width×≤75mm `object-fit:cover`, `half`→≤80mm `object-fit:contain`, no crop), so neither risked page overflow, but the grok layout dropped the முருகன்-section image entirely (leaving the back half of the article with zero visual breaks) and ran a page longer. Landed on a hybrid: dropped the top banner (none of the 3 photos has a panoramic shape, so it was the weakest fit for either candidate image), kept the grok layout's `half` placement of `04-kandhal-hill.jpg` directly under "பாறைமேல் ஒரு செந்தீ" (uncropped, thematically on-point), kept the shared float (`04-kandhal-viral.jpg`), restored `04-kandhal-muruga.jpg` as float-left under "முருகன் சூடிய மலர்" to fix the back-half gap. Removed now-unreferenced duplicate image files `04-kandhal-banner.jpg`/`04-kandhal-flame.jpg`. Lint clean, 4.4 est. pages. `articles/04-sangailakkiyam_claude.md` kept in sync as a safety copy. |
| 2026-09-27 | 04-sangailakkiyam citation accuracy re-verified against two independent primary sources (Project Madurai + Tamil Wikisource) after a first single-source check wrongly flagged கபிலர் (PN 144) and "கந்தப்பிள்ளை"/"மலரந்த" (PN 168) as errors — both turned out to be genuine cross-edition variants matching Wikisource exactly, not mistakes. No changes needed. Article confirmed content-ready. |
| 2026-09-27 | 06-nool-mathippurai: softened the காஞ்சி மகாபெரியவர் reference — removed the named attribution and direct quote, kept the book's actual argument (refutes a common claim about religious conversion) intact. Lint clean, 2.6 pages, unchanged length. Still open: byline "M.ஜோதிமணி" formatting. |
| 2026-09-27 | 11-closing.md written: கார்த்திகை 2026 teaser + 4 வாசகர் குரல் quotes (real feedback, collected via WhatsApp — confirmed by Gowri). issue_meta.json's `next_issue` corrected from ஐப்பசி (stale) to கார்த்திகை, matching Gowri's cadence confirmation (Oct 1 = புரட்டாசி, Dec 1 = கார்த்திகை). Release date set: 1 அக்டோபர் 2026. Lint clean, 0.5 pages. |
| 2026-09-27 | 05-kalai.md images verified ready: all 5 files exist, captioned, correctly typed (no portraits misused as half). Built an isolated preview and rendered every page — images render crisply despite modest source resolution (399–639px wide, below the CLAUDE.md "ideal" but usable), and the pipeline's existing same-type image-pairing logic automatically laid out the 3 consecutive `half` images as 2-side-by-side + 1 solo rather than a flat stack. No layout or quality issues found. Marked ✅ in tracker. |
| 2026-09-27 | Cover permanent tagline changed (all future issues): replaced placeholder "செந்தமிழில் அறம் வளர்க்கும் அறிவொளி இதழ்" with வள்ளலார்'s own couplet ("தாழ்வு எலாம் தவிர்த்துச் சக மிசை அழியா / வாழ்வு எனக்கு அளித்த "வளர் ஒளி" மணியே.") in `templates/cover.html` — editor request. The magazine's own name comes from this couplet's "வளர் ஒளி" phrase. No attribution line (removed per follow-up). Old tagline text still preserved independently on the imprint page (`templates/imprint.html`, untouched). Verified via preview render, no CSS changes needed. |
| 2026-09-27 | 06-nool-mathippurai byline resolved: "M.ஜோதிமணி" -> "எம்.ஜோதிமணி" (Tamil transliteration, per Gowri). Lint clean, 2.6 pages, unchanged. Article now fully content-ready — nothing deferred. |
| 2026-09-27 | Cover image finalized: `cover-image.jpeg` placed (mother + two children at a temple pond, golden hour), converted to proper JPEG, md5-confirmed not a duplicate of any released issue's cover (past bug, see CLAUDE.md Lesson list). First full pipeline build run for Issue 03: `make_magazine.py` end-to-end, `compare_html.py` integrity audit passed clean, 38 pages, 9.8MB PDF, text confirmed real/searchable via `pdftotext`. |
| 2026-09-27 | Font-size QA found and fixed a real pagination bug: 2 pages (04-sangailakkiyam p.15, 06-nool-mathippurai p.24) had overflowed and gotten auto-shrunk by build_text_pdf.py's last-resort zoom safety net — 04-sangailakkiyam's was 16.7% smaller than surrounding pages (clearly visible side-by-side), caused by a `banner-full` (uncropped, full-height) image on the section's title-block page combined with 2 intro paragraphs — too much for one page. Removed the banner image (matches the earlier layout A/B finding: none of the 3 photos suit a banner slot) and shortened one image caption; shrink reduced 16.7% -> 4.6%, now in the same minor range as 06-nool-mathippurai's un-changed 5.5% (that one's overflow is much smaller and wasn't touched). Also restored `04-kandhal-muruga.jpg` as float-left under "முருகன் சூடிய மலர்" (the recurring back-half image gap from the collision history). Root cause is a pagination-estimator gap for section-opening pages that combine a title block + image — not fixed at the script level this round (would need rebalance_sections.py changes, higher risk); flagged here for a future pipeline fix per the standing rule in CLAUDE.md PART 9. |
| 2026-09-27 | 01-thalaiyangam: added the Issue 02-style reader greeting ("வான் வளரொளி இதழ் நேயர்களுக்கு வணக்கங்களும் வாழ்த்துக்களும்," + a "sharing my thoughts through issue N" line) before the existing content, per Gowri's request to match the established opening style. Lint clean, 1.8 pages (was 1.7). |
| 2026-09-27 | Editorial read-through fixes: 01-thalaiyangam's closing paraphrase now a proper `:::quote source="திருக்குறள் 131"` block (verified against multiple sources) instead of an uncited echo. 10-activities: removed the unsupported "no side effects" claim about homeopathy, kept the factual "doctor examined, medicine given free" sentence. 06-nool-mathippurai: replaced the line suggesting grandparents narrate the நங்கேலி self-mutilation story to grandchildren — kept the section's actual point (feeding the hungry = true spirituality) without that framing. |
| 2026-09-27 | 03-sirukathai trimmed (moved the மணிக்கொடி date into the `subtitle:` field where it belongs, shortened the trailing author bio) and 07-ozhukkam corrected a wrong finger name ("தர்சனி விரல்" -> "ஆள்காட்டி விரல்", the actual Tamil term for index finger) and 11-closing swapped a 4th reader quote for a forward-looking note about the next issue's content — all by Gowri directly. Also fixed: masthead's YouTube URL was wrapping mid-word on the card (font-size + white-space CSS fix in magazine.css, scoped to `.masthead-url` only). |
| 2026-09-27 | **Pipeline bug found and fixed at the shared-script level** (rebalance_sections.py) — see CLAUDE.md PART 9 Lesson 13. The 03-sirukathai trim above paradoxically made pagination *worse* (9–11% shrink on 2 pages, worse than any prior case) because the page-count estimator used a flat, wrong constant for how much a section-start page's title block costs. Root cause: `.content-area` puts THREE siblings ahead of `.body-text` (.section-header + .section-divider + .author-byline), not one — measuring only .section-header first made the fix a no-op. Fixed by measuring the real combined header-region height per section (range found: 179–248px, all higher than the old flat 165px assumption, explaining why overflow was systemic). Also added the missing `page.emulate_media('print')` call to rebalance's two measurement passes (Lesson 11's rule, was never applied here). Result: 03-sirukathai's shrink eliminated entirely (back to 3 clean pages); 04-sangailakkiyam/06-nool-mathippurai's pre-existing minor shrinks (4.6%/5.5%) unchanged — those were already accepted as minor before this fix and this pass didn't move them. Full pipeline rebuilt, compare_html.py integrity clean, 38 pages, 9.8MB. |
| 2026-09-29 | Date typo fixed: `issue_meta.json`'s topic_title for section 10 had a stray space ("ஆகஸ்ட் -செப்டம்பர்") — this field feeds both the TOC (p.4) and the section's own title block (p.34), so one fix resolved both occurrences the editorial review flagged. |
| 2026-09-29 | **Cover image finalized (v2):** replaced with `_drafts/coverart-03.png` — same scene (mother + two children at a temple pond, golden hour) regenerated with a more detailed temple and stronger sky. Same resolution as before (1024×1536, ~124 DPI at full A4 bleed — same softness tradeoff, not worse). md5-confirmed not a duplicate of Issue 02's cover. Rebuilt and visually confirmed: masthead text and teaser list both stay legible against the image. |
| 2026-09-29 | Cover dark-overlay transparency increased (all future issues, `templates/cover.html`'s `.masthead`/`.bottom-band` gradients in magazine.css) — per Gowri's request to let more of the cover art show through top and bottom. Opacity stops reduced roughly 97%/94%/60% -> 78%/74%/45% (top) and 97%/93% -> 78%/70% (bottom). Rebuilt and visually confirmed text (title, tagline, quote, teaser list) stays fully legible against the lighter scrim. |
| 2026-10-01 | Proofing pass: cover tagline's "வளர் ஒளி" now bold, quote marks removed (`templates/cover.html`, all future issues). 11-closing's 3 வாசகர் குரல் attributions now bold the reader's name. 02-thirukkural fixed a hyphen artifact ("30-க்கும்" -> "30க்கும்") that was wrapping awkwardly across a line break on p.8. Rebuilt, integrity clean, 39 pages, 9.8MB, all three changes visually confirmed. |
| 2026-10-01 | 04-sangailakkiyam (காந்தள் article) clarity fixes: named the boar explicitly ("அதன் கிழங்கு மண்ணைப் புரட்ட" -> "காட்டுப் பன்றி அதன் கிழங்கைத் தேடி மண்ணைப் புரட்ட") so the reader isn't left guessing who's digging; trimmed a redundant restatement of the already-stated toxicity warning later in the same article. Toxicity claim ("no part of the plant is food") independently verified against medical/toxicology sources — understated if anything. |
| 2026-10-01 | **Pipeline bug found and fixed at the shared-script level** (`templates/magazine.css`) — see CLAUDE.md PART 9 Lesson 14. On p.22 (05-kalai), subhead "4. குடைவரைக் கோவிலிலிருந்து கற்றளிக்கு" visibly started ~500px right of the page margin while subhead "3." above it started flush left — reported by Gowri from a screenshot. First diagnostic pass checked only the `.subhead` div's bounding box / border-left bar position (via Playwright geometry + pixel scan) and found it unchanged at the margin in both cases, so the fix was wrongly reverted as a non-issue. Second pass measured the actual text-line start position (not the box) and found the real gap: a taller `img-left` float above the subhead was still active when the subhead rendered, so the box's border stayed at the margin but the text line inside it got squeezed/pushed right around the float. Fixed with `clear: both;` on `.subhead`. Rebuilt, integrity clean, text start position confirmed identical to subhead 3 after the fix. **Lesson:** a bounding-box/border check doesn't catch float-driven text-line indentation — measure the actual glyph/text position, not just the element's box, when diagnosing a reported visual shift. |
| 2026-10-01 | 03-sirukathai: added an "ஆசிரியர் குறிப்பு" (Author's Note) `##` subhead immediately before the trailing Pudhumaipithan bio paragraph on p.14, so the story's ending and the editorial note about the author don't run together unmarked (Gowri flagged this as confusing). Uses the existing `.subhead` component, no new MMD directive or CSS needed. Rebuilt, integrity clean, visually confirmed. |
