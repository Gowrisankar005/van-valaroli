#!/usr/bin/env python3
"""
fix_html.py — Post-process the magazine HTML to fix:

  1. Image paths: src="Content/Issue-01/foo.jpg" → src="Images/foo.jpg"

  2. Hanging subheads: subheads stranded at the bottom of a page (with
     their paragraph on the next page) are moved to the next page.

  3. www.van.org.in URL on the cover's publisher-row — REMOVED.

  4. Page-number centering: original CSS uses flex `justify-content:
     space-between` which puts the number geometrically between the
     left and right items (widths differ → visually off-centre).
     We inject CSS that absolutely-positions .page-number at horizontal 50%.

  5. Page 36 (அறநிலையச் செய்திகள் — Activities) image layout: original has
     6 images each floated right (cramped). Restructure each subsection
     into a clean 2-column image grid above its paragraphs.

Usage:
    python3 fix_html.py <input.html> <output.html>
"""
import sys
import re
from pathlib import Path
from lxml import html as lxml_html


# ─── 1. Image path rewrite ────────────────────────────────────────────────────

def fix_image_paths(html_str: str) -> tuple[str, int]:
    pattern = re.compile(r'src="Content/Issue-01/')
    count = len(pattern.findall(html_str))
    return pattern.sub('src="Images/', html_str), count


# ─── 2. Hanging-subhead detection & fix ───────────────────────────────────────

def is_subhead(el) -> bool:
    if el.tag != 'div':
        return False
    return 'subhead' in (el.get('class') or '').split()


def find_content_area(page_div):
    for child in page_div.iter():
        if child.tag == 'div' and 'content-area' in (child.get('class') or '').split():
            return child
    return None


def find_body_text(content_area):
    for child in content_area:
        if child.tag == 'div' and 'body-text' in (child.get('class') or '').split():
            return child
    return None


SKIP_AT_END_CLASSES = {'section-divider', 'lotus-end'}

def get_last_meaningful_child(container):
    for child in reversed(list(container)):
        if child.tag is None:
            continue
        classes = set((child.get('class') or '').split())
        if classes & SKIP_AT_END_CLASSES:
            continue
        if child.tag in ('p', 'div') and not (child.text_content() or '').strip():
            continue
        return child
    return None


def find_target_container(page_div):
    ca = find_content_area(page_div)
    if ca is None:
        return None
    bt = find_body_text(ca)
    return bt if bt is not None else ca


def fix_hanging_subheads_doc(doc) -> int:
    pages = doc.xpath('//div[contains(concat(" ", normalize-space(@class), " "), " page ")]')
    moved = 0
    for i in range(len(pages) - 1):
        cur, nxt = pages[i], pages[i + 1]
        cur_container = find_target_container(cur)
        nxt_container = find_target_container(nxt)
        if cur_container is None or nxt_container is None:
            continue
        last_el = get_last_meaningful_child(cur_container)
        if last_el is None or not is_subhead(last_el):
            continue
        subhead_text = (last_el.text_content() or '').strip()[:40]
        cur_container.remove(last_el)
        if 'body-text' in (nxt_container.get('class') or '').split():
            nxt_container.insert(0, last_el)
        else:
            insert_index = 0
            for j, child in enumerate(nxt_container):
                classes = (child.get('class') or '').split()
                if any(c in classes for c in ('continuation-banner',
                                              'section-header',
                                              'section-divider')):
                    insert_index = j + 1
                    continue
                break
            nxt_container.insert(insert_index, last_el)
        moved += 1
        print(f"  ✓ Moved subhead '{subhead_text}' from page {i+1} → page {i+2}")
    return moved


# ─── 3. Remove www.van.org.in ─────────────────────────────────────────────────

def remove_publisher_url_doc(doc) -> int:
    """Delete <span class='publisher-url'>www.van.org.in</span> wherever it lives."""
    nodes = doc.xpath('//span[contains(concat(" ", normalize-space(@class), " "), " publisher-url ")]')
    for n in nodes:
        n.getparent().remove(n)
    return len(nodes)


# ─── 4. Inject CSS for centered page-number + page-36 grid ────────────────────

CSS_INJECTION = """
<style id="fix-html-overrides">
    /* Center the page number on the printable page — not between the two
       sibling elements (issue-info + logo), which causes visual mis-centering. */
    .page-footer { position: relative !important; }
    .page-footer .page-number {
        position: absolute !important;
        left: 50% !important;
        top: 50% !important;
        transform: translate(-50%, -50%) !important;
        margin: 0 !important;
        z-index: 5 !important;
    }
    /* The logo on the right gets a tiny bottom offset so it sits on the same
       baseline as the issue-info after we absolute-position the number. */
    .page-footer .van-logo-footer { flex-shrink: 0; }

    /* ── Body text — reduce to industry-standard 11pt with tighter line-height.
       Original 12pt + 1.65 LH felt large; magazines typically use 10-11pt for
       print body text. This also packs ~15% more content per page,
       eliminating much of the trailing empty space. */
    .body-text {
        font-size: 11pt !important;
        line-height: 1.55 !important;
    }
    .body-text p {
        margin-bottom: 2.5mm !important;
    }
    .salutation {
        font-size: 11pt !important;
        line-height: 1.4 !important;
    }
    /* Subheads and box titles step DOWN proportionally */
    .subhead {
        font-size: 12pt !important;
    }
    .highlights-box {
        font-size: 11pt !important;
    }
    .highlights-box .box-title {
        font-size: 11.5pt !important;
    }

    /* ── Missing corner decorations: add top-right + bottom-left so all
       four corners carry the kolam motif (matches cover page). */
    .corner-tr, .corner-bl {
        position: absolute !important;
        font-size: 13pt !important;
        color: var(--van-brown, #8b6f47) !important;
        opacity: 0.09 !important;
        z-index: 1 !important;
        pointer-events: none !important;
    }
    .corner-tr { top: 3.5mm !important; right: 4.5mm !important; }
    .corner-bl { bottom: 3.5mm !important; left: 4.5mm !important; }

    /* ── Slim-quote — REDESIGNED for elegant magazine look.
       Removed restrictive top/bottom gold lines (felt like a frame).
       Added subtle LEFT vertical accent bar (typographic anchor without
       enclosure). Strip background tint for clean white. Better breathing
       room via increased outer margin, tighter inner padding.
       Captions/quotes now never overlap with floated images: clear:both.

       Poem alignment: centre the quote *block* on the page, but every
       verse line shares the same left edge as the first line
       (.verse-line blocks + text-align:left). Do NOT centre / justify
       each line (body-text justify must not stretch Tamil in poems). */
    .slim-quote {
        display: flex !important;
        justify-content: center !important;  /* centres the poem unit */
        margin: 6mm 14mm !important;
        padding: 2mm 0 2mm 6mm !important;
        border: none !important;
        border-left: 2pt solid var(--van-gold, #D4AF37) !important;
        border-radius: 0 !important;
        background: none !important;
        text-align: left !important;         /* never centre verse lines */
        clear: both !important;              /* never overlap with floats */
    }
    .slim-quote .quote-text {
        display: inline-block !important;
        text-align: left !important;         /* all lines start at same point */
        text-align-last: left !important;
        max-width: 100% !important;
        font-size: 11pt !important;
        line-height: 1.55 !important;
        font-style: italic !important;
        color: var(--van-deep, #2d7a3e) !important;   /* theme green */
        text-shadow: none !important;
        word-spacing: normal !important;
        letter-spacing: normal !important;
        overflow-wrap: normal !important;
        word-break: normal !important;
        hyphens: none !important;
    }
    .slim-quote .verse-line {
        display: block !important;
        text-align: left !important;
        text-align-last: left !important;
        white-space: normal !important;
    }
    .slim-quote .quote-text::before,
    .slim-quote .quote-text::after {
        display: none !important;      /* drop the ❝ ❞ marks; left bar is anchor */
    }
    .slim-quote .quote-source {
        font-size: 9pt !important;
        font-style: normal !important;
        color: #888 !important;
        margin-top: 2mm !important;
        letter-spacing: 0.2px !important;
    }
    .slim-quote + .slim-quote { margin-top: 3mm !important; }
    .slim-quote + .slim-quote .quote-text { font-size: 10.5pt !important; }

    /* ── Image captions — uniform centered alignment.
       Pre-existing CSS in source had inconsistent alignment per float
       type. Force ALL captions to center and italic for editorial look. */
    .img-caption, figure figcaption {
        text-align: center !important;
        font-size: 8.5pt !important;
        color: #666 !important;
        font-style: italic !important;
        margin-top: 1mm !important;
        line-height: 1.3 !important;
        display: block !important;
    }
    /* Floated figures: ensure caption width matches image width */
    .img-right, .img-left {
        text-align: center !important;
    }
    /* Prevent any quote/paragraph from overlapping a float image */
    .slim-quote, .highlights-box {
        clear: both !important;
    }

    /* ── UNIFORM FLOAT IMAGE SIZING — industry-standard magazine
       thumbnail. All float images become 60×45mm landscape with
       object-fit: cover (crops cleanly to fill). Caps the visual
       footprint so:
         (a) all float images look CONSISTENT in size
         (b) body text wraps fully around image (no orphan empty
             space below)
         (c) captions are uniform width
       Portrait sources (lotus flowers, etc.) get center-cropped to
       a wider landscape view — same as how editorial magazines size
       their photo thumbnails. */
    .img-right, .img-left {
        width: 60mm !important;
        max-width: 60mm !important;
    }
    .img-right {
        float: right !important;
        margin: 1mm 0 3mm 6mm !important;
        shape-margin: 4mm !important;
    }
    .img-left {
        float: left !important;
        margin: 1mm 6mm 3mm 0 !important;
        shape-margin: 4mm !important;
    }
    .img-right img, .img-left img {
        width: 60mm !important;
        height: 45mm !important;
        object-fit: cover !important;
        object-position: center !important;
        border-radius: 1mm !important;
        display: block !important;
        margin: 0 !important;
    }

    /* Banner & half-page images: not floated, keep at intended size
       but bound height so they never dominate a page. */
    .img-banner img {
        max-height: 75mm !important;
        object-fit: cover !important;
    }
    .img-half img {
        max-height: 80mm !important;
        object-fit: contain !important;
    }

    /* Subhead caption — when an explanatory line follows a subhead,
       style it as an attached subtitle rather than a regular paragraph. */
    .subhead-caption {
        font-size: 10pt !important;
        color: #666 !important;
        font-style: italic !important;
        margin: -2mm 0 4mm 4mm !important;
        line-height: 1.4 !important;
    }

    /* Thamarai (Sangam Ilakkiyam) section — alternate image float
       direction for visual rhythm. Default float is right; every even
       img-right inside .sangam-section becomes a left float.
       Implemented via :nth-of-type. */
    .sangam-section figure.article-figure.img-right:nth-of-type(2n) {
        float: left !important;
        margin: 0 6mm 4mm 0 !important;
    }

    /* Activities page: 2-column image grid for each subsection */
    .activities-image-grid {
        display: grid !important;
        grid-template-columns: 1fr 1fr !important;
        gap: 3mm !important;
        margin: 3mm 0 4mm !important;
        page-break-inside: avoid !important;
        break-inside: avoid !important;
    }
    .activities-image-grid figure {
        margin: 0 !important;
        text-align: center;
        page-break-inside: avoid !important;
    }
    .activities-image-grid img {
        width: 100% !important;
        height: 48mm !important;
        object-fit: cover !important;
        display: block !important;
        border-radius: 1.5mm !important;
        margin: 0 !important;
        float: none !important;
    }
    .activities-image-grid figcaption {
        font-size: 8pt !important;
        color: #666 !important;
        margin-top: 1mm !important;
        text-align: center !important;
        line-height: 1.3 !important;
    }
    /* Shared caption spans full width under both photos */
    .activities-image-grid > .activities-grid-caption,
    .activities-image-grid > figcaption.activities-grid-caption {
        grid-column: 1 / -1 !important;
        margin-top: 2mm !important;
        font-size: 9pt !important;
        font-weight: 600 !important;
        color: #444 !important;
    }

    /* Side-by-side pair for two .img-half images of differing aspect
       ratio (artifact/portrait photos) — height-capped, width follows
       naturally, nothing gets cropped. See .activities-image-grid above
       for the fixed-box variant used for same-shaped event photos. */
    .image-pair-row {
        display: flex !important;
        gap: 4mm !important;
        justify-content: center !important;
        align-items: flex-start !important;
        margin: 4mm 0 !important;
        page-break-inside: avoid !important;
        break-inside: avoid !important;
    }
    .image-pair-row figure {
        margin: 0 !important;
        text-align: center;
        flex: 0 1 auto !important;
        max-width: 48% !important;
    }
    .image-pair-row img {
        height: 55mm !important;
        max-height: 55mm !important;
        width: auto !important;
        max-width: 100% !important;
        object-fit: contain !important;
        display: block !important;
        margin: 0 auto !important;
        border: none !important;
        border-radius: 0 !important;
        float: none !important;
    }
    .image-pair-row figcaption {
        font-size: 8pt !important;
        color: #666 !important;
        margin-top: 1mm !important;
        text-align: center !important;
        line-height: 1.3 !important;
    }
</style>
"""


def inject_css(html_str: str) -> str:
    """Insert the override stylesheet right before </head>."""
    if 'id="fix-html-overrides"' in html_str:
        return html_str  # already injected, idempotent
    return html_str.replace('</head>', CSS_INJECTION + '\n</head>', 1)


# ─── 5b. Text-cleanup typos (stray characters left by markdown parsing) ──────

# Known stray-character patterns from source: a lone Tamil consonant
# appended after a sentence-ending period (e.g. "வாலன்.த"). Strip any
# 1-character trailing token following a period at end of paragraph.
STRAY_TAIL = re.compile(r'(\.)\s*[஀-௿]{1}\s*$')

def fix_stray_characters(doc) -> int:
    """Strip a single trailing Tamil character left after a period at the
    very end of a paragraph — a typical markdown-conversion artifact."""
    fixed = 0
    for p in doc.xpath('//p'):
        if p.text is None or len(p) > 0:
            continue
        m = STRAY_TAIL.search(p.text)
        if m:
            p.text = p.text[:m.start()] + '.'
            fixed += 1
    return fixed


# ─── 6. Subhead-caption detection ─────────────────────────────────────────────

def fix_subhead_captions(doc) -> int:
    """Detect paragraphs that follow a .subhead and start with '----' (literal
    em-dash artifact from markdown). Convert them to .subhead-caption styled
    subtitles attached visually to the preceding subhead."""
    fixed = 0
    for body in doc.xpath(
            '//div[contains(concat(" ", normalize-space(@class), " "), " body-text ")]'):
        children = list(body)
        for i, ch in enumerate(children):
            if (ch.tag == 'p'
                    and (ch.text or '').lstrip().startswith('----')
                    and i > 0
                    and children[i-1].tag == 'div'
                    and 'subhead' in (children[i-1].get('class') or '').split()):
                # Strip leading dashes + whitespace
                ch.text = (ch.text or '').lstrip('-').lstrip()
                ch.set('class', 'subhead-caption')
                fixed += 1
    return fixed


# ─── 7b. Add missing corner decorations (top-right + bottom-left) ─────────────

def add_missing_corners(doc) -> int:
    """Each .page has .corner-tl + .corner-br but lacks .corner-tr + .corner-bl.
    Insert them so all four corners carry the kolam motif (matches cover)."""
    added = 0
    for page in doc.xpath(
            '//div[contains(concat(" ", normalize-space(@class), " "), " page ")]'):
        existing = {(ch.get('class') or '') for ch in page if ch.tag == 'span'}
        # Find the existing corner-tl to anchor insertion (keeps order tidy)
        tl = None
        for ch in page:
            if ch.tag == 'span' and (ch.get('class') or '') == 'corner-tl':
                tl = ch
                break
        if not any('corner-tr' in c for c in existing):
            tr = lxml_html.Element('span', attrib={'class': 'corner-tr'})
            tr.text = '❈'
            if tl is not None:
                tl.addnext(tr)
            else:
                page.insert(0, tr)
            added += 1
        if not any('corner-bl' in c for c in existing):
            bl = lxml_html.Element('span', attrib={'class': 'corner-bl'})
            bl.text = '❈'
            # Just append; CSS positions it absolutely
            page.append(bl)
            added += 1
    return added


# ─── 7. Tag the Sangam section so CSS alternation works ───────────────────────

def tag_sangam_section(doc) -> int:
    """Add class .sangam-section to .page divs whose section-name contains
    'சங்க', so the alternating-image CSS rule can target them."""
    tagged = 0
    for page in doc.xpath(
            '//div[contains(concat(" ", normalize-space(@class), " "), " page ")]'):
        sn = page.find('.//span[@class="section-name"]')
        if sn is not None and 'சங்க' in (sn.text or ''):
            cls = (page.get('class') or '').split()
            if 'sangam-section' not in cls:
                cls.append('sangam-section')
                page.set('class', ' '.join(cls))
                tagged += 1
    return tagged


# ─── 5. Page-36 image reorganization ──────────────────────────────────────────

def reorganize_activities_page(doc) -> int:
    """Find the அறநிலையச் செய்திகள் page(s) and group any run of 2+
    CONSECUTIVE float figures (nothing else between them — no subhead, no
    paragraph) into a 2-column .activities-image-grid, in place.

    Only truly-adjacent figures are grouped; document order is otherwise
    left untouched, so each subsection's own heading/images/paragraphs stay
    together. (An earlier version of this function grouped EVERY figure on
    the page into one grid regardless of position, which scattered a page
    with several subsections into "all headings, one giant image block,
    all paragraphs" — see PART 9 lesson in CLAUDE.md.)

    Returns number of grids created (0 if not found / nothing to do).
    """
    pages = doc.xpath('//div[contains(concat(" ", normalize-space(@class), " "), " page ")]')
    grids_created = 0

    for page in pages:
        # Identify "activities" page: has section-name == 'அறநிலையச் செய்திகள்'
        section_name_el = page.find('.//span[@class="section-name"]')
        if section_name_el is None or 'அறநிலை' not in (section_name_el.text or ''):
            continue

        body = find_body_text(find_content_area(page))
        if body is None:
            continue

        children = list(body)
        new_children = []
        i = 0
        page_grids = 0
        while i < len(children):
            ch = children[i]
            cls = set((ch.get('class') or '').split())
            is_float_fig = ch.tag == 'figure' and ({'img-right', 'img-left'} & cls)
            if is_float_fig:
                run = [ch]
                j = i + 1
                while j < len(children):
                    cls2 = set((children[j].get('class') or '').split())
                    if children[j].tag == 'figure' and ({'img-right', 'img-left'} & cls2):
                        run.append(children[j])
                        j += 1
                    else:
                        break
                if len(run) >= 2:
                    grid = lxml_html.Element('div', attrib={'class': 'activities-image-grid'})
                    # One shared caption under the whole pair (first non-empty wins)
                    shared_caption = ''
                    for fig in run:
                        for cap in fig.findall('.//figcaption'):
                            t = (cap.text or '').strip()
                            if t and not shared_caption:
                                shared_caption = t
                            fig.remove(cap)
                        fig_classes = [c for c in (fig.get('class') or '').split()
                                       if c not in ('img-right', 'img-left', 'article-figure')]
                        fig.set('class', ' '.join(fig_classes) if fig_classes else 'article-figure')
                        grid.append(fig)
                    if shared_caption:
                        cap_el = lxml_html.Element(
                            'figcaption',
                            attrib={'class': 'img-caption activities-grid-caption'})
                        cap_el.text = shared_caption
                        grid.append(cap_el)
                    new_children.append(grid)
                    grids_created += 1
                    page_grids += 1
                else:
                    new_children.append(ch)
                i = j
            else:
                new_children.append(ch)
                i += 1

        if page_grids:
            for ch in list(body):
                body.remove(ch)
            for ch in new_children:
                body.append(ch)
            page_no = page.find('.//span[@class="page-number"]')
            page_label = (page_no.text if page_no is not None else '?')
            print(f"  ✓ Page {page_label}: grouped {page_grids} adjacent image pair(s) into grid(s)")

    return grids_created


# ─── 6. Pair up adjacent .img-half images anywhere in the document ───────────

def pair_adjacent_half_images(doc) -> int:
    """Group any run of 2+ CONSECUTIVE .img-half figures (nothing else
    between them) into the same 2-column grid used on the activities page
    — but document-wide, not just there. Two full-width-centered images
    stacked vertically each leave ~50mm of dead space on both sides and
    read inconsistently; side by side uses the width and reads as a
    deliberate comparison instead of two separate afterthought photos.

    Odd runs leave the last image out of the grid (stays solo/full-width)
    rather than forcing an awkward 3-up.
    """
    pages = doc.xpath('//div[contains(concat(" ", normalize-space(@class), " "), " page ")]')
    grids_created = 0

    for page in pages:
        ca = find_content_area(page)
        if ca is None:
            continue
        body = find_body_text(ca)
        if body is None:
            continue

        children = list(body)
        new_children = []
        i = 0
        page_grids = 0
        while i < len(children):
            ch = children[i]
            cls = set((ch.get('class') or '').split())
            is_half_fig = ch.tag == 'figure' and 'img-half' in cls
            if is_half_fig:
                run = [ch]
                j = i + 1
                while j < len(children):
                    cls2 = set((children[j].get('class') or '').split())
                    if children[j].tag == 'figure' and 'img-half' in cls2:
                        run.append(children[j])
                        j += 1
                    else:
                        break
                pair_count = len(run) - (len(run) % 2)
                for k in range(0, pair_count, 2):
                    # NOT .activities-image-grid — that forces a fixed
                    # 48mm height with object-fit:cover, tuned for same-
                    # ish landscape event photos. Artifact/portrait photos
                    # here vary wildly in aspect ratio (a tall figurine
                    # next to a squarish one); cropping to a fixed box
                    # would cut off real content. .image-pair-row instead
                    # caps height and lets width follow naturally, so nothing
                    # gets cropped.
                    grid = lxml_html.Element('div', attrib={'class': 'image-pair-row'})
                    for fig in run[k:k + 2]:
                        fig_classes = [c for c in (fig.get('class') or '').split()
                                       if c not in ('img-half', 'article-figure')]
                        fig.set('class', ' '.join(fig_classes))
                        grid.append(fig)
                    new_children.append(grid)
                    grids_created += 1
                    page_grids += 1
                for leftover in run[pair_count:]:
                    new_children.append(leftover)
                i = j
            else:
                new_children.append(ch)
                i += 1

        if page_grids:
            for ch in list(body):
                body.remove(ch)
            for ch in new_children:
                body.append(ch)
            page_no = page.find('.//span[@class="page-number"]')
            page_label = (page_no.text if page_no is not None else '?')
            print(f"  ✓ Page {page_label}: paired {page_grids} adjacent .img-half image(s) into grid(s)")

    return grids_created


# ─── Driver ───────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    in_path = Path(sys.argv[1])
    out_path = Path(sys.argv[2])
    if not in_path.exists():
        print(f"✗ Input file not found: {in_path}")
        sys.exit(1)

    print(f"━━━ fix_html.py ━━━")
    print(f"  Input:  {in_path}")
    print(f"  Output: {out_path}\n")

    html_str = in_path.read_text(encoding='utf-8')
    orig_size = len(html_str)

    print("[1/5] Fixing image paths (Content/Issue-01/ → Images/)…")
    html_str, n_paths = fix_image_paths(html_str)
    print(f"      Replaced {n_paths} path(s)\n")

    print("[2/5] Injecting CSS overrides (centered page numbers, grid styles)…")
    html_str = inject_css(html_str)
    print(f"      Done\n")

    # The remaining fixes work on the parsed DOM
    doc = lxml_html.fromstring(html_str)

    print("[3/5] Fixing hanging subheads…")
    n_subheads = fix_hanging_subheads_doc(doc)
    print(f"      Moved {n_subheads} subhead(s)\n")

    print("[4/5] Removing www.van.org.in from publisher row…")
    n_urls = remove_publisher_url_doc(doc)
    print(f"      Removed {n_urls} occurrence(s)\n")

    print("[5/9] Reorganizing Activities-page images into 2-column grids…")
    n_grids = reorganize_activities_page(doc)
    print(f"      Created {n_grids} image grid(s)\n")

    print("[5c/9] Pairing adjacent .img-half images document-wide…")
    n_pairs = pair_adjacent_half_images(doc)
    print(f"      Paired {n_pairs} image(s) into side-by-side row(s)\n")

    print("[5b/9] Stripping stray trailing characters from paragraphs…")
    n_stray = fix_stray_characters(doc)
    print(f"      Cleaned {n_stray} paragraph(s)\n")

    print("[6/7] Fixing '----' subhead captions…")
    n_caps = fix_subhead_captions(doc)
    print(f"      Converted {n_caps} paragraph(s) to subhead-caption\n")

    print("[7/8] Tagging Sangam section for alternating-image layout…")
    n_tagged = tag_sangam_section(doc)
    print(f"      Tagged {n_tagged} page(s)\n")

    print("[8/8] Adding missing top-right + bottom-left corner motifs…")
    n_corners = add_missing_corners(doc)
    print(f"      Added {n_corners} corner element(s)\n")

    html_str = lxml_html.tostring(doc, encoding='unicode',
                                  method='html', doctype='<!DOCTYPE html>')
    out_path.write_text(html_str, encoding='utf-8')

    print(f"✓ Wrote {out_path} "
          f"({len(html_str):,} bytes, {len(html_str) - orig_size:+,} change)")


if __name__ == '__main__':
    main()
