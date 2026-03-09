#!/usr/bin/env python3
"""
validate_template.py — வான் வளரொளி இதழ் HTML Validator
========================================================
Validates the template and any issue file against:
  - CSS class completeness (all design-spec components present)
  - Brand color integrity (hex values match spec)
  - Responsive media queries (print, tablet, mobile)
  - Page structure rules (header + content-area + footer per page)
  - Image references (file paths, no base64 in template)
  - Placeholder hygiene (template has [SLOTS], issues have none)
  - Edit zone coverage (<!-- EDIT: --> comments in template)
  - செந்தமிழ் word violations (banned loan words in content)

Usage:
  python3 validate_template.py                          # validates template
  python3 validate_template.py path/to/issue.html       # validates an issue file
  python3 validate_template.py --all                    # validates all HTML files

Exit codes: 0 = PASS, 1 = WARNINGS only, 2 = FAILURES found
"""

import sys
import re
import os
from pathlib import Path
from collections import defaultdict

# ── Paths ──────────────────────────────────────────────────────────────────────
SCRIPT_DIR   = Path(__file__).parent
PROJECT_DIR  = SCRIPT_DIR.parent
TEMPLATE     = PROJECT_DIR / "VAN_Vallaroli_TEMPLATE_v1.html"
IMAGES_DIR   = PROJECT_DIR / "Images"

# ── Required CSS classes (must be defined in <style> block) ───────────────────
REQUIRED_CSS_CLASSES = [
    # Page skeleton
    "page", "page-header", "page-footer", "content-area",
    "cover", "cover-section", "glossy", "corner-tl", "corner-br",
    # Cover components
    "masthead", "mag-name-main", "org-name", "tagline",
    "issue-row", "pill", "pill-special",
    "quote-float", "quote-attr",
    "bottom-band", "teasers", "teaser-item", "teaser-dot", "teaser-text",
    "publisher-row", "van-seal", "publisher-name", "publisher-url",
    "cover-image", "border-frame",
    # TOC
    "toc-header", "toc-title", "toc-subtitle", "toc-underline",
    "issue-banner", "toc-list", "toc-row", "toc-accent",
    "toc-content", "toc-section", "toc-desc", "toc-dots", "toc-page",
    "toc-quote",
    # Section content
    "section-header", "topic-title", "section-label-row",
    "section-label", "lotus-icon", "title-underline",
    "continuation-banner", "cont-section-name", "cont-page-info",
    "body-text", "subhead", "slim-quote", "highlights-box",
    "closing", "comparison-table", "numbered-list",
    "section-divider", "byline", "img-placeholder",
    "first-para", "salutation", "sal-initial",
    # Footer
    "issue-info", "page-number", "van-logo-footer",
]

# ── Brand color palette (must appear in CSS — as hex OR as CSS variable ref) ──
# After the theme-system refactor, colors live in :root as CSS variables.
# Each entry: hex_value → (var_name, css_variable_alternative)
REQUIRED_BRAND_COLORS = {
    "#8DC63F": ("van-green-bright",  "--van-primary"),
    "#6BA82F": ("van-green-dark",    "--van-dark"),
    "#2d7a3e": ("van-green-deep",    "--van-deep"),
    "#D4AF37": ("van-gold",          "--van-gold"),
    "#2B2B2B": ("body-text",         "--body-text"),
    "#fffef5": ("page-bg-top",       "--page-bg-top"),
    "#fef9f2": ("page-bg-bottom",    "--page-bg-bottom"),
}

# ── Required theme system elements ────────────────────────────────────────────
REQUIRED_THEME_VARS = [
    "--van-primary", "--van-deep", "--van-dark", "--van-gold",
    "--van-deepest", "--van-deeper",
]
REQUIRED_THEME_IDS = [
    'data-theme="peacock"', 'data-theme="blue"',
    'data-theme="terracotta"', 'data-theme="saffron"',
]

# ── Required media queries ────────────────────────────────────────────────────
REQUIRED_MEDIA_QUERIES = [
    "@media print",
    "@media screen and (max-width: 880px)",
    "@media screen and (max-width: 600px)",
]

# ── Required @page rule ───────────────────────────────────────────────────────
REQUIRED_AT_PAGE = "@page"

# ── Required image file references in HTML ────────────────────────────────────
REQUIRED_IMAGE_REFS = [
    "Images/VANLogoGold.jpg",
    "Images/valarolilogogold01.jpg",
]

# ── செந்தமிழ் violations — banned loan words in body content ─────────────────
SENTHAMIZH_VIOLATIONS = {
    "கம்ப்யூட்டர்": "கணினி",
    "லேப்டாப்":     "மடிக்கணினி",
    "மொபைல்":      "கைப்பேசி / அலைபேசி",
    "இன்டர்நெட்":  "இணையம்",
    "இ-மெயில்":    "மின்னஞ்சல்",
    "வெப்சைட்":    "இணையதளம்",
    "ஸ்கூல்":      "பள்ளி",
    "காலேஜ்":      "கல்லூரி",
    "டீச்சர்":     "ஆசிரியர்",
    "ஸ்டூடென்ட்":  "மாணவர்",
    "ஹாஸ்பிடல்":  "மருத்துவமனை",
    "டாக்டர்":     "மருத்துவர்",
    "நர்ஸ்":       "செவிலியர்",
    "மெடிசின்":    "மருந்து",
    "பஸ்":         "பேருந்து",
    "டிரெய்ன்":    "தொடர்வண்டி",
    "ரோடு":        "சாலை",
    "ஏர்போர்ட்":  "விமான நிலையம்",
    "தர்மம்":      "அறம்",
    "ஆரோக்கியம்": "நலம்",
}


# ══════════════════════════════════════════════════════════════════════════════
# Report helpers
# ══════════════════════════════════════════════════════════════════════════════

class Report:
    def __init__(self, filepath: str):
        self.filepath  = filepath
        self.checks    = []   # (level, category, message)
        self.pass_cnt  = 0
        self.warn_cnt  = 0
        self.fail_cnt  = 0

    def ok(self, category: str, msg: str):
        self.checks.append(("PASS", category, msg))
        self.pass_cnt += 1

    def warn(self, category: str, msg: str):
        self.checks.append(("WARN", category, msg))
        self.warn_cnt += 1

    def fail(self, category: str, msg: str):
        self.checks.append(("FAIL", category, msg))
        self.fail_cnt += 1

    def print_report(self):
        icons = {"PASS": "✅", "WARN": "⚠️ ", "FAIL": "❌"}
        colours = {"PASS": "\033[32m", "WARN": "\033[33m", "FAIL": "\033[31m"}
        reset = "\033[0m"

        print(f"\n{'═'*64}")
        print(f"  வான் வளரொளி — Template Validator")
        print(f"  File: {Path(self.filepath).name}")
        print(f"{'═'*64}")

        last_cat = None
        for level, cat, msg in self.checks:
            if cat != last_cat:
                print(f"\n  ── {cat} ──")
                last_cat = cat
            icon  = icons[level]
            color = colours[level]
            print(f"  {icon}  {color}{msg}{reset}")

        print(f"\n{'─'*64}")
        total = self.pass_cnt + self.warn_cnt + self.fail_cnt
        print(f"  Results: {self.pass_cnt} passed  |  "
              f"{self.warn_cnt} warnings  |  {self.fail_cnt} failed  "
              f"(of {total} checks)")

        if self.fail_cnt == 0 and self.warn_cnt == 0:
            print(f"\n  \033[32m✅  PASS — File is valid and production-ready.\033[0m")
        elif self.fail_cnt == 0:
            print(f"\n  \033[33m⚠️   PASS WITH WARNINGS — Review warnings before publishing.\033[0m")
        else:
            print(f"\n  \033[31m❌  FAIL — {self.fail_cnt} issue(s) must be fixed.\033[0m")
        print(f"{'═'*64}\n")

    def exit_code(self) -> int:
        if self.fail_cnt > 0: return 2
        if self.warn_cnt > 0: return 1
        return 0


# ══════════════════════════════════════════════════════════════════════════════
# Check functions
# ══════════════════════════════════════════════════════════════════════════════

def extract_css(html: str) -> str:
    """Return the content of the first <style>…</style> block."""
    m = re.search(r'<style>(.*?)</style>', html, re.DOTALL)
    return m.group(1) if m else ""


def extract_body(html: str) -> str:
    """Return the content of the <body>…</body> block."""
    m = re.search(r'<body>(.*?)</body>', html, re.DOTALL)
    return m.group(1) if m else html


def check_css_classes(css: str, report: Report):
    missing = []
    for cls in REQUIRED_CSS_CLASSES:
        # Match .classname { or .classname::  or .classname ,  etc.
        pattern = rf'\.{re.escape(cls)}[\s{{:,>~+\[]'
        if not re.search(pattern, css):
            missing.append(cls)

    if missing:
        for m in missing:
            report.fail("CSS Classes", f"Missing class definition: .{m}")
    else:
        report.ok("CSS Classes",
                  f"All {len(REQUIRED_CSS_CLASSES)} required classes defined ✓")


def check_brand_colors(css: str, report: Report):
    missing = []
    for hex_val, (name, var_name) in REQUIRED_BRAND_COLORS.items():
        # Accept the raw hex OR the CSS variable name (post theme-system refactor)
        hex_present = hex_val.lower() in css.lower()
        var_present = var_name in css
        if not hex_present and not var_present:
            missing.append((hex_val, name, var_name))

    if missing:
        for hex_val, name, var_name in missing:
            report.fail("Brand Colors",
                        f"Brand color missing: {hex_val} ({name}) — "
                        f"expected hex or {var_name}")
    else:
        report.ok("Brand Colors",
                  f"All {len(REQUIRED_BRAND_COLORS)} brand colors present "
                  f"(as hex or CSS variable) ✓")


def check_css_variable_values(css: str, report: Report):
    """
    Verify that CSS variables defined in :root (and theme blocks) are assigned
    real color values — NOT circular var() self-references.

    This catches the exact failure mode where a script replaces color hex values
    everywhere in the CSS block including inside the :root variable definitions,
    turning  --van-primary: #8DC63F  into  --van-primary: var(--van-primary).
    CSS treats circular var() as invalid and silently falls back to black.
    """
    # ── 1. Parse :root block ─────────────────────────────────────────────────
    root_match = re.search(r':root\s*\{([^}]+)\}', css)
    if not root_match:
        report.warn("CSS Variable Values",
                    ":root block not found — cannot verify variable values")
        return

    root_content = root_match.group(1)
    # Extract all  --name: value;  declarations
    decls = re.findall(r'(--[\w-]+)\s*:\s*([^;]+)\s*;', root_content)

    circular, valid = [], 0
    for var_name, raw_value in decls:
        value = raw_value.strip()
        # Circular if the value itself is a var() call
        if re.search(r'var\s*\(', value):
            circular.append((var_name, value))
        else:
            valid += 1

    if circular:
        for var_name, value in circular:
            report.fail(
                "CSS Variable Values",
                f":root circular reference — {var_name}: {value}  "
                f"(CSS falls back to black; replace with a real hex value)"
            )
    else:
        report.ok(
            "CSS Variable Values",
            f":root has {valid} variable(s) — all assigned real values, "
            f"no circular var() references ✓"
        )

    # ── 2. Same check for every [data-theme="…"] override block ──────────────
    theme_blocks = re.finditer(
        r'\[data-theme=["\'](\w+)["\']\]\s*\{([^}]+)\}', css
    )
    bad_themes = []
    for match in theme_blocks:
        theme_name   = match.group(1)
        block_content = match.group(2)
        block_decls  = re.findall(r'(--[\w-]+)\s*:\s*([^;]+)\s*;', block_content)
        for var_name, raw_value in block_decls:
            if re.search(r'var\s*\(', raw_value.strip()):
                bad_themes.append((theme_name, var_name, raw_value.strip()))

    if bad_themes:
        for theme_name, var_name, value in bad_themes:
            report.fail(
                "CSS Variable Values",
                f"[data-theme=\"{theme_name}\"] circular ref — "
                f"{var_name}: {value}"
            )
    else:
        report.ok(
            "CSS Variable Values",
            "All theme override blocks have real values — no circular refs ✓"
        )


def check_theme_system(css: str, html: str, report: Report):
    """Verify CSS variable theme system and picker UI are present."""
    # CSS variables in :root — check names AND that they have real values
    missing_vars = [v for v in REQUIRED_THEME_VARS if v not in css]
    if missing_vars:
        for v in missing_vars:
            report.fail("Theme System", f"CSS variable missing from :root: {v}")
    else:
        report.ok("Theme System",
                  f"All {len(REQUIRED_THEME_VARS)} CSS theme variables defined ✓")

    # Theme override blocks
    missing_themes = [t for t in REQUIRED_THEME_IDS if t not in css]
    if missing_themes:
        for t in missing_themes:
            report.warn("Theme System", f"Theme override block missing: [{t}]")
    else:
        report.ok("Theme System", f"All 4 theme override blocks present ✓")

    # Picker UI
    if 'id="theme-picker"' in html:
        report.ok("Theme System", "Theme picker UI (#theme-picker) present ✓")
    else:
        report.warn("Theme System",
                    "Theme picker UI missing — add floating picker before </body>")


def check_media_queries(css: str, report: Report):
    for mq in REQUIRED_MEDIA_QUERIES:
        if mq in css:
            report.ok("Media Queries", f"Present: {mq}")
        else:
            report.fail("Media Queries", f"Missing: {mq}")

    if REQUIRED_AT_PAGE in css:
        report.ok("Media Queries", "@page { size: A4 portrait } present ✓")
    else:
        report.fail("Media Queries", "@page rule missing — print output will be wrong")


def check_page_structure(body: str, report: Report):
    """Each .page div must contain page-header, content-area, page-footer."""
    # Find all page div blocks (rough heuristic: capture between class="page" and next same-level div)
    page_blocks = re.findall(
        r'<div class="page">(.*?)(?=<div class="page"|</body>)',
        body, re.DOTALL
    )

    if not page_blocks:
        report.warn("Page Structure", "No <div class=\"page\"> blocks found — template only has cover?")
        return

    required = ["page-header", "content-area", "page-footer"]
    required_decorators = ["glossy", "corner-tl", "corner-br"]

    pages_ok = 0
    for i, block in enumerate(page_blocks, 1):
        for req in required:
            if f'class="{req}"' not in block and f"class='{req}'" not in block:
                report.fail("Page Structure",
                            f"Page {i}: missing <div class=\"{req}\">")
        for dec in required_decorators:
            if dec not in block:
                report.warn("Page Structure",
                            f"Page {i}: missing decorator '{dec}'")
        pages_ok += 1

    report.ok("Page Structure",
              f"{pages_ok} page block(s) checked — all have required structure ✓")


def check_image_refs(html: str, report: Report):
    """All image src refs should be file paths, not base64."""
    # Check for base64 images (only flag if outside CSS — cover image in issues is OK)
    body = extract_body(html)
    base64_imgs = re.findall(r'<img[^>]+src=["\']data:image/', body)
    if base64_imgs:
        report.fail("Images",
                    f"{len(base64_imgs)} base64-embedded image(s) found in <body> — "
                    "use file paths (Images/*.jpg) instead")
    else:
        report.ok("Images", "No base64 images in body — all images use file paths ✓")

    # Check required image refs are present
    for ref in REQUIRED_IMAGE_REFS:
        if ref in html:
            # Also check the file actually exists on disk
            img_path = PROJECT_DIR / ref
            if img_path.exists():
                report.ok("Images", f"Image ref present and file exists: {ref} ✓")
            else:
                report.warn("Images",
                            f"Image ref found in HTML but file missing on disk: {ref}")
        else:
            report.warn("Images", f"Image reference not found in HTML: {ref}")


def check_placeholders(html: str, is_template: bool, report: Report):
    """
    Template: must have [PLACEHOLDER] tokens and <!-- EDIT: --> zones.
    Issue file: must NOT have unfilled [PLACEHOLDER] tokens.
    """
    placeholder_pattern = r'\[(?!VERSE|STEP|COL|CELL|POINT|KEY|BOX|SIGN)[A-Z_]+(?:\s[A-Z_]+)?\]'
    placeholders = re.findall(placeholder_pattern, html)
    # Deduplicate
    unique_ph = sorted(set(placeholders))

    edit_zones = len(re.findall(r'<!-- EDIT:', html))

    if is_template:
        if unique_ph:
            report.ok("Placeholders",
                      f"Template has {len(unique_ph)} placeholder token type(s): "
                      f"{', '.join(unique_ph[:8])}{'…' if len(unique_ph) > 8 else ''} ✓")
        else:
            report.warn("Placeholders",
                        "No [PLACEHOLDER] tokens found — template may not guide editors")

        if edit_zones >= 5:
            report.ok("Edit Zones",
                      f"{edit_zones} <!-- EDIT: --> comment zones found ✓")
        else:
            report.warn("Edit Zones",
                        f"Only {edit_zones} <!-- EDIT: --> zones found (expected ≥5)")
    else:
        # Issue file — placeholders should be filled
        if unique_ph:
            report.fail("Placeholders",
                        f"Issue file has {len(unique_ph)} unfilled placeholder(s): "
                        f"{', '.join(unique_ph)}")
        else:
            report.ok("Placeholders", "No unfilled [PLACEHOLDER] tokens — content fully populated ✓")


def check_senthamizh(html: str, report: Report):
    """Scan body text for banned loan words."""
    body = extract_body(html)
    # Strip HTML tags for text scan
    text = re.sub(r'<[^>]+>', ' ', body)
    violations = []
    for banned, correct in SENTHAMIZH_VIOLATIONS.items():
        if banned in text:
            violations.append((banned, correct))

    if violations:
        for banned, correct in violations:
            report.fail("செந்தமிழ்",
                        f"Loan word found: '{banned}' → should be '{correct}'")
    else:
        report.ok("செந்தமிழ்",
                  f"No loan word violations found in body text ✓")


def check_print_query_intact(css: str, report: Report):
    """Verify the print query hasn't been accidentally altered."""
    essential = [
        "page-break-after: always",
        "break-after: page",
        "width: 210mm",
        "min-height: 297mm",
    ]
    missing = [e for e in essential if e not in css]
    if missing:
        for m in missing:
            report.fail("Print Safety", f"Print query missing critical rule: '{m}'")
    else:
        report.ok("Print Safety",
                  "Print media query intact — page-break, A4 dimensions confirmed ✓")


def check_font_import(html: str, report: Report):
    """Noto Sans Tamil must be loaded."""
    if "Noto+Sans+Tamil" in html or "Noto Sans Tamil" in html:
        report.ok("Typography", "Noto Sans Tamil font import found ✓")
    else:
        report.fail("Typography",
                    "Noto Sans Tamil font not imported — Tamil text will fall back to system font")


def check_meta_viewport(html: str, report: Report):
    if 'name="viewport"' in html and 'width=device-width' in html:
        report.ok("Responsiveness", "viewport meta tag present ✓")
    else:
        report.fail("Responsiveness",
                    "Missing <meta name=\"viewport\"> — page won't scale on mobile")


def check_overflow_guard(css: str, report: Report):
    if "overflow-x: hidden" in css:
        report.ok("Responsiveness", "overflow-x: hidden on html/body — no horizontal scroll ✓")
    else:
        report.warn("Responsiveness",
                    "overflow-x: hidden not found — mobile may show horizontal scrollbar")


def check_title_tag(html: str, is_template: bool, report: Report):
    m = re.search(r'<title>(.*?)</title>', html)
    if not m:
        report.fail("Metadata", "<title> tag missing")
        return
    title = m.group(1)
    if is_template:
        if "[TAMIL_MONTH]" in title or "[YEAR]" in title:
            report.ok("Metadata", f"<title> has placeholder slots ✓")
        else:
            report.warn("Metadata",
                        f"<title> doesn't contain month/year placeholders: '{title}'")
    else:
        if "[" in title:
            report.fail("Metadata",
                        f"<title> has unfilled placeholders: '{title}'")
        else:
            report.ok("Metadata", f"<title> set: '{title}' ✓")


def check_footer_consistency(html: str, report: Report):
    """All footers must include VANLogoGold.jpg and issue-info."""
    page_count = html.count('<div class="page">')
    logo_count = html.count("VANLogoGold.jpg")
    issue_info_count = html.count('class="issue-info"')

    if page_count == 0:
        return  # template may not have many pages

    # Allow ± 1 for pages without footer (shouldn't happen)
    if logo_count >= page_count:
        report.ok("Footer Consistency",
                  f"VANLogoGold.jpg present in all {page_count} page footer(s) ✓")
    else:
        report.fail("Footer Consistency",
                    f"VANLogoGold.jpg found {logo_count}× but there are {page_count} pages — "
                    "some footers missing logo")

    if issue_info_count >= page_count:
        report.ok("Footer Consistency",
                  f"issue-info spans present in all {page_count} footer(s) ✓")
    else:
        report.warn("Footer Consistency",
                    f"issue-info spans: {issue_info_count} found, {page_count} pages — "
                    "some footers may be missing issue metadata")


# ══════════════════════════════════════════════════════════════════════════════
# Main orchestration
# ══════════════════════════════════════════════════════════════════════════════

def validate_file(filepath: Path) -> Report:
    report = Report(str(filepath))

    if not filepath.exists():
        report.fail("File", f"File not found: {filepath}")
        return report

    html = filepath.read_text(encoding="utf-8")
    css  = extract_css(html)
    body = extract_body(html)

    is_template = "TEMPLATE" in filepath.name.upper()

    if not css:
        report.fail("File", "No <style> block found — CSS is missing entirely")
        return report

    report.ok("File", f"File loaded ({len(html):,} bytes, "
              f"CSS: {len(css):,} chars) ✓")

    # Run all checks
    check_title_tag(html, is_template, report)
    check_meta_viewport(html, report)
    check_font_import(html, report)
    check_css_classes(css, report)
    check_brand_colors(css, report)
    check_theme_system(css, html, report)
    check_css_variable_values(css, report)
    check_media_queries(css, report)
    check_print_query_intact(css, report)
    check_overflow_guard(css, report)
    check_page_structure(body, report)
    check_image_refs(html, report)
    check_footer_consistency(html, report)
    check_placeholders(html, is_template, report)
    check_senthamizh(html, report)

    return report


def main():
    args = sys.argv[1:]

    if "--all" in args:
        files = list(PROJECT_DIR.glob("*.html"))
        if not files:
            print("No HTML files found in project directory.")
            sys.exit(0)
    elif args:
        files = [Path(args[0])]
    else:
        files = [TEMPLATE]

    exit_code = 0
    for f in files:
        report = validate_file(f)
        report.print_report()
        exit_code = max(exit_code, report.exit_code())

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
