#!/usr/bin/env python3
"""
வான் வளரொளி இதழ் — PDF Build Script
Converts the self-contained HTML magazine into a print-ready PDF using WeasyPrint.

Usage:
    python3 build_magazine.py <html_file> <image_folder> [output.pdf]

Example:
    python3 build_magazine.py VAN_Vallaroli_Chittirai2026_v4_6_20260512.html Issue-01/ output.pdf
"""

import sys
import os
import re
import base64
import mimetypes
from pathlib import Path

# ─── Configuration ──────────────────────────────────────────────────────────

# Map of relative image paths in HTML → actual filenames in the image folder
# The HTML uses src="Images/filename" — we strip the "Images/" prefix to find the file
IMAGE_PREFIX = "Images/"

# MIME type lookup
MIME_MAP = {
    '.jpg':  'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.png':  'image/png',
    '.webp': 'image/webp',
    '.gif':  'image/gif',
    '.svg':  'image/svg+xml',
}

# WeasyPrint CSS — comprehensive layout fixes
# The HTML was built for browser @media print with fixed-height page divs + overflow:hidden.
# WeasyPrint handles pagination differently, so we:
# 1. Strip the @media print block (done in strip_print_media_rules())
# 2. Inject WeasyPrint-native rules below
WEASYPRINT_CSS = """
<style>
/* ══════════════════════════════════════════════════════════════
   WeasyPrint overrides — injected by build_magazine.py
   ══════════════════════════════════════════════════════════════ */

/* ── Fonts: use FreeSerif for Tamil (matches Claude Code builds) ── */
body, p, div, span, li, td, th, h1, h2, h3, h4, h5, h6,
.body-text, .content-area, .section-title, .article-title {
    font-family: 'FreeSerif', 'Noto Sans Tamil', serif !important;
}

/* ── Page setup ── */
@page {
    size: A4 portrait;
    margin: 0;
}

/* ── Root reset: strip screen-only flex/padding ── */
html { width: 210mm !important; }
body {
    background: none !important;
    padding: 0 !important;
    margin: 0 !important;
    display: block !important;
    width: 210mm !important;
    max-width: 210mm !important;
    overflow: hidden !important;
}

/* ── Cover section wrapper: strip screen chrome ── */
.cover-section {
    padding: 0 !important;
    background: none !important;
    display: block !important;
    width: 210mm !important;
}

/* ── Cover: FIXED height to preserve full layout ── */
.cover {
    width: 210mm !important;
    height: 297mm !important;
    min-height: unset !important;
    margin: 0 !important;
    box-shadow: none !important;
    border-radius: 0 !important;
    overflow: hidden !important;
    page-break-after: always !important;
    break-after: page !important;
    max-width: 210mm !important;
}

/* ── Content pages: AUTO height to prevent blank overflow pages ── */
.page {
    width: 210mm !important;
    height: auto !important;
    min-height: unset !important;
    max-height: none !important;
    margin: 0 !important;
    box-shadow: none !important;
    border-radius: 0 !important;
    overflow: visible !important;
    page-break-after: always !important;
    break-after: page !important;
    page-break-inside: auto !important;
    break-inside: auto !important;
    max-width: 210mm !important;
}

/* ── Glossy overlay: hide in print ── */
.glossy { display: none !important; }

/* ── Content area: let it flow naturally ── */
.content-area {
    overflow: visible !important;
    min-height: unset !important;
}

/* ── Header logos: consistent size ── */
.header-logo-left, .header-logo-right {
    height: 6mm !important;
    width: auto !important;
}

/* ── Images: prevent horizontal overflow ── */
img { max-width: 100% !important; }

/* ── Prevent border on consecutive pages ── */
.page + .page { border-top: none !important; }

/* ── Hide screen-only interactive elements ── */
#theme-picker { display: none !important; }
script { display: none !important; }

/* ── Orphan/widow control: keep titles with their content ── */
.section-title, .article-title, h2, h3, h4,
.subsection-heading, .kural-heading {
    page-break-after: avoid !important;
    break-after: avoid !important;
    orphans: 3;
    widows: 3;
}
p { orphans: 2; widows: 2; }

/* ── Footer separator line (was in stripped @media print) ── */
.page-footer {
    border-top: 1.5px solid var(--van-primary, #8DC63F) !important;
    margin-top: auto !important;
    padding-top: 2mm !important;
}

</style>
"""


def file_to_base64_uri(filepath):
    """Convert a file to a base64 data URI."""
    ext = Path(filepath).suffix.lower()
    mime = MIME_MAP.get(ext, 'application/octet-stream')
    with open(filepath, 'rb') as f:
        data = base64.b64encode(f.read()).decode('ascii')
    return f"data:{mime};base64,{data}"


def embed_images(html, image_folder):
    """Replace all src="Images/..." references with base64 data URIs."""
    image_folder = Path(image_folder)
    
    def replace_match(match):
        full_match = match.group(0)
        src_value = match.group(1)
        
        # Skip already-embedded base64 images
        if src_value.startswith('data:'):
            return full_match
        
        # Strip known path prefixes to get just the filename
        filename = src_value
        for prefix in ["Images/", "Content/Issue-01/"]:
            if filename.startswith(prefix):
                filename = filename[len(prefix):]
                break
        
        # Look for the file in the image folder
        filepath = image_folder / filename
        if filepath.exists():
            uri = file_to_base64_uri(str(filepath))
            print(f"  ✓ Embedded: {filename} ({filepath.stat().st_size // 1024}KB)")
            return f'src="{uri}"'
        else:
            print(f"  ✗ Not found: {filename} (looked in {image_folder})")
            return full_match
    
    # Match src="..." in img tags (both single and double quotes)
    pattern = r'src="([^"]+)"'
    result = re.sub(pattern, replace_match, html)
    return result


def remove_google_fonts_link(html):
    """Remove the Google Fonts <link> tag (WeasyPrint uses local fonts)."""
    pattern = r'<link[^>]*fonts\.googleapis\.com[^>]*>'
    return re.sub(pattern, '', html)


def strip_print_media_rules(html):
    """Remove the @media print { ... } block and existing @page rule.
    These conflict with WeasyPrint's rendering. Our injected CSS replaces them."""
    # Remove @media print { ... } block (handles nested braces)
    result = []
    i = 0
    in_media_print = False
    brace_depth = 0
    while i < len(html):
        # Detect start of @media print
        if not in_media_print and html[i:i+12] == '@media print':
            in_media_print = True
            # Find the opening brace
            j = html.index('{', i)
            brace_depth = 1
            i = j + 1
            continue
        if in_media_print:
            if html[i] == '{':
                brace_depth += 1
            elif html[i] == '}':
                brace_depth -= 1
                if brace_depth == 0:
                    in_media_print = False
                    i += 1
                    continue
            i += 1
            continue
        result.append(html[i])
        i += 1
    html = ''.join(result)
    # Remove standalone @page { ... } rules (outside @media blocks)
    html = re.sub(r'@page\s*\{[^}]*\}', '', html)
    return html


def inject_weasyprint_css(html):
    """Inject WeasyPrint-specific CSS before </head>."""
    return html.replace('</head>', WEASYPRINT_CSS + '\n</head>')


def build_pdf(html_file, image_folder, output_pdf):
    """Main build pipeline."""
    print(f"\n{'='*60}")
    print(f"  வான் வளரொளி இதழ் — PDF Builder")
    print(f"{'='*60}")
    print(f"  HTML:   {html_file}")
    print(f"  Images: {image_folder}")
    print(f"  Output: {output_pdf}")
    print(f"{'='*60}\n")
    
    # Step 1: Read HTML
    print("[1/5] Reading HTML file...")
    with open(html_file, 'r', encoding='utf-8') as f:
        html = f.read()
    print(f"  Read {len(html):,} bytes ({html.count(chr(10)):,} lines)")
    
    # Step 2: Remove Google Fonts link
    print("\n[2/6] Removing Google Fonts link (using local fonts)...")
    html = remove_google_fonts_link(html)
    
    # Step 3: Strip conflicting @media print rules
    print("\n[3/6] Stripping browser @media print rules (replaced by WeasyPrint CSS)...")
    html = strip_print_media_rules(html)
    
    # Step 4: Embed images
    print("\n[4/6] Embedding images as base64...")
    html = embed_images(html, image_folder)
    
    # Step 5: Inject WeasyPrint CSS
    print("\n[5/6] Injecting WeasyPrint layout & font rules...")
    html = inject_weasyprint_css(html)
    
    # Step 6: Generate PDF
    print("\n[6/6] Generating PDF with WeasyPrint...")
    print("  (This may take a minute for a large magazine...)")
    
    from weasyprint import HTML
    doc = HTML(string=html, base_url=str(Path(html_file).parent))
    doc.write_pdf(output_pdf)
    
    size_mb = os.path.getsize(output_pdf) / (1024 * 1024)
    print(f"\n{'='*60}")
    print(f"  ✓ PDF generated: {output_pdf}")
    print(f"  ✓ Size: {size_mb:.1f} MB")
    print(f"{'='*60}\n")


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    
    html_file = sys.argv[1]
    image_folder = sys.argv[2]
    output_pdf = sys.argv[3] if len(sys.argv) > 3 else 'VAN_Vallaroli_output.pdf'
    
    build_pdf(html_file, image_folder, output_pdf)
