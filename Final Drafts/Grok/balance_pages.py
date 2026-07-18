#!/usr/bin/env python3
"""
balance_pages.py — Detect .page divs with excessive empty space and
fill them by pulling the first content element from the next page.

Uses Playwright to render the HTML and measure each .page's actual
content height. Iterates until either all pages are balanced or a max
iteration count is reached.

Definitions:
  * Content height: the rendered height of .content-area (excludes header
    and footer; matches what the magazine's reader experiences as
    "the writeable area").
  * Target zone: 240mm–290mm of content. Below 240mm = "underfilled"
    (worth filling). Above 290mm = "overfilled" (do not pull more in).
  * "First content element" = the first <p>/<div class="subhead">/
    <figure>/<div class="highlights-box">/<div class="slim-quote"> inside
    the next page's .body-text.

Iteration safety: max 30 passes. Each pass moves AT MOST one element
per underfilled page (single-shot moves are easier to back out if a
page tips into overfilled).

Usage:
    python3 balance_pages.py <input.html> <output.html>
"""
import sys
from pathlib import Path
from lxml import html as lxml_html
from playwright.sync_api import sync_playwright


# Tunable thresholds (millimetres of body-text height — actual content,
# not the flex-expanded .content-area container which always fills to 269mm).
UNDERFILL_BELOW = 220      # pull content forward if below this
OVERFILL_ABOVE  = 275      # never push a page above this
MAX_ITERATIONS  = 12
# Pull from next page only if next page has noticeably MORE content than
# current. This keeps the algorithm from draining successive light pages
# (it naturally averages adjacent pages without cascading).
PULL_DELTA_MM   = 25

# CSS injection used during measurement — lets pages render at their
# natural height so we can detect underfills.
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


def measure_content_heights(html_path: Path) -> list[float]:
    """Render the HTML once and return BODY-TEXT height in mm for each
    .page div. body-text is the actual content container; content-area
    is flex-expanded so it always reads ~269mm and is useless for
    detecting underfills."""
    heights_mm = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(
            viewport={'width': 900, 'height': 1300},
            device_scale_factor=1,
        )
        page = ctx.new_page()
        page.goto(html_path.as_uri(), wait_until='networkidle')
        page.add_style_tag(content=MEASUREMENT_CSS)
        page.evaluate("document.fonts.ready")
        page.wait_for_timeout(200)

        raw_heights = page.evaluate("""
            () => {
                const pages = document.querySelectorAll('.page');
                return Array.from(pages).map(p => {
                    const bt = p.querySelector('.body-text');
                    // If no .body-text (e.g. TOC, masthead pages), fall back
                    // to .content-area so we don't false-trigger an underfill.
                    if (bt && bt.offsetHeight > 0) return bt.offsetHeight;
                    const ca = p.querySelector('.content-area');
                    return ca ? ca.offsetHeight : 0;
                });
            }
        """)
        heights_mm = [h * 25.4 / 96 for h in raw_heights]
        browser.close()
    return heights_mm


def find_target_body(page_div):
    """Return the .body-text div inside the .page (where content lives)."""
    ca = None
    for ch in page_div.iter():
        if ch.tag == 'div' and 'content-area' in (ch.get('class') or '').split():
            ca = ch
            break
    if ca is None:
        return None
    for ch in ca:
        if ch.tag == 'div' and 'body-text' in (ch.get('class') or '').split():
            return ch
    return ca


def is_section_start_page(page_div) -> bool:
    """A page is the FIRST page of a section iff its .content-area contains
    a .section-header (vs a .continuation-banner used on follow-on pages).
    Pulling content backward across a section start would break section
    integrity — the byline or opening paragraph of the next article would
    bleed onto the previous article's final page.
    """
    ca = None
    for ch in page_div.iter():
        if ch.tag == 'div' and 'content-area' in (ch.get('class') or '').split():
            ca = ch
            break
    if ca is None:
        return False
    for ch in ca:
        if ch.tag != 'div':
            continue
        classes = (ch.get('class') or '').split()
        if 'section-header' in classes:
            return True
        if 'continuation-banner' in classes:
            return False
    return False


def is_subsection_start_page(page_div) -> bool:
    """A page is a 'subsection start' iff the first content element inside
    its .body-text is a <div class='subhead'>. Pulling backward from such
    a page would either (a) pull the subhead alone (leaving it stranded on
    current page with its paragraph still on next), or (b) pull the
    paragraph below it (orphaning the subhead alone on next page).
    Either way the subsection's integrity breaks, so refuse the pull.
    """
    body = find_target_body(page_div)
    if body is None:
        return False
    for ch in body:
        if ch.tag is None:
            continue
        classes = set((ch.get('class') or '').split())
        # Skip pure decorations at the very top
        if classes & {'section-divider'}:
            continue
        # If the first real element is a subhead → new subsection
        if ch.tag == 'div' and 'subhead' in classes:
            return True
        # Otherwise content begins normally (paragraph, figure, etc.)
        return False
    return False


CONTENT_TAGS_AT_FRONT = {'p', 'div', 'figure'}

def first_movable_element(body):
    """Return the first child of body that's a movable content element."""
    for ch in body:
        if ch.tag is None:
            continue
        # Don't move section-dividers or banners; they should stay anchored
        classes = set((ch.get('class') or '').split())
        if classes & {'section-divider', 'continuation-banner', 'section-header'}:
            continue
        if ch.tag in CONTENT_TAGS_AT_FRONT:
            return ch
    return None


def last_movable_element(body):
    """Return the last child of body that's a movable content element.
    Used by push-backward to relieve overfilled pages."""
    for ch in reversed(list(body)):
        if ch.tag is None:
            continue
        classes = set((ch.get('class') or '').split())
        # Never push out structural decorations or closing blocks
        if classes & {'section-divider', 'lotus-end', 'closing'}:
            continue
        if ch.tag in CONTENT_TAGS_AT_FRONT:
            return ch
    return None


def append_to_body(body, el):
    """Append element to end of body. Avoid creating empty trailing
    text-only siblings."""
    body.append(el)


def balance_once(html_str: str) -> tuple[str, int, list[float]]:
    """One balancing pass. Returns (new_html, moves_done, heights_after)."""
    # First, write current state to a temp file for Playwright to read
    tmp_path = Path('/tmp/balance_pages_tmp.html')
    tmp_path.write_text(html_str, encoding='utf-8')
    heights_before = measure_content_heights(tmp_path)

    # Parse for DOM manipulation
    doc = lxml_html.fromstring(html_str)
    pages = doc.xpath(
        '//div[contains(concat(" ", normalize-space(@class), " "), " page ")]')

    moves = 0
    for i in range(len(pages) - 1):
        h = heights_before[i] if i < len(heights_before) else 0

        # ─── PUSH-BACKWARD (overfilled → next) ─────────────────────────
        # When current page exceeds OVERFILL_ABOVE its rendered height
        # is > 297mm. The screenshot captures that natural height; the
        # later resize-to-A4 compresses the content (smaller text). Move
        # the LAST element to the start of the next page to redistribute.
        if h > OVERFILL_ABOVE:
            # Same boundary guards as pull: don't push across sections
            # or subsections.
            if (not is_section_start_page(pages[i + 1])
                    and not is_subsection_start_page(pages[i + 1])):
                cur_body = None
                nxt_body = None
                for ch in pages[i].iter():
                    if ch.tag == 'div' and 'body-text' in (ch.get('class') or '').split():
                        cur_body = ch
                        break
                for ch in pages[i + 1].iter():
                    if ch.tag == 'div' and 'body-text' in (ch.get('class') or '').split():
                        nxt_body = ch
                        break
                if cur_body is not None and nxt_body is not None:
                    last_el = last_movable_element(cur_body)
                    if last_el is not None:
                        cur_body.remove(last_el)
                        nxt_body.insert(0, last_el)
                        moves += 1
                        page_no_el = pages[i].find('.//span[@class="page-number"]')
                        page_no = page_no_el.text if page_no_el is not None else f'#{i+1}'
                        snippet = (last_el.text_content() or '').strip()[:50].replace('\n', ' ')
                        print(f"    ← push {page_no}→{int(page_no)+1}  "
                              f"({h:.0f}mm)  \"{snippet}…\"")
            # Skip pull-forward on this page (we just pushed).
            continue

        if h >= UNDERFILL_BELOW:
            continue  # this page is fine

        # GUARD: never pull across section boundaries. If the next page
        # starts a new section (.section-header instead of .continuation-banner),
        # its first content is the byline or opening paragraph of a new
        # article — moving that to fill the previous article's last page
        # breaks section integrity.
        if is_section_start_page(pages[i + 1]):
            continue

        # GUARD: never pull across subsection boundaries. If the next page's
        # body-text begins with a <div class='subhead'>, that's a new
        # subsection within the current article. Pulling from there would
        # either strand the subhead or its first paragraph.
        if is_subsection_start_page(pages[i + 1]):
            continue

        # GUARD: only pull from next page if next page has noticeably more
        # content. This naturally averages adjacent pages without cascading
        # drainage of late-section pages.
        nxt_h = heights_before[i + 1] if i + 1 < len(heights_before) else 0
        if nxt_h < h + PULL_DELTA_MM:
            continue  # next page doesn't have enough surplus

        # Find the body-text container; skip pages that have none
        # (e.g. masthead/TOC/cover-section pages don't have body-text)
        cur_body = None
        for ch in pages[i].iter():
            if ch.tag == 'div' and 'body-text' in (ch.get('class') or '').split():
                cur_body = ch
                break
        nxt_body = None
        for ch in pages[i + 1].iter():
            if ch.tag == 'div' and 'body-text' in (ch.get('class') or '').split():
                nxt_body = ch
                break
        if cur_body is None or nxt_body is None:
            continue

        # Don't pull from a next-page that's the last page of a section
        # ending with a closing/lotus block. Heuristic: skip if next page's
        # last meaningful element is a .closing or .lotus-end.
        # (Cheap protection against breaking sign-off blocks.)
        nxt_last = None
        for ch in reversed(list(nxt_body)):
            if ch.tag is not None:
                nxt_last = ch
                break
        if nxt_last is not None:
            last_classes = set((nxt_last.get('class') or '').split())
            if last_classes & {'closing', 'lotus-end'}:
                # Pull element only if next page has > 1 content element
                cnt = sum(1 for ch in nxt_body if ch.tag is not None)
                if cnt <= 2:
                    continue

        # Grab the first movable element from the next page
        el = first_movable_element(nxt_body)
        if el is None:
            continue

        # Move it
        nxt_body.remove(el)
        cur_body.append(el)
        moves += 1

        page_no_el = pages[i].find('.//span[@class="page-number"]')
        page_no = page_no_el.text if page_no_el is not None else f'#{i+1}'
        snippet = (el.text_content() or '').strip()[:50].replace('\n', ' ')
        print(f"    → page {page_no}  ({h:.0f}mm → +1 elem)  "
              f"\"{snippet}…\"")

    if moves == 0:
        return html_str, 0, heights_before

    new_html = lxml_html.tostring(
        doc, encoding='unicode', method='html', doctype='<!DOCTYPE html>')
    return new_html, moves, heights_before


def balance(html_str: str) -> str:
    """Iteratively rebalance until stable."""
    print("\n  Iterating until all pages reach ≥%dmm of content "
          "(or %d passes max)…\n" % (UNDERFILL_BELOW, MAX_ITERATIONS))
    total_moves = 0
    for it in range(1, MAX_ITERATIONS + 1):
        print(f"  Pass {it:>2}:")
        new_html, moves, heights = balance_once(html_str)
        if moves == 0:
            n_under = sum(1 for h in heights if 0 < h < UNDERFILL_BELOW)
            print(f"     ↳ no moves needed — {n_under} page(s) "
                  f"still under {UNDERFILL_BELOW}mm but next-page guards "
                  f"prevent further pulls.\n")
            break
        total_moves += moves
        html_str = new_html
    else:
        print(f"  Reached max iterations ({MAX_ITERATIONS}); stopping.\n")

    # Final measurement for reporting
    tmp_path = Path('/tmp/balance_pages_tmp.html')
    tmp_path.write_text(html_str, encoding='utf-8')
    final_heights = measure_content_heights(tmp_path)

    print(f"  Total moves: {total_moves}")
    print("\n  Final content heights (mm):")
    for i, h in enumerate(final_heights, 1):
        flag = '  ' if UNDERFILL_BELOW <= h <= OVERFILL_ABOVE else ('▼ ' if h < UNDERFILL_BELOW else '▲ ')
        print(f"    {flag}page {i:>2}: {h:>5.0f}")

    return html_str


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    in_path = Path(sys.argv[1])
    out_path = Path(sys.argv[2])
    if not in_path.exists():
        print(f"✗ Not found: {in_path}")
        sys.exit(1)

    print("━━━ balance_pages.py ━━━")
    print(f"  Input:  {in_path}")
    print(f"  Output: {out_path}")
    print(f"  Underfill threshold: {UNDERFILL_BELOW}mm  "
          f"(A4 content area ≈ 280mm of writable height)")

    html_str = in_path.read_text(encoding='utf-8')
    balanced = balance(html_str)
    out_path.write_text(balanced, encoding='utf-8')
    print(f"\n✓ Wrote {out_path}")


if __name__ == '__main__':
    main()
