# Starter template — copy this to begin a new issue

You just copied `issues/_starter-template/` (or you're looking at it to see what a
minimal issue looks like). This folder is a working 3-article demo — it builds
on its own, so it doubles as the pipeline's smoke test.

## Start a new issue from here

```bash
cd magazine-toolkit
cp -r issues/_starter-template issues/Issue-03
```

Then:

1. **Edit `issue_meta.json`** — bump `issue_number`, set `tamil_month`/`year`/
   `year_tamil`/`english_dates`, update `next_issue`, and replace `sections`
   with this issue's real section/topic list. Check the rotation tracker in
   root `CLAUDE.md` PART 6 first so you don't repeat a topic that's still
   fresh, and note any series (e.g. மனம் தொடர்) that owes a next part.
2. **Delete the 3 sample articles** in `articles/` and the sample images in
   `images/`, and drop in the real ones — one `.md` per section (see
   `docs/MMD_Specification.md` for the format), naming convention
   `NN-slug.md` matching each article's images to `NN-...` where relevant.
   If author submissions arrive as `.docx`/raw text first, stage them in
   `_drafts/` and convert before they land here — see `PRODUCTION_WORKFLOW.md`
   Phase 3 for that intake workflow.
3. **Validate:**
   ```bash
   python validate_mmd.py issues/Issue-03/articles/*.md --issue issues/Issue-03
   ```
4. **Build:**
   ```bash
   python make_magazine.py --from-issue issues/Issue-03 output/VAN_Vallaroli_<Month><Year>.pdf
   ```
5. Once it ships, promote it: move `issues/Issue-03/` into
   `issues/released/Issue-03/`, add a `final/` folder with the shipped
   HTML + PDF (see `issues/released/README.md`).

## What's in this folder

| File | Purpose |
|---|---|
| `issue_meta.json` | Issue identity + section list. The schema to copy from. |
| `articles/*.md` | 3 example MMD articles — subhead, quote, box, image directives all demonstrated. |
| `images/*` | The images those 3 articles reference. |

Full reference: `PRODUCTION_WORKFLOW.md` (general per-issue workflow) and
`docs/MMD_Specification.md` (the authoring format itself).
