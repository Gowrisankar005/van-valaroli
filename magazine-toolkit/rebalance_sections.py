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

    # Write tagged copy next to the real source file — NOT /tmp. Images are
    # referenced with relative paths ("Images/foo.jpg"), which only resolve
    # against the source directory. A copy written to /tmp/ 404s on every
    # image, and each falls back to the browser's tiny broken-image size —
    # silently under-measuring every image-bearing element by 60-70%, which
    # then lets rebalance pack far more content onto a page than actually
    # fits once printed.
    tmp_path = html_path.resolve().parent / '_rebalance_measure_tmp.html'
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
        # .img-half/.img-right/.img-left all use height:auto with no
        # aspect-ratio reservation, so a not-yet-loaded <img> measures as
        # 0-height. networkidle doesn't guarantee decoded/laid-out images
        # for file:// pages, so without this wait, image-heavy pages get
        # under-counted and rebalance overpacks them — they then overflow
        # once actually printed. Wait for every image to finish loading.
        page.wait_for_function(
            "Array.from(document.images).every(img => img.complete)")
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

    tmp_path.unlink(missing_ok=True)

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

    # Remove section-header and author-byline (first-page only chrome)
    for ch in list(ca):
        cls = (ch.get('class') or '').split()
        if 'section-header' in cls or 'author-byline' in cls:
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


def adjust_page_count(doc, html_path: Path, verbose=True) -> tuple[int, int]:
    """For each section, compute ideal page count and add/remove pages so
    each page lands at ≈ IDEAL_DENSITY_PX. Returns (added, removed)."""
    pages = all_pages(doc)
    page_index_of = {id(p): i for i, p in enumerate(pages)}
    heights = measure_element_heights(html_path, doc)
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
            # Only stay at the denser floor page-count if content fits
            # (near) exactly — otherwise prefer ceil (one more page).
            # This used to tolerate up to 20% overfill at floor, relying
            # on build_text_pdf.py's per-page zoom to shrink text back
            # to fit. That zoom mechanism is a last-resort safety net for
            # small measurement error, not a layout strategy — leaning on
            # it this heavily produced visibly smaller type AND leftover
            # blank space (zoom shrinks the box without anything else
            # growing to fill the page), which reads as inconsistent
            # across the issue. Add the extra page instead.
            cap_floor = SECTION_START_CAPACITY_PX + max(0, floor_p - 1) * CONTINUATION_CAPACITY_PX
            ratio = total / cap_floor
            ideal = floor_p if ratio <= 1.03 else ceil_p

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
                if is_subhead(next_el):
                    # A nested heading (## immediately followed by ###,
                    # say) — don't consume it as this subhead's "content".
                    # Each subhead glues only to its OWN following content;
                    # otherwise two adjacent subheads glue to each other,
                    # both end up stranded without their real content, and
                    # rebalancing leaves a large under-filled gap on the
                    # page before whatever comes next.
                    break
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
        elif (el.tag == 'p'
              and el.text_content().strip().endswith((':', '：'))
              and i + 1 < n
              and not is_subhead(elements[i + 1][0])
              and not is_section_divider(elements[i + 1][0])
              and not is_closing_block(elements[i + 1][0])):
            # A paragraph ending in ":" introduces the element right after
            # it (a list, a quote, ...). Keep the two together, otherwise
            # the intro line can be stranded at a page bottom with its list
            # starting on the next page.
            units.append([(el, h), elements[i + 1]])
            i += 2
        else:
            units.append([(el, h)])
            i += 1

    # Second pass: a unit made ENTIRELY of subheads/dividers (no real
    # content) must never be left to stand alone — distribute_units could
    # place it at the very bottom of a page and defer the next unit (its
    # real content) to the following page, stranding the heading by
    # itself. Merge any such unit forward into whatever unit follows it.
    merged = []
    pending = []
    for u in units:
        combined = pending + u
        pending = []
        if all(is_subhead(e) or is_section_divider(e) for e, _h in combined):
            pending = combined
            continue
        merged.append(combined)
    if pending:
        merged.append(pending)
    return merged


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


def rebalance(doc, html_path: Path, verbose=True) -> int:
    """Top-level rebalance. Returns number of element moves made."""
    pages = all_pages(doc)
    page_index_of = {id(p): i for i, p in enumerate(pages)}

    # 1. Measure heights once for the whole doc
    heights = measure_element_heights(html_path, doc)

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


# ─── Post-redistribution verification / backfill ──────────────────────────────

# A section's last page may be left with at most this much blank space (px) after
# backfill pulls content forward from it; beyond that it would look too empty.
LAST_PAGE_MAX_GAP_PX = 500


def backfill_underfilled_pages(doc, html_path: Path, threshold_px: float = 60,
                                max_rounds: int = 4, verbose: bool = True) -> int:
    """rebalance() decides page boundaries using PRE-measured element heights
    (measured while each element still sits in its ORIGINAL position, before
    anything moved). That estimate can diverge from the truth — text wrapping
    around a floated figure measures differently depending on what float
    context it's actually rendered next to, margins collapse differently once
    neighbours change, etc. The result: a page can end up with real, rendered
    blank space at the bottom even though the estimate said it was full.

    This does the opposite of estimation: render the ACTUAL current doc,
    measure the real gap between each page's body-text and its footer, and
    if that gap is large enough to fit the next page's leading paragraph(s)
    (never a subhead — that must stay glued to its own content), move them
    up. Repeats a few rounds since one move can free room for another.

    Returns total number of elements moved.
    """
    total_moved = 0

    for round_i in range(max_rounds):
        tmp_path = html_path.resolve().parent / '_rebalance_backfill_tmp.html'
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
            page.evaluate("document.fonts.ready")
            page.wait_for_function(
                "Array.from(document.images).every(img => img.complete)")
            page.wait_for_timeout(200)
            # For each page: real gap to footer, PLUS the actual rendered
            # height of its own first body-text child (the pull candidate
            # if some earlier page wants to backfill FROM this page).
            # Using this page's real measured height — not a guessed
            # constant — is what keeps a pull from silently overflowing
            # the page it lands on.
            info = page.evaluate("""
                () => Array.from(document.querySelectorAll('.page')).map(p => {
                    const bt = p.querySelector('.body-text');
                    const footer = p.querySelector('.page-footer');
                    if (!bt || !footer) return null;
                    const btRect = bt.getBoundingClientRect();
                    const footerRect = footer.getBoundingClientRect();
                    const gap = Math.round(footerRect.top - btRect.bottom);
                    const first = bt.firstElementChild;
                    if (!first) return {gap, firstH: null, firstIsSubhead: false};
                    const cs = getComputedStyle(first);
                    const h = first.getBoundingClientRect().height
                        + parseFloat(cs.marginTop) + parseFloat(cs.marginBottom);
                    const isSubhead = (first.className || '').split(' ').includes('subhead');
                    return {gap, firstH: Math.round(h), firstIsSubhead: isSubhead};
                })
            """)
            browser.close()
        tmp_path.unlink(missing_ok=True)

        pages = all_pages(doc)
        page_index_of = {id(p): i for i, p in enumerate(pages)}
        groups = group_into_sections(pages)

        moved_this_round = 0
        for name, sect_pages in groups:
            if len(sect_pages) < 2:
                continue
            for idx in range(len(sect_pages) - 1):
                cur = sect_pages[idx]
                nxt = sect_pages[idx + 1]
                cur_i = page_index_of[id(cur)]
                nxt_i = page_index_of[id(nxt)]
                if cur_i >= len(info) or info[cur_i] is None:
                    continue
                if nxt_i >= len(info) or info[nxt_i] is None:
                    continue
                gap = info[cur_i]['gap']
                if gap < threshold_px:
                    continue
                nxt_first_h = info[nxt_i]['firstH']
                nxt_first_is_subhead = info[nxt_i]['firstIsSubhead']
                # A subhead must stay glued to its own content (handled by
                # the earlier rebalance pass) — don't drag it along by
                # height alone, that would strand it again elsewhere.
                if nxt_first_h is None or nxt_first_is_subhead:
                    continue
                # Real measured height, with a small safety margin, must
                # actually fit the real gap — no guessing.
                if nxt_first_h + 10 > gap:
                    continue
                # Net-improvement check: pulling this element empties it out
                # of nxt, so nxt's OWN gap grows by roughly nxt_first_h. If
                # that would leave nxt worse off than cur is right now, this
                # isn't fixing anything — it's just relocating the same
                # blank space one page later (and across several rounds,
                # cascading it all the way to the section's last page,
                # which is worse than where it started).
                nxt_gap_after = info[nxt_i]['gap'] + nxt_first_h
                # Exception: blank space at the bottom of a section's LAST
                # page is natural (the article just ends), so pulling content
                # forward from it is fine — as long as that last page stays
                # reasonably filled afterwards.
                nxt_is_last = (idx + 1 == len(sect_pages) - 1)
                last_page_ok = nxt_is_last and nxt_gap_after < LAST_PAGE_MAX_GAP_PX
                if nxt_gap_after >= gap and not last_page_ok:
                    continue
                cur_body = find_body_text(cur)
                nxt_body = find_body_text(nxt)
                if cur_body is None or nxt_body is None or len(nxt_body) <= 1:
                    continue  # never fully drain nxt — that leaves a blank page
                first = nxt_body[0]
                cur_body.append(first)  # lxml re-parents (moves) the node
                moved_this_round += 1
                if verbose:
                    # Page-number text isn't finalized until renumber_pages()
                    # runs later in the pipeline, so use document position
                    # here rather than the (still stale) printed number.
                    print(f"  ✓ Backfilled 1 element ({nxt_first_h}px) in "
                          f"[{name}]: doc-page {nxt_i} → doc-page {cur_i}")

        total_moved += moved_this_round
        if moved_this_round == 0:
            break

    return total_moved


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

    print("[1/5] Adjusting per-section page count to match content density…")
    added, removed = adjust_page_count(doc, in_path)
    print(f"      +{added} pages, -{removed} pages\n")

    print("[2/5] Rebalancing content within each section…")
    moves = rebalance(doc, in_path)
    print(f"      Rebalanced {moves} section(s)\n")

    print("[3/5] Verifying real rendered fill + backfilling underfilled pages…")
    n_backfilled = backfill_underfilled_pages(doc, in_path)
    print(f"      Backfilled {n_backfilled} element(s)\n")

    print("[4/5] Renumbering pages sequentially…")
    total = renumber_pages(doc)
    print(f"      {total} pages numbered\n")

    print("[5/5] Updating TOC page numbers…")
    n_toc = update_toc(doc)
    print(f"      Updated {n_toc} TOC row(s)\n")

    new_html = lxml_html.tostring(
        doc, encoding='unicode', method='html', doctype='<!DOCTYPE html>')
    out_path.write_text(new_html, encoding='utf-8')
    print(f"\n✓ Wrote {out_path}")


if __name__ == '__main__':
    main()
