#!/usr/bin/env python3
"""
build_text_pdf.py — Generate a text-based (searchable, selectable) PDF
using Playwright's page.pdf() — Chrome's native print engine.

Compared to image-based screenshots:
  • 5-10× smaller file (text instead of raster pixels)
  • Searchable + selectable text
  • Vector fonts: sharp at any zoom level
  • Accessible to screen readers
  • Builds in ~5 seconds vs ~20 for screenshots

Uses the same per-page zoom strategy as build_screenshot_pdf.py to make
sure each .page div renders within A4 bounds — Chrome's print engine
then breaks pages on the page-break-after rule.

Usage:
    python3 build_text_pdf.py <html_file> [output.pdf] [--theme NAME]
"""
import sys
import argparse
from pathlib import Path

from playwright.sync_api import sync_playwright


A4_W_MM = 210
A4_H_MM = 297


PRINT_CSS = """
    /* ─── PRINT CSS OVERRIDES ──────────────────────────────────────
       Chrome's print engine reads these via @media print + our @page
       declaration. Each .page div becomes one A4 PDF page via
       page-break-after: always. */
    @page {
        size: A4 portrait;
        margin: 0;
    }
    @media print {
        body {
            background: white !important;
            padding: 0 !important;
            margin: 0 !important;
        }
        #theme-picker, .glossy { display: none !important; }
        .cover, .page {
            width: 210mm !important;
            height: 297mm !important;
            min-height: 297mm !important;
            max-height: 297mm !important;
            margin: 0 !important;
            padding: 0 !important;
            overflow: hidden !important;
            page-break-after: always !important;
            break-after: page !important;
            page-break-inside: avoid !important;
            break-inside: avoid !important;
            box-shadow: none !important;
            border-radius: 0 !important;
            position: relative !important;
            display: flex !important;
            flex-direction: column !important;
        }
        /* Drop the screen-only cover-section wrapper background/padding */
        .cover-section {
            background: none !important;
            padding: 0 !important;
            margin: 0 !important;
            display: block !important;
            gap: 0 !important;
        }
    }
    /* Also apply non-@media versions so on-screen render matches what
       Chrome will print (helps the zoom-measurement step below). */
    body {
        background: white !important;
        padding: 0 !important;
        margin: 0 !important;
    }
    #theme-picker, .glossy { display: none !important; }
    .cover, .page {
        width: 210mm !important;
        height: 297mm !important;
        min-height: 297mm !important;
        max-height: 297mm !important;
        margin: 0 !important;
        overflow: hidden !important;
        box-shadow: none !important;
    }
"""


def build(html_file: Path, output_pdf: Path, theme: str = 'default') -> None:
    print("━" * 60)
    print("  வான் வளரொளி இதழ் — Text-based PDF Builder (Playwright)")
    print("━" * 60)
    print(f"  Input:  {html_file}")
    print(f"  Output: {output_pdf}")
    print(f"  Theme:  {theme}")
    print("━" * 60)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        # device_scale_factor only affects screen render, not PDF output
        ctx = browser.new_context(
            viewport={'width': 900, 'height': 1300},
            device_scale_factor=1,
        )
        page = ctx.new_page()

        page.goto(html_file.as_uri(), wait_until='networkidle')

        # Switch to print media BEFORE measuring anything. page.pdf() always
        # renders using @media print, regardless of this setting — but the
        # per-page zoom measurement below runs against the live page, which
        # defaults to screen media. Without this, the measurement sees a
        # slightly different CSS than what actually gets printed (the
        # @media print block below never applied during measurement), so a
        # page sitting just under the A4 threshold on screen could still
        # overflow — and clip into the footer — once actually printed.
        page.emulate_media(media='print')

        # Apply requested theme via the source's theme-picker mechanism
        if theme != 'default':
            page.evaluate(
                f"document.documentElement.setAttribute('data-theme', '{theme}')")
            print(f"\n  ✓ Theme set to: {theme}")

        # Inject print CSS overrides (forces each .page to A4 with overflow:hidden)
        page.add_style_tag(content=PRINT_CSS)

        # Wait for fonts (Noto Sans Tamil) and images — a not-yet-loaded
        # <img> under height:auto measures as 0-height, which would let an
        # image-heavy page slip past the overflow check below undetected.
        page.evaluate("document.fonts.ready")
        page.wait_for_function(
            "Array.from(document.images).every(img => img.complete)")
        page.wait_for_timeout(300)

        # PER-PAGE ZOOM: same logic as build_screenshot_pdf.py.
        # We measure each .page's NATURAL rendered height (would be taller
        # than A4 if content overflows the 297mm cap), then zoom .body-text
        # by the precise amount needed to bring the page down to A4.
        # NOTE: PRINT_CSS sets max-height/height/overflow with !important,
        # so a plain `p.style.maxHeight = 'none'` CANNOT override it — the
        # stylesheet !important always wins over a normal-priority inline
        # style. That silently capped every measurement at exactly 1123px
        # (i.e. "never overflowing"), so this safety net never actually
        # caught anything. Must use setProperty(..., 'important') to win.
        print("\n  Measuring overflow + applying per-page zoom…")
        page.evaluate("""
            () => {
                document.querySelectorAll('.cover, .page').forEach(p => {
                    p.style.setProperty('max-height', 'none', 'important');
                    p.style.setProperty('height', 'auto', 'important');
                    p.style.setProperty('overflow', 'visible', 'important');
                });
            }
        """)
        page.wait_for_timeout(150)

        A4_TOTAL_PX = 1123    # 297mm × 96/25.4
        A4_TARGET_PX = 1100   # ~2% safety margin — extra buffer against
                              # screen/print font-hinting rounding
        n_zoomed = page.evaluate(f"""
            () => {{
                let count = 0;
                document.querySelectorAll('.page').forEach(p => {{
                    const pageH = p.offsetHeight;
                    if (pageH <= {A4_TOTAL_PX}) return;
                    const bt = p.querySelector('.body-text');
                    if (!bt) return;
                    const btH = bt.offsetHeight;
                    const overshoot = pageH - {A4_TARGET_PX};
                    const newBtH = btH - overshoot;
                    if (newBtH <= 0) return;
                    const z = newBtH / btH;
                    bt.style.zoom = z.toFixed(4);
                    count++;
                }});
                return count;
            }}
        """)
        if n_zoomed:
            print(f"  ✓ Zoomed {n_zoomed} overfilled page(s) to fit A4")

        # Reapply the height cap so PDF respects page boundaries — same
        # setProperty(..., 'important') requirement as above, and overflow
        # must be explicitly put back to hidden since we forced it visible
        # for measurement (an inline !important otherwise keeps winning).
        page.evaluate("""
            () => {
                document.querySelectorAll('.cover, .page').forEach(p => {
                    p.style.setProperty('max-height', '297mm', 'important');
                    p.style.setProperty('height', '297mm', 'important');
                    p.style.setProperty('overflow', 'hidden', 'important');
                });
            }
        """)
        page.wait_for_timeout(200)

        # GENERATE PDF — Chrome's native print engine produces a text-based
        # PDF. Each .page div becomes one A4 PDF page via page-break-after.
        print("\n  Generating PDF via Chrome print engine…")
        page.pdf(
            path=str(output_pdf),
            format='A4',
            print_background=True,
            prefer_css_page_size=True,
            margin={'top': '0', 'bottom': '0', 'left': '0', 'right': '0'},
        )
        browser.close()

    size_mb = output_pdf.stat().st_size / (1024 * 1024)
    print(f"\n{'━'*60}")
    print(f"  ✓ Text-PDF: {output_pdf}")
    print(f"  ✓ Size: {size_mb:.1f} MB  (text searchable + selectable)")
    print(f"{'━'*60}\n")


def parse_args():
    ap = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=__doc__,
    )
    ap.add_argument('html_file', help='Input HTML file')
    ap.add_argument('output_pdf', nargs='?', default=None,
                    help='Output PDF (default: <html_basename>.pdf)')
    ap.add_argument('--theme', default='default',
                    choices=['default', 'peacock', 'blue', 'terracotta', 'saffron'])
    return ap.parse_args()


def main():
    args = parse_args()
    html_file = Path(args.html_file).absolute()
    if not html_file.exists():
        print(f"✗ Not found: {html_file}"); sys.exit(1)
    output_pdf = (Path(args.output_pdf).absolute()
                  if args.output_pdf
                  else html_file.with_suffix('.pdf'))
    build(html_file, output_pdf, theme=args.theme)


if __name__ == '__main__':
    main()
