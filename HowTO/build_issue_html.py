#!/usr/bin/env python3
"""
build_issue_html.py — Build a fresh issue's base HTML from author content.

Takes an Issue folder containing:
    issue_meta.json     issue identity + section order
    articles/*.md       one Magazine Markdown file per section
    images/             image assets (copied to source/Images on first build)

Produces:
    A single base HTML file ready to feed into the rest of the pipeline
    (fix_html → rebalance → text-PDF).

Each article becomes ONE .page div initially; rebalance_sections.py later
expands sections that need more pages and distributes content evenly.

Usage:
    python build_issue_html.py <issue_folder> <output.html>

Example:
    python build_issue_html.py issues/Issue-02 source/VAN_Vaigasi2026.html
"""
import json
import shutil
import sys
from pathlib import Path

from mmd_parser import parse_mmd_file


HERE = Path(__file__).parent.resolve()
TEMPLATES = HERE / 'templates'

# Theme-aware accent colors used in TOC rows (rotate through these)
TOC_COLORS = ['#8DC63F', '#D4AF37', '#2d7a3e', '#6BA82F']


# ─── Tiny template engine (no jinja2 dependency) ─────────────────────────────

def render(template_path: Path, ctx: dict) -> str:
    """Render a template using simple {{ var }} and {% for ... %} {% endfor %}
    and {% if ... %} {% endif %} substitution. Avoids the jinja2 dependency.

    Supported:
      {{ var }}             — substitute value (HTML-escaped if not callable)
      {{ var | raw }}       — substitute without escaping
      {% for x in xs %}…{% endfor %}    — loop
      {% if expr %}…{% endif %}         — conditional (Python truthiness)
    """
    tmpl = template_path.read_text(encoding='utf-8')
    return _render_string(tmpl, ctx)


def _eval(expr: str, ctx: dict):
    """Resolve a dotted path like 'foo.bar' against ctx."""
    expr = expr.strip()
    parts = expr.split('.')
    cur = ctx
    for p in parts:
        if isinstance(cur, dict):
            cur = cur.get(p)
        else:
            cur = getattr(cur, p, None)
        if cur is None:
            return None
    return cur


def _render_string(tmpl: str, ctx: dict) -> str:
    # {% for x in xs %}…{% endfor %}
    import re
    for_pat = re.compile(
        r'\{%\s*for\s+(\w+)\s+in\s+([\w.]+)\s*%\}(.*?)\{%\s*endfor\s*%\}',
        re.DOTALL)
    while True:
        m = for_pat.search(tmpl)
        if not m:
            break
        var, src_name, inner = m.group(1), m.group(2), m.group(3)
        items = _eval(src_name, ctx) or []
        out_parts = []
        for idx, item in enumerate(items):
            inner_ctx = dict(ctx)
            inner_ctx[var] = item
            # Provide loop.index0 for simple parity checks
            inner_ctx['loop'] = {'index0': idx, 'index': idx + 1}
            out_parts.append(_render_string(inner, inner_ctx))
        tmpl = tmpl[:m.start()] + ''.join(out_parts) + tmpl[m.end():]

    # {% if expr %}…{% endif %}
    if_pat = re.compile(
        r'\{%\s*if\s+([^%]+?)\s*%\}(.*?)\{%\s*endif\s*%\}',
        re.DOTALL)
    while True:
        m = if_pat.search(tmpl)
        if not m:
            break
        cond_expr, inner = m.group(1).strip(), m.group(2)
        # Support simple expressions: var, var %2, etc.
        val = _eval_condition(cond_expr, ctx)
        tmpl = tmpl[:m.start()] + (inner if val else '') + tmpl[m.end():]

    # {{ var }} or {{ var | raw }}
    var_pat = re.compile(r'\{\{\s*([^}|]+?)(?:\s*\|\s*(\w+))?\s*\}\}')
    def sub_var(m):
        path, filt = m.group(1).strip(), m.group(2)
        val = _eval(path, ctx)
        if val is None:
            return ''
        s = str(val)
        return s  # we trust template content not to need escaping
    tmpl = var_pat.sub(sub_var, tmpl)
    return tmpl


def _eval_condition(expr: str, ctx: dict) -> bool:
    """Evaluate simple conditional expressions:
        var                  → truthy?
        var % N              → modulo (for row-alt detection)
    """
    if '%' in expr:
        left, _, right = expr.partition('%')
        l = _eval(left.strip(), ctx)
        try:
            r = int(right.strip())
            return bool((l or 0) % r)
        except ValueError:
            return False
    val = _eval(expr, ctx)
    return bool(val)


# ─── Build pipeline ──────────────────────────────────────────────────────────

def build_teaser_list(sections: list, articles: dict) -> list:
    """Generate the cover-page teaser strings from section + article info.
    Format: 'section_name — topic_title' (or just section_name if no title)."""
    teasers = []
    for sec in sections:
        title = sec.get('topic_title', '').strip()
        if title:
            teasers.append(f"{sec['section_name']} — {title}")
        else:
            teasers.append(sec['section_name'])
    return teasers[:6]   # cap at 6 for cover space


def build_toc_entries(sections: list, articles: dict, start_page: int = 5) -> list:
    """Build TOC rows: each section gets its starting page number (rough
    estimate; rebalance.update_toc will fix these precisely)."""
    entries = []
    page = start_page
    for i, sec in enumerate(sections):
        article = articles.get(sec['file'])
        # Estimate pages from content length (rough)
        chars = len(article['body_html']) if article else 1000
        est_pages = max(1, round(chars / 3500))
        entries.append({
            'section_name': sec['section_name'],
            'topic_title': sec.get('topic_title', ''),
            'page': str(page),
            'color': TOC_COLORS[i % len(TOC_COLORS)],
        })
        page += est_pages
    return entries


def find_cover_image(images_dir: Path) -> str:
    """Locate the cover image — looks for cover-image.{jpg,jpeg,png}."""
    for name in ('cover-image.jpg', 'cover-image.jpeg', 'cover-image.png',
                 'cover.jpg', 'cover.jpeg', 'cover.png'):
        p = images_dir / name
        if p.exists():
            return f'Images/{name}'
    # fallback
    return 'Images/cover-image.jpeg'


def build_issue(issue_dir: Path, output_html: Path) -> None:
    print(f"━━━ Build Issue HTML ━━━")
    print(f"  Issue dir: {issue_dir}")
    print(f"  Output:    {output_html}\n")

    # 1. Load meta
    meta_path = issue_dir / 'issue_meta.json'
    if not meta_path.exists():
        print(f"  ✗ Missing {meta_path}")
        sys.exit(1)
    meta = json.loads(meta_path.read_text(encoding='utf-8'))
    print(f"  ✓ Loaded meta: Issue {meta['issue_number']} — "
          f"{meta['tamil_month']} {meta['year']}")

    # 2. Parse each article
    articles_dir = issue_dir / 'articles'
    articles = {}
    for sec in meta['sections']:
        path = articles_dir / sec['file']
        if not path.exists():
            print(f"  ⚠ Missing article: {sec['file']}")
            articles[sec['file']] = {'meta': {}, 'body_html': '', 'warnings': []}
            continue
        articles[sec['file']] = parse_mmd_file(path)
        warnings = articles[sec['file']]['warnings']
        msg = f"  ✓ Parsed {sec['file']}"
        if warnings:
            msg += f"  ({len(warnings)} warning(s))"
        print(msg)

    # 3. Read CSS
    css = (TEMPLATES / 'magazine.css').read_text(encoding='utf-8')

    # 4. Build common context
    base_ctx = {
        'issue_number': meta['issue_number'],
        'tamil_month': meta['tamil_month'],
        'year': meta['year'],
        'year_tamil': meta.get('year_tamil', str(meta['year'])),
        'english_dates': meta.get('english_dates', ''),
        'special_label': meta.get('special_label', ''),
        'css_content': css,
    }

    # 5. Build structural pages
    print(f"\n  Rendering structural pages…")
    cover_html = render(TEMPLATES / 'cover.html', {
        **base_ctx,
        'cover_image': find_cover_image(issue_dir / 'images'),
        'teasers': build_teaser_list(meta['sections'], articles),
    })

    imprint_html = render(TEMPLATES / 'imprint.html', base_ctx)

    masthead_html = render(TEMPLATES / 'masthead.html', {
        **base_ctx,
        'masthead': meta.get('masthead', {
            'roles': [
                {'label': 'பொறுப்பாசிரியர்', 'name': 'மு. முத்துஜோதி'},
                {'label': 'பதிப்பாசிரியர்',   'name': 'தயவு கொமாரிசங்கர்'},
            ],
            'publisher': 'பெண்ணாடம் வள்ளலார் அறநிலையம்',
            'address':   'கடலூர் மாவட்டம், பெண்ணாடம்',
            'email':     'vallalararanilayampdm@gmail.com',
        }),
    })

    toc_html = render(TEMPLATES / 'toc.html', {
        **base_ctx,
        'toc_entries': build_toc_entries(meta['sections'], articles),
    })

    # 6. Build article pages — ONE .page per article initially.
    #    rebalance_sections.adjust_page_count will expand as needed.
    print(f"\n  Rendering article pages…")
    page_no = 5
    article_pages = []
    for sec in meta['sections']:
        article = articles[sec['file']]
        article_html = render(TEMPLATES / 'article_page.html', {
            **base_ctx,
            'section_name': sec['section_name'],
            'topic_title': sec.get('topic_title', ''),
            'author': article['meta'].get('author', ''),
            'body_html': article['body_html'],
            'page_number': page_no,
        })
        article_pages.append(article_html)
        page_no += 1   # placeholder; rebalance will renumber
        print(f"    ✓ {sec['section_name']}  (page {page_no - 1})")

    # 7. Stitch full document
    pages_html = '\n'.join([
        cover_html, imprint_html, masthead_html, toc_html,
        *article_pages,
    ])
    full_html = render(TEMPLATES / '_base.html', {
        **base_ctx,
        'pages_html': pages_html,
    })

    # 8. Write output
    output_html.parent.mkdir(parents=True, exist_ok=True)
    output_html.write_text(full_html, encoding='utf-8')
    size_kb = output_html.stat().st_size // 1024
    print(f"\n  ✓ Wrote {output_html}  ({size_kb} KB)")

    # 9. Sync images into source/Images if not present (so HTML can find them)
    sync_images(issue_dir / 'images', output_html.parent / 'Images')


def sync_images(src: Path, dst: Path) -> None:
    """Copy any images from issue folder that aren't already in source/Images."""
    if not src.exists():
        return
    dst.mkdir(parents=True, exist_ok=True)
    copied = 0
    for img in src.iterdir():
        if not img.is_file():
            continue
        if img.name.startswith('.') or img.name == 'README.md':
            continue
        target = dst / img.name
        if not target.exists() or target.stat().st_size != img.stat().st_size:
            shutil.copy2(img, target)
            copied += 1
    if copied:
        print(f"  ✓ Synced {copied} image(s) → {dst}")


# ─── CLI ─────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    issue_dir = Path(sys.argv[1]).resolve()
    output_html = Path(sys.argv[2]).resolve()
    if not issue_dir.is_dir():
        print(f"✗ Not a directory: {issue_dir}")
        sys.exit(1)
    build_issue(issue_dir, output_html)
