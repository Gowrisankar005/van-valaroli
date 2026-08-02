# வான் வளரொளி இதழ் (Van Vallaroli Magazine)

Production repo for **வான் வளரொளி இதழ்**, the bi-monthly Tamil e-magazine
published by பெண்ணாடம் வள்ளலார் அறநிலையம் (VAN).

## New here? Start based on your role

| You are | Go to |
|---|---|
| **A new team member, not sure where to start** | `magazine-toolkit/GETTING_STARTED.md` — one-time machine setup |
| **An article contributor / author** | `magazine-toolkit/docs/Author_Guide.docx` — how to write and submit an article |
| **An editor producing an issue** | `magazine-toolkit/docs/Editor_Guide.docx` + `magazine-toolkit/PRODUCTION_WORKFLOW.md` |
| **A developer working on the build pipeline** | `magazine-toolkit/docs/Architecture.md` |
| **Claude Code (AI-assisted development)** | `CLAUDE.md` — not needed for human onboarding, this one's written for the AI assistant |

## What's in this repo

- **`magazine-toolkit/`** — the active production system: author markdown →
  templated HTML → auto-paginated PDF. Everything for building an issue
  lives here. See `magazine-toolkit/README.md` for the full layout.
- **`Reference_docs/`** — the structural/brand-color validator for the
  legacy (pre-toolkit) HTML build process. Still enforced by a pre-commit
  hook on root-level `.html` files if any exist.
- **`CLAUDE.md`** — instructions for Claude Code, the AI assistant used to
  help build and maintain this repo. Skip this unless you're configuring
  or working alongside that assistant.

## Quick start

```bash
git clone https://github.com/gowrishankar005/van-valaroli.git
cd van-valaroli/magazine-toolkit
./setup.sh
```

Then see `magazine-toolkit/GETTING_STARTED.md` for the rest.
