#!/usr/bin/env python3
"""
make_magazine.py — One-command magazine production pipeline.

Runs the full sequence:
  1. fix_html.py            — paths, subheads, captions, image grids, CSS
  2. rebalance_sections.py  — per-section page count + content distribution + TOC
  3. compare_html.py        — integrity audit (optional, --skip-audit to omit)
  4. build_*_pdf.py         — text-PDF (default) or image-PDF

Usage:
    python3 make_magazine.py <input.html> [output.pdf] [options]

Examples:
    # Default: text-PDF, green theme
    python3 make_magazine.py source.html magazine.pdf

    # Peacock theme
    python3 make_magazine.py source.html magazine.pdf --theme peacock

    # Image-PDF (pixel-perfect, larger file)
    python3 make_magazine.py source.html magazine.pdf --format image

    # Skip audit, keep intermediate files for inspection
    python3 make_magazine.py source.html --skip-audit --keep-intermediates

Output:
    magazine.pdf  (text-PDF default, ~15-20 MB, searchable + selectable)
"""
import argparse
import shutil
import subprocess
import sys
import time
from pathlib import Path


HERE = Path(__file__).parent.resolve()
VENV_PY = HERE / '.venv' / 'bin' / 'python'


def run(cmd: list[str], step_name: str, check: bool = True) -> int:
    """Run a subprocess command, print friendly status."""
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
    ap.add_argument('input_html', help='Source HTML (e.g. v4_6 base file)')
    ap.add_argument('output_pdf', nargs='?', default=None,
                    help='Output PDF path (default: <input>.pdf)')
    ap.add_argument('--theme', default='default',
                    choices=['default', 'peacock', 'blue', 'terracotta', 'saffron'],
                    help='Color theme (default: default/green)')
    ap.add_argument('--format', default='text', choices=['text', 'image'],
                    help='text=searchable PDF (default), image=pixel snapshot PDF')
    ap.add_argument('--dpi', type=int, default=192,
                    help='Only for --format image; default 192 (≈2× retina)')
    ap.add_argument('--skip-audit', action='store_true',
                    help='Skip compare_html.py integrity check')
    ap.add_argument('--keep-intermediates', action='store_true',
                    help='Keep step1/step2 HTML for inspection')
    return ap.parse_args()


def main():
    args = parse_args()
    input_html = Path(args.input_html).resolve()
    if not input_html.exists():
        print(f"✗ Input not found: {input_html}")
        sys.exit(1)

    output_pdf = (Path(args.output_pdf).resolve()
                  if args.output_pdf
                  else input_html.with_suffix('.pdf'))

    # Intermediate paths (in HERE so scripts find them via relative path)
    step1 = HERE / 'step1.html'
    step2 = HERE / 'step2.html'

    print("=" * 64)
    print("  வான் வளரொளி இதழ் — Magazine Production Pipeline")
    print("=" * 64)
    print(f"  Input:    {input_html}")
    print(f"  Output:   {output_pdf}")
    print(f"  Theme:    {args.theme}")
    print(f"  Format:   {args.format}-PDF")
    print("=" * 64)

    t_start = time.time()

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
        # Audit may have non-zero exit on intentional diffs; don't stop pipeline
        run([str(VENV_PY), str(HERE / 'compare_html.py'),
             str(input_html), str(step2)],
            "Step 3/4  compare_html.py  (integrity audit)",
            check=False)
    else:
        print("\n   ⏩ Step 3/4 skipped (--skip-audit)")

    # ─── STEP 4: build_*_pdf.py ────────────────────────────────────────
    if args.format == 'text':
        run([str(VENV_PY), str(HERE / 'build_text_pdf.py'),
             str(step2), str(output_pdf), '--theme', args.theme],
            "Step 4/4  build_text_pdf.py  (Playwright print → searchable PDF)")
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
