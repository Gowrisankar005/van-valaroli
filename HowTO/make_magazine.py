#!/usr/bin/env python3
"""
make_magazine.py — Magazine production pipeline (one command).

Two input modes:

  (A) FROM AUTHOR CONTENT (recommended for new issues):
      python make_magazine.py --from-issue issues/Issue-02 output/Vaigasi2026.pdf

      Reads issues/Issue-02/{issue_meta.json, articles/*.md, images/*}
      Runs Step 0 (build_issue_html) + Steps 1-4.

  (B) FROM EXISTING HTML (for re-publishing or one-off tweaks):
      python make_magazine.py --from-html source/foo.html output/foo.pdf

      Skips Step 0, uses your HTML as-is. Runs Steps 1-4.

Pipeline steps:
  0. build_issue_html.py     (only in mode A) — markdown → base HTML
  1. fix_html.py             — corrections, CSS, image grids, corners
  2. rebalance_sections.py   — page count + content distribution + TOC
  3. compare_html.py         — integrity audit (optional, --skip-audit)
  4. build_text_pdf.py       — searchable PDF (or build_screenshot_pdf for image-PDF)

Options:
  --theme {default|peacock|blue|terracotta|saffron}
  --format {text|image}       text-PDF (default) or image-PDF
  --dpi N                     image-PDF only
  --skip-audit                skip integrity check
  --keep-intermediates        keep step0/step1/step2 HTML files
"""
import argparse
import subprocess
import sys
import time
from pathlib import Path


HERE = Path(__file__).parent.resolve()
VENV_PY = HERE / '.venv' / 'bin' / 'python'


def run(cmd: list, step_name: str, check: bool = True) -> int:
    print(f"\n╭─ {step_name}")
    print(f"│  $ {' '.join(str(c) for c in cmd[1:])}")
    print(f"╰─")
    t0 = time.time()
    result = subprocess.run(cmd, cwd=HERE)
    elapsed = time.time() - t0
    status = '✓' if result.returncode == 0 else '✗'
    print(f"   {status} {step_name} ({elapsed:.1f}s)")
    if check and result.returncode != 0:
        print(f"\n  Pipeline stopped at: {step_name}")
        sys.exit(result.returncode)
    return result.returncode


def parse_args():
    ap = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=__doc__,
    )
    grp = ap.add_mutually_exclusive_group(required=True)
    grp.add_argument('--from-issue', metavar='ISSUE_DIR',
                     help='Folder containing issue_meta.json + articles/*.md + images/')
    grp.add_argument('--from-html', metavar='HTML_FILE',
                     help='Pre-built base HTML (skips Step 0)')

    ap.add_argument('output_pdf', help='Output PDF path')

    ap.add_argument('--theme', default='default',
                    choices=['default', 'peacock', 'blue', 'terracotta', 'saffron'],
                    help='Color theme (default: green)')
    ap.add_argument('--format', default='text', choices=['text', 'image'],
                    help='text-PDF (default) or image-PDF')
    ap.add_argument('--dpi', type=int, default=192,
                    help='image-PDF only (default 192)')
    ap.add_argument('--skip-audit', action='store_true')
    ap.add_argument('--keep-intermediates', action='store_true')
    return ap.parse_args()


def main():
    args = parse_args()
    output_pdf = Path(args.output_pdf).resolve()
    src_dir = HERE / 'source'
    src_dir.mkdir(exist_ok=True)

    print("=" * 64)
    print("  வான் வளரொளி இதழ் — Magazine Production Pipeline")
    print("=" * 64)
    print(f"  Output:   {output_pdf}")
    print(f"  Theme:    {args.theme}")
    print(f"  Format:   {args.format}-PDF")
    print("=" * 64)

    t_start = time.time()

    # ─── STEP 0 (mode A): build base HTML from author articles ──────────
    if args.from_issue:
        issue_dir = Path(args.from_issue).resolve()
        if not issue_dir.is_dir():
            print(f"✗ Issue folder not found: {issue_dir}")
            sys.exit(1)
        # Output base HTML to source/<issue>_base.html
        base_html = src_dir / f"{issue_dir.name}_base.html"
        run([str(VENV_PY), str(HERE / 'build_issue_html.py'),
             str(issue_dir), str(base_html)],
            "Step 0/4  build_issue_html.py  (author markdown → base HTML)")
        input_html = base_html
    else:
        input_html = Path(args.from_html).resolve()
        if not input_html.exists():
            print(f"✗ Input HTML not found: {input_html}")
            sys.exit(1)

    # Intermediates live alongside source HTML (so Images/ paths resolve).
    base_dir = input_html.parent
    step1 = base_dir / '_pipeline_step1.html'
    step2 = base_dir / '_pipeline_step2.html'

    # ─── STEP 1: fix_html.py ───────────────────────────────────────────
    run([str(VENV_PY), str(HERE / 'fix_html.py'),
         str(input_html), str(step1)],
        "Step 1/4  fix_html.py  (paths, subheads, image grids, CSS, corners)")

    # ─── STEP 2: rebalance_sections.py ─────────────────────────────────
    run([str(VENV_PY), str(HERE / 'rebalance_sections.py'),
         str(step1), str(step2)],
        "Step 2/4  rebalance_sections.py  (page count, content distribution, TOC)")

    # ─── STEP 3: compare_html.py ───────────────────────────────────────
    if not args.skip_audit:
        run([str(VENV_PY), str(HERE / 'compare_html.py'),
             str(input_html), str(step2)],
            "Step 3/4  compare_html.py  (integrity audit)",
            check=False)
    else:
        print("\n   ⏩ Step 3/4 skipped (--skip-audit)")

    # ─── STEP 4: build PDF ─────────────────────────────────────────────
    if args.format == 'text':
        run([str(VENV_PY), str(HERE / 'build_text_pdf.py'),
             str(step2), str(output_pdf), '--theme', args.theme],
            "Step 4/4  build_text_pdf.py  (Playwright → searchable PDF)")
    else:
        run([str(VENV_PY), str(HERE / 'build_screenshot_pdf.py'),
             str(step2), str(output_pdf),
             '--theme', args.theme, '--dpi', str(args.dpi)],
            f"Step 4/4  build_screenshot_pdf.py  (image PDF @ {args.dpi} DPI)")

    # ─── Cleanup ───────────────────────────────────────────────────────
    if not args.keep_intermediates:
        for p in (step1, step2):
            if p.exists():
                p.unlink()
        # Keep the base HTML if from-issue (it represents the issue)

    elapsed = time.time() - t_start
    size_mb = output_pdf.stat().st_size / (1024 * 1024)

    print()
    print("=" * 64)
    print(f"  ✓ Done in {elapsed:.1f}s")
    print(f"  ✓ Output: {output_pdf}")
    print(f"  ✓ Size:   {size_mb:.1f} MB")
    print("=" * 64)


if __name__ == '__main__':
    main()
