#!/usr/bin/env python3
"""
build_screenshot_pdf.py — Render each .cover/.page div in the HTML as a
high-DPI PNG via headless Chromium (Playwright), then compile the PNGs
into a single A4 PDF.

Why this approach: each .page div in the source HTML is already designed
at exactly 210×297mm with the correct content. By taking element-level
screenshots, the PDF becomes a pixel-perfect flipbook of what the
browser renders — bypassing all of WeasyPrint's pagination quirks and
font-fallback issues.

Trade-off: text in the PDF is rasterized (not selectable). For a
print-targeted magazine, that's acceptable.

Usage:
    python3 build_screenshot_pdf.py <html_file> [output.pdf] [--dpi N]

Defaults:
    output.pdf = <html_basename>.pdf
    --dpi 192   (device_scale_factor=2; ~192 DPI; good for print)
    --dpi 288   would be ~300 DPI (excellent print, ~2× the file size)

Requires:
    pip install playwright img2pdf
    playwright install chromium
"""
import sys
import os
import argparse
from pathlib import Path

from playwright.sync_api import sync_playwright
import img2pdf
from PIL import Image


# A4 dimensions
A4_W_MM = 210
A4_H_MM = 297
CSS_DPI = 96            # browser's standard CSS pixel density


def css_px(mm: float) -> int:
    """Convert millimetres to CSS pixels at 96 DPI (browser default)."""
    return round(mm * CSS_DPI / 25.4)


def screenshot_pages(html_path: Path, tmp_dir: Path, scale: int,
                     theme: str = 'default') -> list[Path]:
    """Launch headless Chromium, screenshot each .cover/.page element.
    Returns list of PNG paths in document order."""
    a4_w = css_px(A4_W_MM)     # 794 px
    a4_h = css_px(A4_H_MM)     # 1123 px

    print(f"  Viewport:   {a4_w}×{a4_h} CSS px  (A4 at 96 DPI)")
    print(f"  Scale:      {scale}× device pixel ratio → ~{scale*96} DPI output")

    screenshots: list[Path] = []

    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(
            viewport={'width': a4_w + 40, 'height': a4_h + 40},
            device_scale_factor=scale,
        )
        page = context.new_page()

        # Navigate and wait for everything to render
        page.goto(html_path.as_uri(), wait_until='networkidle')

        # Apply requested theme by setting the HTML data-theme attribute
        # (matches the theme-picker mechanism in the source HTML)
        if theme != 'default':
            page.evaluate(
                f"document.documentElement.setAttribute('data-theme', '{theme}')")
            print(f"  Theme:      {theme}")

        # Hide screen-only UI and decorative overlays before screenshots.
        # NOTE: .glossy is a faux-paper sheen that looks fine on screen
        # but adds noise in print — strip it.
        page.add_style_tag(content="""
            #theme-picker { display: none !important; }
            .glossy { display: none !important; }
            /* Strip the screen background so .page boundaries are clean */
            body { background: white !important; }
            /* Force A4 width. Let pages grow taller than 297mm if content
               requires; we'll capture the full rendered box and let img2pdf
               scale it to fit A4 (so nothing is ever clipped). overflow is
               kept hidden so page-internal overflows don't visually leak,
               but the box itself can extend. */
            .cover, .page {
                width: 210mm !important;
                min-height: 297mm !important;
                max-height: none !important;
                height: auto !important;
                overflow: hidden !important;
                margin: 0 !important;
                box-shadow: none !important;
                border-radius: 0 !important;
                position: relative !important;
            }
            /* Stack pages with no gap so element screenshots align perfectly */
            .cover-section {
                padding: 0 !important;
                margin: 0 !important;
                background: white !important;
                gap: 0 !important;
            }
        """)

        # Wait for web fonts to finish loading (Noto Sans Tamil)
        page.evaluate("document.fonts.ready")
        # Tiny pause for any remaining paints to settle
        page.wait_for_timeout(300)

        # ─── PER-PAGE ZOOM TO FIT A4 ──────────────────────────────────
        # If the WHOLE .page renders taller than A4 (1123px @ 96 DPI),
        # the screenshot has off-A4 aspect, then normalise_to_a4 either
        # letterboxes (=> horizontal margins on PDF) or distorts text.
        # Both are bad.
        #
        # Previous logic zoomed only .body-text against a body-only budget,
        # which missed section-start pages where .section-header + dividers
        # add ~30-50mm OUTSIDE body-text — pushing the page total >297mm
        # even when body-text was within budget.
        #
        # Correct approach: measure TOTAL page height. If > 1123px, zoom
        # body-text by exactly the overshoot amount so the page lands at
        # ~1115px (a 1% safety margin under A4).
        A4_TOTAL_PX = 1123        # 297mm @ 96 DPI
        A4_TARGET_PX = 1115       # 1% under to absorb sub-pixel rounding
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
                    // body-text must shrink by `overshoot` px → new height
                    // = btH - overshoot. Zoom factor = newBtH / btH.
                    const newBtH = btH - overshoot;
                    if (newBtH <= 0) return;
                    const z = (newBtH / btH);
                    bt.style.zoom = z.toFixed(4);
                    count++;
                }});
                return count;
            }}
        """)
        if n_zoomed:
            print(f"  Zoomed:     {n_zoomed} overfilled page(s) "
                  f"to fit A4 total height")
        page.wait_for_timeout(200)  # let reflow settle

        # Collect every .cover and .page element in document order
        elements = page.locator('.cover, .page')
        count = elements.count()
        print(f"  Found:      {count} page element(s) in HTML\n")

        for i in range(count):
            el = elements.nth(i)
            out = tmp_dir / f"page_{i+1:03d}.png"
            # Element screenshot — captures only the bounding box of the element
            el.screenshot(path=str(out), animations='disabled')
            screenshots.append(out)
            print(f"    ✓ [{i+1:>2}/{count}] {out.name}  "
                  f"({out.stat().st_size // 1024} KB)")

        browser.close()

    return screenshots


def normalise_to_a4(png_paths: list[Path], target_w: int, target_h: int) -> None:
    """Resize every screenshot to exactly the same A4 pixel dimensions so
    img2pdf places them all identically on A4 PDF pages.

    Why this matters: Playwright captures each .page element at its
    NATURAL rendered size. Pages with more content render TALLER (e.g.
    2824×3994 px for a content-heavy page) than normal ones (1588×2246
    px). Even though both have A4 aspect ratio, img2pdf scales them
    independently using DPI metadata — leading to inconsistent visual
    sizing on the PDF pages (some content looks shrunk, some has visible
    margins from sub-pixel aspect rounding).

    By forcing every image to identical (target_w × target_h) we
    guarantee uniform PDF page layouts. Content-heavy pages are scaled
    down (their text becomes proportionally smaller — same outcome as
    browser print would produce); short pages are unchanged.

    We preserve aspect via LANCZOS resize when the source already has
    A4 aspect (≈ 0.707); pad with white otherwise to avoid distortion.
    """
    target_ratio = target_w / target_h
    for p in png_paths:
        with Image.open(p) as img:
            w, h = img.size
            if (w, h) == (target_w, target_h):
                continue

            actual_ratio = w / h
            # If aspect is already A4 (within 0.5%), pure resize is safe
            if abs(actual_ratio - target_ratio) / target_ratio < 0.005:
                resized = img.resize((target_w, target_h), Image.LANCZOS)
                resized.save(p, 'PNG', dpi=(192, 192))
                continue

            # Aspect off-A4: letterbox-pad first (no cropping), then resize
            if actual_ratio > target_ratio:
                new_h = round(w / target_ratio)
                canvas = Image.new('RGB', (w, new_h), 'white')
                canvas.paste(img, (0, (new_h - h) // 2))
            else:
                new_w = round(h * target_ratio)
                canvas = Image.new('RGB', (new_w, h), 'white')
                canvas.paste(img, ((new_w - w) // 2, 0))
            resized = canvas.resize((target_w, target_h), Image.LANCZOS)
            resized.save(p, 'PNG', dpi=(192, 192))


def assemble_pdf(png_paths: list[Path], output_pdf: Path) -> None:
    """Combine PNGs into a single A4 PDF using img2pdf.

    We force image size = page size = A4. This bypasses img2pdf's
    aspect-fit logic (which produced thin white borders when PNG
    aspect was a fraction off A4 due to sub-pixel rounding).
    """
    a4_w_pt = img2pdf.mm_to_pt(A4_W_MM)
    a4_h_pt = img2pdf.mm_to_pt(A4_H_MM)

    def force_a4_layout(imgwidthpx, imgheightpx, ndpi):
        # Return (pagewidth, pageheight, imgwidth, imgheight) all in pt.
        # Forcing img dims = page dims = A4 → image fills page exactly,
        # no margins, no letterbox.
        return a4_w_pt, a4_h_pt, a4_w_pt, a4_h_pt

    with open(output_pdf, 'wb') as f:
        f.write(img2pdf.convert(
            [str(p) for p in png_paths],
            layout_fun=force_a4_layout,
        ))


def build(html_file: Path, output_pdf: Path, dpi: int,
          theme: str = 'default') -> None:
    print("━" * 60)
    print("  வான் வளரொளி இதழ் — Screenshot-based PDF Builder")
    print("━" * 60)
    print(f"  Input:  {html_file}")
    print(f"  Output: {output_pdf}")
    print(f"  DPI:    {dpi}")
    print(f"  Theme:  {theme}")
    print("━" * 60)

    # device_scale_factor: 192 DPI → 2×, 288 DPI → 3×
    scale = max(1, round(dpi / 96))

    tmp_dir = Path('/tmp/van_screenshots')
    tmp_dir.mkdir(exist_ok=True)
    # Clean any prior run
    for old in tmp_dir.glob('page_*.png'):
        old.unlink()

    print("\n[1/3] Capturing screenshots with headless Chromium…")
    pngs = screenshot_pages(html_file, tmp_dir, scale, theme=theme)

    # Target uniform A4 dimensions: width 210mm at scale × 96 DPI.
    # All pages get resized to these exact dimensions for consistent
    # placement on A4 PDF pages.
    a4_w = css_px(A4_W_MM)            # 794
    a4_h = css_px(A4_H_MM)            # 1123
    target_w = a4_w * scale            # 1588 at scale=2
    target_h = a4_h * scale            # 2246 at scale=2
    print(f"\n[2/3] Resizing all screenshots to uniform {target_w}×{target_h} px "
          f"for consistent PDF layout…")
    normalise_to_a4(pngs, target_w, target_h)
    print(f"      Done.")

    print(f"\n[3/3] Assembling PDF…")
    assemble_pdf(pngs, output_pdf)

    size_mb = output_pdf.stat().st_size / (1024 * 1024)
    print(f"\n{'━'*60}")
    print(f"  ✓ PDF: {output_pdf}")
    print(f"  ✓ Size: {size_mb:.1f} MB  ({len(pngs)} pages)")
    print(f"{'━'*60}\n")

    # Leave the screenshots in /tmp for inspection; they're small.


def parse_args():
    ap = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=__doc__,
    )
    ap.add_argument('html_file', help='Input HTML file')
    ap.add_argument('output_pdf', nargs='?', default=None,
                    help='Output PDF path (default: <html_basename>.pdf)')
    ap.add_argument('--dpi', type=int, default=192,
                    help='Target DPI (default: 192 ≈ 2× retina; '
                         'use 288 for near-300 DPI print quality)')
    ap.add_argument('--theme', default='default',
                    choices=['default', 'peacock', 'blue', 'terracotta', 'saffron'],
                    help='Color theme: default (green), peacock (teal), '
                         'blue, terracotta, saffron (each maps to the HTML '
                         "theme-picker's data-theme value)")
    return ap.parse_args()


def main():
    args = parse_args()
    html_file = Path(args.html_file).absolute()
    if not html_file.exists():
        print(f"✗ Not found: {html_file}")
        sys.exit(1)
    output_pdf = (Path(args.output_pdf).absolute()
                  if args.output_pdf
                  else html_file.with_suffix('.pdf'))
    build(html_file, output_pdf, args.dpi, theme=args.theme)


if __name__ == '__main__':
    main()
