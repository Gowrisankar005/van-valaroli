#!/usr/bin/env python3
"""
validate_mmd.py — Lint Magazine Markdown files before submission.

Catches common mistakes early:
  • Missing required frontmatter fields
  • Unclosed ::: directives
  • Image files referenced but missing
  • English loan words (செந்தமிழ் check)
  • Em-dash typos (---- instead of —)
  • Page-budget estimation

Usage:
    # Single file
    python validate_mmd.py article.md

    # Multiple files
    python validate_mmd.py issues/Issue-03/articles/*.md

    # Validate against issue meta (checks section names match + images exist)
    python validate_mmd.py issues/Issue-03/articles/*.md --issue issues/Issue-03

Exit code 0 = all clean, 1 = errors, 2 = warnings only.
"""
import argparse
import json
import re
import sys
from pathlib import Path

from mmd_parser import parse_frontmatter, DIRECTIVE_OPEN, DIRECTIVE_CLOSE


# ─── Lint rules ──────────────────────────────────────────────────────────────

REQUIRED_FRONTMATTER = ['section', 'title', 'author']

# Common English loan words → suggested replacements
LOAN_WORDS = {
    'கம்ப்யூட்டர்': 'கணினி',
    'லேப்டாப்': 'மடிக்கணினி',
    'மொபைல்': 'கைப்பேசி',
    'போன்': 'அலைபேசி',
    'இன்டர்நெட்': 'இணையம்',
    'இ-மெயில்': 'மின்னஞ்சல்',
    'வெப்சைட்': 'இணையதளம்',
    'ஸ்கூல்': 'பள்ளி',
    'காலேஜ்': 'கல்லூரி',
    'டீச்சர்': 'ஆசிரியர்',
    'ஸ்டூடென்ட்': 'மாணவர்',
    'ஹாஸ்பிடல்': 'மருத்துவமனை',
    'டாக்டர்': 'மருத்துவர்',
    'நர்ஸ்': 'செவிலியர்',
    'மெடிசின்': 'மருந்து',
    'பஸ்': 'பேருந்து',
    'டிரெய்ன்': 'தொடர்வண்டி',
    'ரோடு': 'சாலை',
}

DIRECTIVE_NAMES = {'quote', 'box', 'image', 'closing'}

# Chars-per-page sizing (matches rebalance_sections capacities)
CHARS_PER_BODY_PAGE = 2800     # rough A4 capacity at 11pt
SUBHEAD_COST_CHARS = 150
QUOTE_COST_CHARS = 300
IMAGE_COST_CHARS = 500
BOX_COST_CHARS = 600


class Issue:
    def __init__(self, level, file, line, msg):
        self.level = level         # 'error' | 'warning' | 'info'
        self.file = file
        self.line = line           # 1-indexed; 0 = file-level
        self.msg = msg

    def render(self, max_file_len: int) -> str:
        loc = f"{self.file}:{self.line}" if self.line else f"{self.file}"
        icon = {'error': '✗', 'warning': '⚠', 'info': 'ℹ'}[self.level]
        return f"  {icon} {loc:<{max_file_len + 6}}  {self.msg}"


# ─── Checks ──────────────────────────────────────────────────────────────────

def check_frontmatter(text: str, file: str) -> list:
    issues = []
    meta, body = parse_frontmatter(text)
    if not meta:
        issues.append(Issue('error', file, 1,
            "missing or malformed YAML frontmatter at top of file"))
        return issues, meta, body
    for field in REQUIRED_FRONTMATTER:
        if not meta.get(field):
            issues.append(Issue('error', file, 1,
                f"frontmatter missing required field: '{field}'"))
    if 'subtitle' not in meta:
        issues.append(Issue('info', file, 1,
            "no subtitle — that's ok, it's optional"))
    return issues, meta, body


def check_directives(body: str, file: str) -> list:
    """Ensure every ::: has a matching closing :::"""
    issues = []
    open_stack = []  # list of (line_no, name)
    for i, line in enumerate(body.splitlines(), start=1):
        s = line.strip()
        m = DIRECTIVE_OPEN.match(s)
        if m:
            name = m.group(1)
            if name not in DIRECTIVE_NAMES:
                issues.append(Issue('error', file, i,
                    f"unknown directive ':::{name}'  "
                    f"(valid: {', '.join(sorted(DIRECTIVE_NAMES))})"))
            open_stack.append((i, name))
            continue
        if DIRECTIVE_CLOSE.match(s):
            if not open_stack:
                issues.append(Issue('error', file, i,
                    "closing ':::' with no matching opener"))
            else:
                open_stack.pop()
    for line_no, name in open_stack:
        issues.append(Issue('error', file, line_no,
            f"unclosed directive ':::{name}' (missing closing ':::')"))
    return issues


# Tamil letters + vowel signs/virama — used to build word-boundary lookarounds,
# since \b relies on \w and doesn't reliably split Tamil combining marks.
_TAMIL_CHAR = r'஀-௿'
_LOAN_WORD_RE = {
    bad: re.compile(rf'(?<![{_TAMIL_CHAR}]){re.escape(bad)}(?![{_TAMIL_CHAR}])')
    for bad in LOAN_WORDS
}


def check_loan_words(body: str, file: str) -> list:
    issues = []
    for i, line in enumerate(body.splitlines(), start=1):
        for bad, good in LOAN_WORDS.items():
            if _LOAN_WORD_RE[bad].search(line):
                issues.append(Issue('warning', file, i,
                    f"English loan word '{bad}' — use செந்தமிழ் '{good}'"))
    return issues


def check_emdash_typos(body: str, file: str) -> list:
    issues = []
    for i, line in enumerate(body.splitlines(), start=1):
        s = line.strip()
        # 4+ dashes at start (citation typo)
        if re.match(r'^-{4,}\s', s):
            issues.append(Issue('warning', file, i,
                "use em-dash '—' (U+2014) for citations, not '----'"))
    return issues


def check_images(body: str, file: str, images_dir: Path | None) -> list:
    """If images_dir is provided, verify each :::image src= file exists."""
    issues = []
    if images_dir is None:
        return issues
    for i, line in enumerate(body.splitlines(), start=1):
        s = line.strip()
        m = DIRECTIVE_OPEN.match(s)
        if not m or m.group(1) != 'image':
            continue
        attr_str = m.group(2) or ''
        src_match = re.search(r'src=(?:"([^"]+)"|\'([^\']+)\'|(\S+))', attr_str)
        if not src_match:
            issues.append(Issue('error', file, i,
                "image directive missing src=\"filename.jpg\""))
            continue
        src = src_match.group(1) or src_match.group(2) or src_match.group(3)
        if not (images_dir / src).exists():
            issues.append(Issue('error', file, i,
                f"image file not found: images/{src}"))
    return issues


def check_section_match(meta: dict, file: str, issue_meta: dict | None) -> list:
    """Ensure the article's section matches one in issue_meta.json."""
    issues = []
    if not issue_meta:
        return issues
    sec = meta.get('section', '')
    valid = {s['section_name'] for s in issue_meta.get('sections', [])}
    if sec and sec not in valid:
        suggested = ', '.join(sorted(valid))
        issues.append(Issue('error', file, 1,
            f"section '{sec}' not in issue_meta.json. "
            f"Valid: {suggested}"))
    return issues


# ─── Page estimation ─────────────────────────────────────────────────────────

def estimate_pages(body: str) -> float:
    """Rough page count estimate for the article."""
    body_chars = 0
    cost_chars = 0
    in_directive = None
    for line in body.splitlines():
        s = line.strip()
        m = DIRECTIVE_OPEN.match(s)
        if m:
            in_directive = m.group(1)
            cost_chars += {
                'quote':   QUOTE_COST_CHARS,
                'box':     BOX_COST_CHARS,
                'image':   IMAGE_COST_CHARS,
                'closing': 200,
            }.get(in_directive, 100)
            continue
        if DIRECTIVE_CLOSE.match(s):
            in_directive = None
            continue
        if in_directive:
            continue
        if s.startswith('## '):
            cost_chars += SUBHEAD_COST_CHARS
            continue
        if s.startswith('#') or s.startswith('- '):
            continue
        body_chars += len(s)
    # Section-header on first page costs ~500 chars
    cost_chars += 500
    total_chars = body_chars + cost_chars
    return total_chars / CHARS_PER_BODY_PAGE


# ─── Main driver ─────────────────────────────────────────────────────────────

def validate_file(path: Path, issue_meta: dict | None,
                  images_dir: Path | None) -> tuple[list, dict, float]:
    if not path.exists():
        return [Issue('error', str(path), 0, 'file not found')], {}, 0.0
    text = path.read_text(encoding='utf-8')
    fm_issues, meta, body = check_frontmatter(text, str(path))
    issues = (fm_issues
              + check_directives(body, str(path))
              + check_loan_words(body, str(path))
              + check_emdash_typos(body, str(path))
              + check_images(body, str(path), images_dir)
              + check_section_match(meta, str(path), issue_meta))
    pages = estimate_pages(body)
    return issues, meta, pages


def main():
    ap = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('files', nargs='+', help='MMD files to validate')
    ap.add_argument('--issue', metavar='ISSUE_DIR',
                    help='Issue folder (loads issue_meta.json + images/)')
    args = ap.parse_args()

    # Load issue context if provided
    issue_meta = None
    images_dir = None
    if args.issue:
        issue_root = Path(args.issue).resolve()
        meta_path = issue_root / 'issue_meta.json'
        if meta_path.exists():
            issue_meta = json.loads(meta_path.read_text(encoding='utf-8'))
        if (issue_root / 'images').exists():
            images_dir = issue_root / 'images'
        print(f"  Issue context: {issue_root.name}")
        print()

    # Validate each file
    all_issues = []
    summary = []
    for f in args.files:
        path = Path(f).resolve()
        issues, meta, pages = validate_file(path, issue_meta, images_dir)
        all_issues.extend(issues)
        summary.append((path.name, meta.get('section', '?'),
                        meta.get('title', '?'), round(pages, 1), len(issues)))

    # Render report
    if all_issues:
        max_loc = max(len(f"{i.file}:{i.line}") for i in all_issues)
        print("Lint findings:")
        print()
        for i in sorted(all_issues, key=lambda x: (x.file, x.line, x.level)):
            print(i.render(max_loc))
        print()

    # Summary table
    print("Per-article summary:")
    print(f"  {'file':<28} {'section':<25} {'~pages':>7} {'issues':>7}")
    print(f"  {'-'*28} {'-'*25} {'-'*7} {'-'*7}")
    for fn, sec, _title, pg, n in summary:
        print(f"  {fn:<28} {sec:<25} {pg:>7.1f} {n:>7}")
    print()

    n_err = sum(1 for i in all_issues if i.level == 'error')
    n_warn = sum(1 for i in all_issues if i.level == 'warning')
    n_info = sum(1 for i in all_issues if i.level == 'info')
    print(f"Totals: {n_err} errors, {n_warn} warnings, {n_info} info")

    if n_err:
        sys.exit(1)
    if n_warn:
        sys.exit(2)
    print("✓ All clean.")
    sys.exit(0)


if __name__ == '__main__':
    main()
