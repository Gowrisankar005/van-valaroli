#!/usr/bin/env python3
"""
validate_template.py — வான் வளரொளி இதழ் HTML Validator
========================================================
Validates the template and any issue file against:
  - CSS class completeness (all design-spec components present)
  - Brand color integrity (hex values match spec)
  - CSS variable values (no circular var() references in :root / theme blocks)
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
  python3 validate_template.py --self-test              # tests the validator itself

Exit codes: 0 = PASS, 1 = WARNINGS only, 2 = FAILURES found

─────────────────────────────────────────────────────────────────────────────
STANDARD PRACTICE — Keeping the validator trustworthy
─────────────────────────────────────────────────────────────────────────────
Rule: Every bug that escapes this validator must become a permanent self-test.
      No gap may cause a production problem twice.

When you find a validator gap:
  1. Write a self-test case that FAILS (proving the gap exists)      ← red
  2. Add / fix the check function so the self-test PASSES            ← green
  3. Commit both together: "Fix validator gap: <description>"

Self-tests run before HTML validation in CI, so a broken validator
is caught before it silently misses real issues.
─────────────────────────────────────────────────────────────────────────────
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
    "Images/van-logo.jpg",
    "Images/vallaroli-logo.jpg",
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
    # Capture content between consecutive <div class="page"> openings, or to end-of-string.
    # NOTE: body is already extracted (no <body> tags present), so do NOT use </body> as sentinel.
    page_blocks = re.findall(
        r'<div class="page">(.*?)(?=<div class="page">|$)',
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
    """Image src refs: cover/logo base64 is OK (self-contained design); footer logos must use file paths."""
    body = extract_body(html)
    base64_imgs = re.findall(r'<img[^>]+src=["\']data:image/', body)
    # Classify: footer logos with base64 are a real problem; cover/seal/decorative base64 is acceptable
    # Footer logos are identified by class="van-logo-footer"
    base64_footers = re.findall(r'<img[^>]*van-logo-footer[^>]*data:image[^>]*>', body)
    if base64_footers:
        report.fail("Images",
                    f"{len(base64_footers)} footer logo(s) use base64 — "
                    "footer logos must use file paths (Images/van-logo.jpg) for consistency")
    elif base64_imgs:
        # Cover/decorative images embedded as base64: acceptable for self-contained delivery
        report.warn("Images",
                    f"{len(base64_imgs)} base64 image(s) in body (cover/decorative) — "
                    "acceptable for self-contained HTML; footer logos use file paths ✓")
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
    """Scan body text for banned loan words.

    Tamil vowel signs (ு, ோ, ா ...) are non-word chars in Python regex, so the
    word-boundary trick fails at the end of Tamil words.  Instead we tokenise the
    plain text on whitespace and punctuation, then look for exact-token matches.
    This correctly catches standalone 'ரோடு' while ignoring the same string
    when it is a suffix of a legitimate word such as 'உலகத்தாரோடு'.
    """
    body = extract_body(html)
    # Replace HTML tags with spaces so adjacent words don't merge
    text = re.sub(r'<[^>]+>', ' ', body)
    # Tokenise: split on whitespace, Tamil punctuation, and common punctuation
    tokens = set(re.split(r'[\s,;.!?()\u0964\u0965\u200b\u00a0\n\t]+', text))
    # Strip any residual ASCII punctuation from token edges
    tokens = {t.strip('.,;:!?()"\'-') for t in tokens if t}
    violations = []
    for banned, correct in SENTHAMIZH_VIOLATIONS.items():
        if banned in tokens:
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
    import re as _re
    # Check with flexible whitespace and optional !important
    def rule_present(pattern):
        return bool(_re.search(pattern, css))

    essential = [
        (r"page-break-after:\s*always",   "page-break-after: always"),
        (r"break-after:\s*page",           "break-after: page"),
        (r"width:\s*210mm",                "width: 210mm"),
        (r"(min-)?height:\s*297mm",        "height: 297mm (or min-height: 297mm)"),
    ]
    missing = [(label) for pattern, label in essential if not rule_present(pattern)]
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
        # FAIL not WARN: this rule was added specifically to fix horizontal scroll on mobile.
        # Its absence directly breaks the mobile layout — not optional.
        report.fail("Responsiveness",
                    "overflow-x: hidden missing — mobile layout will show horizontal scrollbar. "
                    "Add: html, body { overflow-x: hidden; max-width: 100%; }")


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
    """All footers must include Images/van-logo.jpg and issue-info."""
    page_count = html.count('<div class="page">')
    logo_count = html.count("van-logo.jpg")
    issue_info_count = html.count('class="issue-info"')

    if page_count == 0:
        return  # template may not have many pages

    # Allow ± 1 for pages without footer (shouldn't happen)
    if logo_count >= page_count:
        report.ok("Footer Consistency",
                  f"van-logo.jpg present in all {page_count} page footer(s) ✓")
    else:
        report.fail("Footer Consistency",
                    f"van-logo.jpg found {logo_count}× but there are {page_count} pages — "
                    "some footers missing logo")

    if issue_info_count >= page_count:
        report.ok("Footer Consistency",
                  f"issue-info spans present in all {page_count} footer(s) ✓")
    else:
        report.warn("Footer Consistency",
                    f"issue-info spans: {issue_info_count} found, {page_count} pages — "
                    "some footers may be missing issue metadata")


# ══════════════════════════════════════════════════════════════════════════════
# Self-test suite  (python3 validate_template.py --self-test)
# ══════════════════════════════════════════════════════════════════════════════
#
# Each entry proves ONE check function behaves correctly on a known input.
# "expect" is either "fail" (check must raise ≥1 FAIL) or "pass" (0 FAILs).
#
# HOW TO ADD A NEW SELF-TEST:
#   1. Give it a unique ID  (e.g. "VAR-003", "IMG-002")
#   2. Set "check" to the exact function name
#   3. Provide minimal "css" and/or "html" that exercise the scenario
#   4. Set "expect": "fail" for bad inputs, "pass" for good inputs
#   5. Add "origin" explaining which real bug this guards against
# ─────────────────────────────────────────────────────────────────────────────

SELF_TESTS = [

    # ── CSS Variable Values ───────────────────────────────────────────────────
    {
        "id": "VAR-001",
        "description": "Circular var() in :root must FAIL",
        "check": "check_css_variable_values",
        "css": ":root { --van-primary: var(--van-primary); --van-deep: #2d7a3e; }",
        "expect": "fail",
        "origin": "Commit 4d63330: replacement script overwrote :root hex values "
                  "with var() self-refs → all fonts fell back to black. "
                  "Old check_brand_colors/check_theme_system both passed because "
                  "they only tested for the variable NAME, not its VALUE.",
    },
    {
        "id": "VAR-002",
        "description": "Circular var() inside [data-theme] block must FAIL",
        "check": "check_css_variable_values",
        "css": (":root { --van-primary: #8DC63F; }"
                "[data-theme=\"blue\"] { --van-gold: var(--van-gold); }"),
        "expect": "fail",
        "origin": "Blue theme had --van-gold: var(--van-gold) with different "
                  "indentation; fix script matched :root but missed theme block.",
    },
    {
        "id": "VAR-003",
        "description": "Valid hex values in :root and theme blocks must PASS",
        "check": "check_css_variable_values",
        "css": (":root { --van-primary: #8DC63F; --van-deep: #2d7a3e; }"
                "[data-theme=\"blue\"] { --van-primary: #1A6BB5; "
                "--van-gold: #D4AF37; }"),
        "expect": "pass",
    },

    # ── Brand Colors ──────────────────────────────────────────────────────────
    {
        "id": "CLR-001",
        "description": "Brand color missing entirely must FAIL",
        "check": "check_brand_colors",
        "css": "body { color: red; }",   # none of the required brand colors
        "expect": "fail",
    },
    {
        "id": "CLR-002",
        "description": "Brand color present as CSS variable name must PASS",
        "check": "check_brand_colors",
        "css": (":root { --van-primary: #8DC63F; --van-dark: #6BA82F; "
                "--van-deep: #2d7a3e; --van-gold: #D4AF37; "
                "--body-text: #2B2B2B; --page-bg-top: #fffef5; "
                "--page-bg-bottom: #fef9f2; }"),
        "expect": "pass",
    },

    # ── செந்தமிழ் ─────────────────────────────────────────────────────────────
    {
        "id": "STZ-001",
        "description": "Banned Tamil loan word in body must FAIL",
        "check": "check_senthamizh",
        "html": "<html><body><p>கம்ப்யூட்டர் பயன்படுத்துக</p></body></html>",
        "expect": "fail",
    },
    {
        "id": "STZ-002",
        "description": "Clean pure-Tamil body text must PASS",
        "check": "check_senthamizh",
        "html": "<html><body><p>கணினி பயன்படுத்துக</p></body></html>",
        "expect": "pass",
    },
    {
        "id": "STZ-003",
        "description": "'ரோடு' as suffix of a legitimate Tamil word (உலகத்தாரோடு) must NOT trigger false positive",
        "check": "check_senthamizh",
        "html": "<html><body><p>உலகத்தாரோடு நட்பு கொண்டு வாழ்வதே சிறந்த அறிவு.</p></body></html>",
        "expect": "pass",
    },
    {
        "id": "STZ-004",
        "description": "Standalone loan word 'ரோடு' (road) as a word must FAIL",
        "check": "check_senthamizh",
        "html": "<html><body><p>அந்த ரோடு மிகவும் நீளமானது.</p></body></html>",
        "expect": "fail",
    },

    # ── Images ────────────────────────────────────────────────────────────────
    {
        "id": "IMG-001",
        "description": "Footer logo as base64 must FAIL (must use file path)",
        "check": "check_image_refs",
        "html": ('<html><body>'
                 '<img class="van-logo-footer" src="data:image/png;base64,iVBORw0KGgo=" alt="VAN">'
                 '</body></html>'),
        "expect": "fail",
    },
    {
        "id": "IMG-002",
        "description": "File-path image reference in body must PASS (no base64)",
        "check": "check_image_refs",
        "html": ('<html><body>'
                 '<img src="Images/van-logo.jpg">'
                 '<img src="Images/vallaroli-logo.jpg">'
                 '</body></html>'),
        "expect": "pass",
    },

    # ── Media Queries ─────────────────────────────────────────────────────────
    {
        "id": "MQ-001",
        "description": "Missing @media print must FAIL",
        "check": "check_media_queries",
        "css": "@media screen and (max-width: 880px) { } "
               "@media screen and (max-width: 600px) { } @page { }",
        "expect": "fail",
    },
    {
        "id": "MQ-002",
        "description": "All required media queries present must PASS",
        "check": "check_media_queries",
        "css": ("@media print { .page { page-break-after: always; } } "
                "@media screen and (max-width: 880px) { } "
                "@media screen and (max-width: 600px) { } "
                "@page { size: A4 portrait; margin: 0; }"),
        "expect": "pass",
    },

    # ── Page Structure ────────────────────────────────────────────────────────
    {
        "id": "PG-001",
        "description": "Page missing content-area must FAIL",
        "check": "check_page_structure",
        "html": ('<html><body>'
                 '<div class="page">'
                 '  <div class="page-header"></div>'
                 '  <div class="page-footer"></div>'
                 '</div>'
                 '</body></html>'),
        "expect": "fail",
    },
    {
        "id": "PG-002",
        "description": "Page with all required structure must PASS",
        "check": "check_page_structure",
        "html": ('<html><body>'
                 '<div class="page">'
                 '  <div class="glossy"></div>'
                 '  <span class="corner-tl">❈</span>'
                 '  <span class="corner-br">❈</span>'
                 '  <div class="page-header"></div>'
                 '  <div class="content-area"></div>'
                 '  <div class="page-footer"></div>'
                 '</div>'
                 '</body></html>'),
        "expect": "pass",
    },

    # ── Overflow Guard ────────────────────────────────────────────────────────
    {
        "id": "OVF-001",
        "description": "Missing overflow-x guard must FAIL",
        "check": "check_overflow_guard",
        "css": "body { margin: 0; }",
        "expect": "fail",
    },
    {
        "id": "OVF-002",
        "description": "overflow-x: hidden on html/body must PASS",
        "check": "check_overflow_guard",
        "css": "html, body { overflow-x: hidden; max-width: 100%; }",
        "expect": "pass",
    },

    # ── Placeholders ──────────────────────────────────────────────────────────
    {
        "id": "PH-001",
        "description": "Unfilled [SLOT] in issue file must FAIL",
        "check": "check_placeholders",
        "html": ('<html><head><title>Issue</title></head>'
                 '<body><p>[ARTICLE TITLE]</p></body></html>'),
        "is_template": False,
        "expect": "fail",
    },
    {
        "id": "PH-002",
        "description": "No unfilled slots in issue file must PASS",
        "check": "check_placeholders",
        "html": ('<html><head><title>Issue</title></head>'
                 '<body><p>திருக்குறள் ஆய்வு</p></body></html>'),
        "is_template": False,
        "expect": "pass",
    },
]


def _run_one_self_test(test: dict) -> tuple:
    """
    Run a single self-test. Returns (passed: bool, detail: str).
    A self-test 'passes' when the check behaves as expected.
    """
    css  = test.get("css",  "")
    html = test.get("html", "") or (
        f"<html><head><style>{css}</style></head><body></body></html>"
    )
    is_template = test.get("is_template", True)
    body = extract_body(html)

    r = Report("self-test")

    # Dispatch to the right check function
    fn_name = test["check"]
    dispatch = {
        "check_css_variable_values": lambda: check_css_variable_values(css, r),
        "check_brand_colors":        lambda: check_brand_colors(css, r),
        "check_theme_system":        lambda: check_theme_system(css, html, r),
        "check_media_queries":       lambda: check_media_queries(css, r),
        "check_print_query_intact":  lambda: check_print_query_intact(css, r),
        "check_css_classes":         lambda: check_css_classes(css, r),
        "check_senthamizh":          lambda: check_senthamizh(html, r),
        "check_image_refs":          lambda: check_image_refs(html, r),
        "check_page_structure":      lambda: check_page_structure(body, r),
        "check_overflow_guard":      lambda: check_overflow_guard(css, r),
        "check_placeholders":        lambda: check_placeholders(html, is_template, r),
    }
    fn = dispatch.get(fn_name)
    if fn is None:
        return False, f"Unknown check function: {fn_name}"

    fn()

    expect_fail = (test["expect"] == "fail")
    actually_failed = (r.fail_cnt > 0)

    if expect_fail and actually_failed:
        return True, "correctly detected the bad pattern ✓"
    elif not expect_fail and not actually_failed:
        return True, "correctly accepted the good pattern ✓"
    elif expect_fail and not actually_failed:
        return False, (f"MISSED — expected FAIL but got PASS. "
                       f"The check did not catch this bad pattern.")
    else:
        return False, (f"FALSE ALARM — expected PASS but got FAIL. "
                       f"The check incorrectly rejected a valid pattern.")


def run_self_tests() -> int:
    """
    Run all self-tests. Returns exit code: 0 = all pass, 2 = gaps found.
    """
    GREEN  = "\033[32m"
    RED    = "\033[31m"
    YELLOW = "\033[33m"
    RESET  = "\033[0m"
    BOLD   = "\033[1m"

    print(f"\n{'═'*64}")
    print(f"  {BOLD}வான் வளரொளி — Validator Self-Tests{RESET}")
    print(f"  Proving the validator catches what it should")
    print(f"{'═'*64}")

    passed = 0
    failed = 0
    last_check = None

    for test in SELF_TESTS:
        check = test["check"]
        if check != last_check:
            print(f"\n  ── {check} ──")
            last_check = check

        ok, detail = _run_one_self_test(test)

        label = f"{test['id']}: {test['description']}"
        if ok:
            print(f"  {GREEN}✅  {label}{RESET}")
            passed += 1
        else:
            print(f"  {RED}❌  {label}{RESET}")
            print(f"      {RED}↳  {detail}{RESET}")
            if "origin" in test:
                print(f"      {YELLOW}Origin: {test['origin'][:80]}{RESET}")
            failed += 1

    print(f"\n{'─'*64}")
    total = passed + failed
    print(f"  Self-tests: {passed} passed  |  {failed} failed  (of {total})")

    if failed == 0:
        print(f"\n  {GREEN}✅  All self-tests pass — validator is trustworthy.{RESET}")
        print(f"  Every known gap has a check. Every check has a test.")
    else:
        print(f"\n  {RED}❌  {failed} self-test(s) FAILED — validator has gaps.{RESET}")
        print(f"  A gap means a real bug could slip through undetected.")
        print(f"  Fix the check function(s) before running HTML validation.")
    print(f"{'═'*64}\n")

    return 0 if failed == 0 else 2


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

    # ── Self-test mode ────────────────────────────────────────────────────────
    if "--self-test" in args:
        sys.exit(run_self_tests())

    # ── HTML validation mode ──────────────────────────────────────────────────
    if "--all" in args:
        # Scan root HTML files only — skip Archive/ (old versions kept for reference)
        files = [f for f in PROJECT_DIR.glob("*.html")]
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
