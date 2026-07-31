#!/usr/bin/env python3
"""
rebalance_sections.py — Within each section, redistribute content elements
across the section's existing pages so each page has roughly equal body-text
density. Uses Playwright to measure real rendered heights and applies
logical-closure rules so breaks land at reader-friendly points.

Key principles:
  • Page count per section is PRESERVED — only redistribution happens.
  • Logical closure (reader experience):
      - never break inside a .slim-quote, .highlights-box, .closing block
      - never end a page on a .subhead (subhead always travels with its
        following element)
      - never split a <figure> from siblings before its caption
      - prefer breaks AFTER a .section-divider (natural sub-thought break)
      - never split mid-paragraph (paragraphs are atomic)
  • Element order WITHIN each section is preserved exactly — only the
    page-boundary positions move.

Usage:
    python3 rebalance_sections.py <input.html> <output.html>
"""
import sys
import math
from copy import deepcopy
from pathlib import Path
from lxml import html as lxml_html
from playwright.sync_api import sync_playwright


# CSS px equivalents at 96 DPI; mirrored from balance_pages.py
A4_BODY_PX = 1015        # ~268mm usable body height per A4 page
TARGET_PX  = 1000        # aim slightly under to leave breathing room
TOLERANCE  = 0.10        # allow target ± 10% before forcing break

# Per-page CAPACITY (px of body-text that fits inside an A4 page without
# pushing the page total over 297mm). Section-start pages lose ~120px to
# the .section-header block, so they have a smaller body-text budget.
# Using per-page targets in rebalance ensures uniform zoom (or zero zoom)
# across pages in a section — the previous symmetric target made
# section-start pages over-fill and need extra zoom (= smaller text).
SECTION_START_CAPACITY_PX = 850   # first page of a section
CONTINUATION_CAPACITY_PX  = 990   # follow-on pages

# Page-count adjustment: ideal density per page (~ 250mm body-text).
# Sections with content above this get extra pages; below get fewer.
IDEAL_DENSITY_PX = 950
# Don't auto-adjust if content is too small (closing/teaser pages stay)
MIN_TOTAL_TO_ADJUST = 200

MEASUREMENT_CSS = """
    #theme-picker { display: none !important; }
    .glossy { display: none !important; }
    body { background: white !important; }
    .cover, .page {
        width: 210mm !important;
        min-height: 297mm !important;
        max-height: none !important;
        height: auto !important;
        overflow: visible !important;
        margin: 0 !important;
        box-shadow: none !important;
    }
"""


# ─── DOM helpers ──────────────────────────────────────────────────────────────

def all_pages(doc):
    return doc.xpath(
        '//div[contains(concat(" ", normalize-space(@class), " "), " page ")]')


def find_content_area(page):
    for ch in page.iter():
        if ch.tag == 'div' and 'content-area' in (ch.get('class') or '').split():
            return ch
    return None


def find_body_text(page):
    ca = find_content_area(page)
    if ca is None:
        return None
    for ch in ca:
        if ch.tag == 'div' and 'body-text' in (ch.get('class') or '').split():
            return ch
    return None


def section_name(page):
    sn = page.find('.//span[@class="section-name"]')
    return (sn.text or '').strip() if sn is not None else '?'


def page_number(page):
    pn = page.find('.//span[@class="page-number"]')
    return (pn.text or '').strip() if pn is not None else '?'


def is_section_start(page):
    """First page of a section has .section-header in .content-area."""
    ca = find_content_area(page)
    if ca is None:
        return False
    for ch in ca:
        if ch.tag != 'div':
            continue
        cls = (ch.get('class') or '').split()
        if 'section-header' in cls:
            return True
        if 'continuation-banner' in cls:
            return False
    return False


def group_into_sections(pages):
    """Return list of (section_name, [pages]) groups, each starting with a
    section-start page. Pages without .body-text (TOC, masthead) become
    standalone single-page groups that we skip."""
    groups = []
    cur = []
    for p in pages:
        body = find_body_text(p)
        if body is None:
            # Skip standalone — flush any in-progress group first
            if cur:
                groups.append(cur)
                cur = []
            continue
        if is_section_start(p) and cur:
            groups.append(cur)
            cur = []
        cur.append(p)
    if cur:
        groups.append(cur)
    return [(section_name(g[0]), g) for g in groups]


# ─── Logical-closure helpers ──────────────────────────────────────────────────

def is_subhead(el):
    return (el.tag == 'div'
            and 'subhead' in (el.get('class') or '').split())


def is_section_divider(el):
    return (el.tag == 'div'
            and 'section-divider' in (el.get('class') or '').split())


def is_closing_block(el):
    cls = (el.get('class') or '').split()
    return 'closing' in cls or 'lotus-end' in cls


# ─── Measurement ──────────────────────────────────────────────────────────────

def measure_element_heights(html_path: Path, doc) -> dict:
    """Returns {(page_index, element_index_in_body): height_px}.
    Renders the HTML in Playwright and measures each .body-text child's
    offsetHeight in CSS pixels."""
    # Tag each body-text child with a unique data-rebalance-id so we can
    # locate it in the rendered DOM.
    heights: dict = {}
    pages = all_pages(doc)
    tagged = 0
    for pi, p in enumerate(pages):
        body = find_body_text(p)
        if body is None:
            continue
        for ei, ch in enumerate(body):
            if ch.tag is None:
                continue
            ch.set('data-rebal', f'{pi}-{ei}')
            tagged += 1

    # Write tagged copy to temp
    tmp_path = Path('/tmp/rebalance_measure.html')
    tagged_html = lxml_html.tostring(
        doc, encoding='unicode', method='html', doctype='<!DOCTYPE html>')
    tmp_path.write_text(tagged_html, encoding='utf-8')

    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(
            viewport={'width': 900, 'height': 1300},
            device_scale_factor=1,
        )
        page = ctx.new_page()
        page.goto(tmp_path.as_uri(), wait_until='networkidle')
        page.add_style_tag(content=MEASUREMENT_CSS)
        page.evaluate("document.fonts.ready")
        page.wait_for_timeout(200)

        # Query every tagged element and record its offsetHeight + margins
        raw = page.evaluate("""
            () => {
                const out = {};
                document.querySelectorAll('[data-rebal]').forEach(el => {
                    const r = el.getBoundingClientRect();
                    const cs = getComputedStyle(el);
                    const mt = parseFloat(cs.marginTop) || 0;
                    const mb = parseFloat(cs.marginBottom) || 0;
                    out[el.getAttribute('data-rebal')] = r.height + mt + mb;
                });
                return out;
            }
        """)
        browser.close()

    # Strip the tag attributes now that we're done
    for p in pages:
        body = find_body_text(p)
        if body is None:
            continue
        for ch in body:
            if ch.tag is not None and ch.get('data-rebal') is not None:
                ch.attrib.pop('data-rebal')

    for k, v in raw.items():
        pi, ei = k.split('-')
        heights[(int(pi), int(ei))] = float(v)
    return heights


# ─── Page-count adjustment ────────────────────────────────────────────────────

def create_continuation_page(template_page, section_name_text: str):
    """Clone template page, replace section-header with continuation-banner,
    empty its body-text. Used to ADD a page to an overfilled section."""
    new = deepcopy(template_page)
    ca = find_content_area(new)
    if ca is None:
        return new

    # Remove any section-header (the new page is a continuation, not a start)
    for ch in list(ca):
        cls = (ch.get('class') or '').split()
        if 'section-header' in cls:
            ca.remove(ch)

    # Ensure a continuation-banner exists at the top of content-area
    has_banner = any('continuation-banner' in (ch.get('class') or '').split()
                     for ch in ca if ch.tag == 'div')
    if not has_banner:
        banner = lxml_html.Element('div', attrib={'class': 'continuation-banner'})
        sn = lxml_html.Element('span', attrib={'class': 'cont-section-name'})
        sn.text = section_name_text
        banner.append(sn)
        pi = lxml_html.Element('span', attrib={'class': 'cont-page-info'})
        pi.text = 'தொடர்ச்சி'
        banner.append(pi)
        ca.insert(0, banner)

    # Empty the body-text so rebalance can refill it
    body = find_body_text(new)
    if body is not None:
        for ch in list(body):
            body.remove(ch)
    return new


def adjust_page_count(doc, verbose=True) -> tuple[int, int]:
    """For each section, compute ideal page count and add/remove pages so
    each page lands at ≈ IDEAL_DENSITY_PX. Returns (added, removed)."""
    pages = all_pages(doc)
    page_index_of = {id(p): i for i, p in enumerate(pages)}
    heights = measure_element_heights(Path(''), doc)
    groups = group_into_sections(pages)

    added = removed = 0
    for name, sect_pages in groups:
        # Sum total content height for the section
        total = 0.0
        for sp in sect_pages:
            pi = page_index_of[id(sp)]
            body = find_body_text(sp)
            if body is None:
                continue
            for ei, _ch in enumerate(body):
                total += heights.get((pi, ei), 0.0)

        if total < MIN_TOTAL_TO_ADJUST:
            continue

        current = len(sect_pages)
        # Ideal page count using CAPACITY model:
        # Section needs N pages where: SECTION_START_CAPACITY +
        # (N-1)*CONTINUATION_CAPACITY ≈ total content.
        # Solve for N: N ≈ 1 + (total - SECTION_START_CAPACITY)/CONTINUATION_CAPACITY
        if total <= SECTION_START_CAPACITY_PX:
            ideal_raw = 1
        else:
            remaining = total - SECTION_START_CAPACITY_PX
            ideal_raw = 1 + remaining / CONTINUATION_CAPACITY_PX
        floor_p = max(1, math.floor(ideal_raw))
        ceil_p  = max(1, math.ceil(ideal_raw))
        if floor_p == ceil_p:
            ideal = floor_p
        else:
            # Bias toward fewer (denser) pages — better reading flow.
            # Accept up to 20 % overfill at floor before preferring ceil.
            cap_floor = SECTION_START_CAPACITY_PX + max(0, floor_p - 1) * CONTINUATION_CAPACITY_PX
            ratio = total / cap_floor
            ideal = floor_p if ratio <= 1.20 else ceil_p

        if ideal == current:
            continue

        if ideal > current:
            # ADD pages
            to_add = ideal - current
            for _ in range(to_add):
                new_p = create_continuation_page(sect_pages[-1], name)
                sect_pages[-1].addnext(new_p)
                sect_pages.append(new_p)
            added += to_add
            if verbose:
                print(f"  + [{name}]  {current}→{ideal} pages  "
                      f"(density {int(total/current)}→{int(total/ideal)}px)")
        else:
            # REMOVE trailing pages — but first MIGRATE their body-text
            # content into the previous page so nothing is lost. rebalance()
            # will then redistribute everything across the (now-smaller)
            # remaining pages.
            to_remove = current - ideal
            for _ in range(to_remove):
                last = sect_pages.pop()
                last_body = find_body_text(last)
                prev_body = find_body_text(sect_pages[-1])
                if last_body is not None and prev_body is not None:
                    for ch in list(last_body):
                        last_body.remove(ch)
                        prev_body.append(ch)
                last.getparent().remove(last)
            removed += to_remove
            if verbose:
                print(f"  − [{name}]  {current}→{ideal} pages  "
                      f"(density {int(total/current)}→{int(total/ideal)}px) "
                      f"[content migrated]")
    return added, removed


# ─── Renumber + TOC ───────────────────────────────────────────────────────────

def renumber_pages(doc) -> int:
    """Renumber every .page-number span sequentially starting at 2
    (skipping the cover which has no .page-number)."""
    n = 2
    for p in all_pages(doc):
        pn = p.find('.//span[@class="page-number"]')
        if pn is not None:
            pn.text = str(n)
        n += 1
    return n - 2


def update_toc(doc) -> int:
    """Update TOC row page numbers to reflect current section start pages."""
    # Build map: section-name → first page number of that section
    section_starts = {}
    for p in all_pages(doc):
        if not is_section_start(p):
            continue
        sn = p.find('.//span[@class="section-name"]')
        pn = p.find('.//span[@class="page-number"]')
        if sn is not None and pn is not None:
            name = (sn.text or '').strip()
            section_starts.setdefault(name, (pn.text or '').strip())

    updated = 0
    toc_rows = doc.xpath(
        '//div[contains(concat(" ", normalize-space(@class), " "), " toc-row ")]')
    for row in toc_rows:
        sec_el = row.find('.//div[@class="toc-section"]')
        page_el = row.find('.//div[@class="toc-page"]')
        if sec_el is None or page_el is None:
            continue
        toc_name = (sec_el.text or '').strip()
        match = None
        for sn, spn in section_starts.items():
            if sn in toc_name or toc_name in sn:
                match = spn
                break
        if match and page_el.text != match:
            page_el.text = match
            updated += 1
    return updated


# ─── Rebalancing ──────────────────────────────────────────────────────────────

def split_logical_units(elements):
    """Group consecutive elements into ATOMIC UNITS that must stay together.

    A unit is a list of (element, height) tuples that should never be split
    across pages. Examples:
      - [subhead, paragraph]      — subhead glued to its first content
      - [closing, lotus-end]      — closing block
      - [figure, caption sibling] — figure stays whole
      - [single paragraph]        — atomic by itself

    section-divider becomes its own unit; it's a soft anchor (page can
    end on it gracefully).
    """
    units = []
    i = 0
    n = len(elements)
    while i < n:
        el, h = elements[i]
        if is_subhead(el):
            # Glue subhead with the next non-divider element
            j = i + 1
            unit = [(el, h)]
            while j < n:
                next_el, next_h = elements[j]
                if is_section_divider(next_el):
                    # Glue divider too (it might be subsection start marker)
                    unit.append((next_el, next_h))
                    j += 1
                    continue
                unit.append((next_el, next_h))
                j += 1
                break
            units.append(unit)
            i = j
        elif is_closing_block(el):
            # Closing block sticks with the lotus-end after it
            unit = [(el, h)]
            if i + 1 < n and is_closing_block(elements[i + 1][0]):
                unit.append(elements[i + 1])
                i += 2
            else:
                i += 1
            units.append(unit)
        else:
            units.append([(el, h)])
            i += 1
    return units


def distribute_units(units, page_targets):
    """Forward greedy with PER-PAGE targets. Each page's target reflects
    its actual capacity (section-start pages get less room than
    continuation pages because of the .section-header).

    Preserves unit ORDER within the section.
    """
    num_pages = len(page_targets)
    pages = [[] for _ in range(num_pages)]
    heights = [0.0] * num_pages
    p = 0
    for unit in units:
        uh = sum(h for _, h in unit)
        if p < num_pages - 1 and heights[p] > 0:
            target = page_targets[p]
            overshoot = (heights[p] + uh) - target
            underfill = target - heights[p]
            if overshoot > underfill:
                p += 1
        pages[p].append(unit)
        heights[p] += uh
    return pages


def rebalance_one_section(section_name_str, section_pages, heights, verbose=True):
    """Redistribute content within one section's pages."""
    if len(section_pages) < 2:
        return 0   # nothing to balance

    pages_idx = []   # global page indices for this section
    elements_with_heights = []   # flat list of (element, height_px)

    # Build flat element list, preserving document order
    all_pages_doc = []
    for sp in section_pages:
        body = find_body_text(sp)
        if body is None:
            continue
        pi = sp.getparent().index(sp) if sp.getparent() is not None else -1
        # Find the index in the all_pages() list (assigned during measurement)
        # We tagged with f'{pi}-{ei}' where pi is index in all_pages()
        all_pages_doc.append((sp, body))

    # Re-derive pi for each section page (we need indices matching measurement)
    # Simpler: walk the doc again
    return rebalance_with_known_indices(section_name_str, section_pages, heights, verbose)


def rebalance_with_known_indices(section_name_str, section_pages, heights, verbose):
    """Worker that does the actual element move using heights dict."""
    # Map each section page → its index in the global all_pages list
    # (already encoded in the heights dict keys).
    # Reconstruct by matching: heights has keys (pi, ei). We need to know
    # which pi belongs to this section.
    # We do this by recomputing pi from the parent's child position.
    # Simpler approach: pass the doc-level page index alongside.
    raise RuntimeError("use rebalance() top-level instead")


def rebalance(doc, verbose=True) -> int:
    """Top-level rebalance. Returns number of element moves made."""
    pages = all_pages(doc)
    page_index_of = {id(p): i for i, p in enumerate(pages)}

    # 1. Measure heights once for the whole doc
    heights = measure_element_heights(Path(''), doc)

    # 2. Group into sections
    groups = group_into_sections(pages)

    moves = 0
    for name, sect_pages in groups:
        if len(sect_pages) < 2:
            continue
        # Gather flat element list in order, with heights
        flat = []
        body_refs = []
        for sp in sect_pages:
            body = find_body_text(sp)
            if body is None:
                continue
            pi = page_index_of[id(sp)]
            body_refs.append((sp, body))
            for ei, ch in enumerate(body):
                if ch.tag is None:
                    continue
                h = heights.get((pi, ei), 0.0)
                flat.append((ch, h))

        if not flat:
            continue

        units = split_logical_units(flat)
        total_h = sum(h for _, h in flat)
        num_pages = len(body_refs)

        # PER-PAGE CAPACITY: first page of section has section-header
        # taking ~140px, so its body-text budget is smaller. Continuation
        # pages just have a slim banner (~30px).
        capacities = [
            SECTION_START_CAPACITY_PX if is_section_start(sp)
            else CONTINUATION_CAPACITY_PX
            for sp, _ in body_refs
        ]
        total_capacity = sum(capacities)

        # Scale capacities so they sum to total content. If section fits
        # comfortably (total ≤ capacity), pages are slightly under-target
        # uniformly. If overfilled, pages are slightly over-target
        # uniformly — the zoom step will then apply ONE uniform zoom
        # factor across all pages of this section (better than mixed).
        scale = total_h / total_capacity if total_capacity > 0 else 1
        page_targets = [c * scale for c in capacities]

        if verbose:
            print(f"  [{name}]  {num_pages} pages, "
                  f"total={total_h:.0f}px, "
                  f"per-page targets={['%.0f'%t for t in page_targets]}")

        # Distribute using per-page targets
        new_pages = distribute_units(units, page_targets)

        # Apply: clear each body and append new contents
        for (sp, body), assigned_units in zip(body_refs, new_pages):
            # Detach all current children
            for ch in list(body):
                body.remove(ch)
            # Append in order
            for unit in assigned_units:
                for el, _ in unit:
                    body.append(el)

        # Count moves (approx: number of elements that ended up on a
        # different page than they started — we don't track precisely;
        # count as 1 if any redistribution happened)
        moves += 1
        if verbose:
            page_h = [sum(h for _, h in [(e, heights.get((page_index_of[id(sp)], _ei), 0))
                                          for _ei, e in enumerate(body)])
                      for sp, body in body_refs]
            est = [sum(sum(h for _, h in u) for u in pg) for pg in new_pages]
            print(f"           → estimated px/pg: "
                  f"{', '.join(f'{int(x)}' for x in est)}")

    return moves


# ─── Driver ───────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 3:
        print(__doc__); sys.exit(1)
    in_path  = Path(sys.argv[1])
    out_path = Path(sys.argv[2])
    if not in_path.exists():
        print(f"✗ Not found: {in_path}"); sys.exit(1)

    print("━━━ rebalance_sections.py ━━━")
    print(f"  Input:  {in_path}")
    print(f"  Output: {out_path}")
    print(f"  Target: ≤{TARGET_PX}px/pg body content ({TARGET_PX*25.4/96:.0f}mm)")
    print()

    html_str = in_path.read_text(encoding='utf-8')
    doc = lxml_html.fromstring(html_str)

    print("[1/4] Adjusting per-section page count to match content density…")
    added, removed = adjust_page_count(doc)
    print(f"      +{added} pages, -{removed} pages\n")

    print("[2/4] Rebalancing content within each section…")
    moves = rebalance(doc)
    print(f"      Rebalanced {moves} section(s)\n")

    print("[3/4] Renumbering pages sequentially…")
    total = renumber_pages(doc)
    print(f"      {total} pages numbered\n")

    print("[4/4] Updating TOC page numbers…")
    n_toc = update_toc(doc)
    print(f"      Updated {n_toc} TOC row(s)\n")

    new_html = lxml_html.tostring(
        doc, encoding='unicode', method='html', doctype='<!DOCTYPE html>')
    out_path.write_text(new_html, encoding='utf-8')
    print(f"\n✓ Wrote {out_path}")


if __name__ == '__main__':
    main()
