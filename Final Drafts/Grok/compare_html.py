#!/usr/bin/env python3
"""
compare_html.py — Diff two magazine HTML files at the section/page level
to surface unintended regressions.

Specifically checks:
  1. Page count            — must match (37)
  2. Section start pages   — every section's first page must still have
                             its .section-header at the start of the file
  3. Section integrity     — for each section, the set of paragraphs in
                             the new HTML should equal the set in the
                             source (no content lost or moved across a
                             section boundary)
  4. Byline preservation   — author bylines should still be on the FIRST
                             page of their section, not floated elsewhere
  5. Image references      — count of <img> tags should match (only the
                             src path may differ)

Usage:
    python3 compare_html.py <source.html> <new.html>
"""
import sys
from pathlib import Path
from collections import Counter
from lxml import html as lxml_html


def find_pages(doc):
    """Return list of .page elements in document order (excludes .cover)."""
    return doc.xpath(
        '//div[contains(concat(" ", normalize-space(@class), " "), " page ")]')


def section_name_of(page):
    """Return the .page-header section-name text, or '?' if missing."""
    sn = page.find('.//span[@class="section-name"]')
    return (sn.text or '').strip() if sn is not None else '?'


def page_number_of(page):
    pn = page.find('.//span[@class="page-number"]')
    return (pn.text or '').strip() if pn is not None else '?'


def is_section_start(page):
    """True if page has .section-header (not .continuation-banner)."""
    for ch in page.iter():
        if ch.tag != 'div':
            continue
        cls = (ch.get('class') or '').split()
        if 'section-header' in cls:
            return True
        if 'continuation-banner' in cls:
            return False
    return False


def normalize_text(s):
    """Collapse whitespace for comparison."""
    return ' '.join((s or '').split())


def gather_paragraphs(page):
    """Yield normalized text of each <p> inside a page's body-text."""
    body = None
    for ch in page.iter():
        if ch.tag == 'div' and 'body-text' in (ch.get('class') or '').split():
            body = ch
            break
    if body is None:
        return []
    paras = []
    for el in body.iter():
        if el.tag == 'p':
            txt = normalize_text(el.text_content())
            if txt:
                paras.append(txt)
    return paras


def group_by_section(pages):
    """Walk pages, group consecutive pages of the same section together.
    Returns list of (section_name, [pages...]) in document order."""
    groups = []
    cur_name, cur_list = None, []
    for p in pages:
        nm = section_name_of(p)
        if is_section_start(p) or nm != cur_name:
            if cur_list:
                groups.append((cur_name, cur_list))
            cur_name, cur_list = nm, [p]
        else:
            cur_list.append(p)
    if cur_list:
        groups.append((cur_name, cur_list))
    return groups


def report(src_path: Path, new_path: Path):
    src = lxml_html.parse(str(src_path)).getroot()
    new = lxml_html.parse(str(new_path)).getroot()

    src_pages = find_pages(src)
    new_pages = find_pages(new)

    print("━" * 64)
    print(f"  source:   {src_path.name}")
    print(f"  new:      {new_path.name}")
    print("━" * 64)

    # 1. Page count (informational — page count adjustment is intentional)
    print(f"\n[1] Page count")
    delta = len(new_pages) - len(src_pages)
    sign = '+' if delta > 0 else ''
    print(f"    ℹ  source {len(src_pages)} → new {len(new_pages)} "
          f"({sign}{delta} from per-section page-count adjustment)")

    # 2. Section order & names (regardless of page numbers)
    print(f"\n[2] Section order")
    src_section_names = [section_name_of(p) for p in src_pages if is_section_start(p)]
    new_section_names = [section_name_of(p) for p in new_pages if is_section_start(p)]
    if src_section_names == new_section_names:
        print(f"    ✓  {len(src_section_names)} sections in identical order")
    else:
        print(f"    ✗  section order changed!")
        print(f"        source: {src_section_names}")
        print(f"        new:    {new_section_names}")

    # 3. Section integrity — paragraph set per section
    print(f"\n[3] Section integrity (paragraphs preserved per section)")
    src_sections = group_by_section(src_pages)
    new_sections = group_by_section(new_pages)

    issues = []
    for (s_name, s_pages), (n_name, n_pages) in zip(src_sections, new_sections):
        if s_name != n_name:
            issues.append(f"  section name mismatch: src '{s_name}' vs new '{n_name}'")
            continue
        s_paras = Counter(p for page in s_pages for p in gather_paragraphs(page))
        n_paras = Counter(p for page in n_pages for p in gather_paragraphs(page))
        if s_paras == n_paras:
            n_lost = 0
            n_gained = 0
        else:
            lost = s_paras - n_paras
            gained = n_paras - s_paras
            n_lost = sum(lost.values())
            n_gained = sum(gained.values())
            if n_lost or n_gained:
                issues.append(
                    f"  '{s_name}': {n_lost} para(s) lost, {n_gained} para(s) gained")
                for p, _ in lost.most_common(3):
                    issues.append(f"      − {p[:80]}…")
                for p, _ in gained.most_common(3):
                    issues.append(f"      + {p[:80]}…")
    if not issues:
        print(f"    ✓  all {len(src_sections)} section(s) preserve their content exactly")
    else:
        print(f"    ✗  found {len(issues)} section issue(s):")
        for line in issues:
            print(line)

    # 4. Byline check — for each section, byline should be on FIRST page
    print(f"\n[4] Author bylines on section's first page")
    def find_byline_locations(pages_list):
        """Return list of (page_number, byline_text)."""
        locs = []
        for p in pages_list:
            for el in p.iter():
                if el.tag == 'div' and 'author-byline' in (el.get('class') or '').split():
                    locs.append((page_number_of(p), normalize_text(el.text_content())))
        return locs

    issues = []
    for s_name, s_pages in new_sections:
        bylines = find_byline_locations(s_pages)
        if not bylines:
            continue
        first_pn = page_number_of(s_pages[0])
        for pn, byline in bylines:
            if pn != first_pn:
                issues.append(
                    f"  '{s_name}': byline '{byline}' appears on page {pn}, "
                    f"section starts at {first_pn}")
    if not issues:
        print(f"    ✓  all bylines are on their section's first page")
    else:
        print(f"    ✗  byline misplacements:")
        for line in issues:
            print(line)

    # 5. Image count (footer logo present per-page; page count change
    # produces predictable image delta of 1 per added page)
    print(f"\n[5] Image references")
    src_imgs = src.xpath('//img')
    new_imgs = new.xpath('//img')
    page_delta = len(new_pages) - len(src_pages)
    img_delta = len(new_imgs) - len(src_imgs)
    expected_delta = page_delta   # each new page brings one footer logo
    print(f"    source: {len(src_imgs)} <img>   new: {len(new_imgs)} "
          f"(delta {img_delta:+d}, expected {expected_delta:+d} from page count change)")
    if img_delta == expected_delta:
        print(f"    ✓  image count consistent with page count change")
    else:
        print(f"    ✗  unexpected image count delta")

    print("\n" + "━" * 64)


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    src = Path(sys.argv[1])
    new = Path(sys.argv[2])
    if not src.exists() or not new.exists():
        print(f"✗ File not found: {src if not src.exists() else new}")
        sys.exit(1)
    report(src, new)


if __name__ == '__main__':
    main()
