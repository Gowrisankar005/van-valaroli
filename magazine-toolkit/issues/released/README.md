# Released issues — the shipped record

Each subfolder here is a completed, published issue. Two shapes exist,
depending on which system built it (see root `CLAUDE.md` PART 1):

## `Issue-02/` onward — built via this toolkit (System B)

The **complete, reproducible recipe** — everything needed to rebuild the
exact same PDF from scratch:

```
Issue-NN/
├── issue_meta.json      — issue identity + section list
├── articles/*.md         — the final MMD source, one file per section
├── images/*               — every image those articles reference
├── ISSUE-NN_PLAN.md      — the concrete production plan for this issue (if kept)
└── final/
    ├── VAN_Vallaroli_<Month><Year>.html         — the fully rebalanced, final HTML
    ├── VAN_Vallaroli_<Month><Year>_fixed.html   — the pre-rebalance intermediate
    └── VAN_Vallaroli_<Month><Year>.pdf           — what actually shipped
```

To rebuild and confirm it still matches:
```bash
python make_magazine.py --from-issue issues/released/Issue-NN output/test.pdf
```

## `Issue-01/` — built via the legacy System A process

Issue 01 predates this toolkit — it was a hand-built, single-file HTML
document, not an MMD source. There's no `articles/`/`images/` recipe to keep
here, just the record:

```
Issue-01/
└── final/VAN_Vallaroli_Magazine.pdf   — what shipped
```

The full legacy history (the hand-built HTML iterations, raw author drafts,
etc.) lives in root `Archive/` if it's ever needed.

## Promoting a newly-finished issue here

When an active issue (`issues/Issue-NN/`) ships:
1. `git mv issues/Issue-NN issues/released/Issue-NN`
2. Create `issues/released/Issue-NN/final/`, move in the final HTML(s) from
   `source/` and copy in the PDF from `output/` before it's overwritten by
   the next build.
3. If a per-issue plan doc exists at the toolkit root, move it in alongside.
