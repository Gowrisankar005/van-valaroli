#!/usr/bin/env python3
"""
build_issue_html.py — Build a fresh issue's base HTML from author content.

Takes an Issue folder containing:
    issue_meta.json     issue identity + section order
    articles/*.md       one Magazine Markdown file per section
    images/             image assets (mirrored into source/Images alongside
                         templates/assets/'s shared logos — see sync_images())

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
import re
import shutil
import sys
from pathlib import Path

from mmd_parser import parse_mmd_file


HERE = Path(__file__).parent.resolve()
TEMPLATES = HERE / 'templates'
BASE_ASSETS = TEMPLATES / 'assets'
DEFAULTS_PATH = HERE / 'magazine_defaults.json'

# Theme-aware accent colors used in TOC rows (rotate through these)
TOC_COLORS = ['#8DC63F', '#D4AF37', '#2d7a3e', '#6BA82F']


def load_defaults() -> dict:
    """Load shared magazine defaults (masthead roles, compilers, cover rules)."""
    if DEFAULTS_PATH.exists():
        return json.loads(DEFAULTS_PATH.read_text(encoding='utf-8'))
    return {}


def derive_release_month(english_dates: str) -> str:
    """Extract the actual release month from an 'english_dates' range like
    'சூலை — ஆகத்து 2026' -> 'ஆகத்து' (the LAST month named is the release month,
    per Issue 01's imprint convention: '[ மே — 2026 ]' for a May 1 release).
    """
    if not english_dates:
        return ''
    last = english_dates.split('—')[-1].strip()
    return re.sub(r'\d+', '', last).strip()


def merge_masthead(meta: dict, defaults: dict) -> dict:
    """Build the masthead context: issue_meta.masthead overlays magazine_defaults.

    தொகுப்பாசிரியர்கள் (compilers) and the ordered roles list are magazine-wide
    defaults unless an issue explicitly sets them.
    """
    base = dict(defaults.get('masthead') or {})
    override = dict(meta.get('masthead') or {})
    # Shallow merge; nested lists from override replace entirely when present
    merged = {**base, **override}

    # Unified ordered roles (1 பொறுப்பு · 2 வெளியீடு · 3 பதிப்பு). Fall back
    # to legacy senior_roles + publisher_role if an old meta still uses them.
    if not merged.get('roles'):
        roles = list(base.get('roles') or [])
        if not roles:
            roles = []
            for r in (base.get('senior_roles') or []):
                roles.append(dict(r))
            pub = base.get('publisher_role') or {}
            if pub:
                entry = {
                    'label': pub.get('label', 'வெளியீட்டாளர்'),
                    'name': pub.get('name', ''),
                }
                if pub.get('title'):
                    entry['lines'] = [pub['title']]
                roles.append(entry)
        merged['roles'] = roles
    # Normalize: every role has a lines list + pre-rendered HTML (template
    # engine does not support nested {% for %} loops).
    for r in merged['roles']:
        if 'lines' not in r or r['lines'] is None:
            r['lines'] = []
        elif isinstance(r['lines'], str):
            r['lines'] = [r['lines']]
        r['lines_html'] = ''.join(
            f'<div class="masthead-contact-text">{line}</div>'
            for line in r['lines']
            if line
        )

    if not merged.get('youtube'):
        merged['youtube'] = base.get('youtube') or ''
    if not merged.get('compilers'):
        merged['compilers'] = base.get('compilers') or []
    if not merged.get('compilers_label'):
        merged['compilers_label'] = base.get('compilers_label') or 'தொகுப்பாசிரியர்கள்'
    if not merged.get('logos'):
        merged['logos'] = base.get('logos') or [
            'Images/van-logo.jpg',
            'Images/vallaroli-logo.jpg',
        ]
    return merged


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


def _find_block(tmpl: str, start: int, open_re, close_re, close_len_getter):
    """Starting right after an opening tag at `start`, scan forward counting
    NESTED opens/closes of the same kind to find the MATCHING close tag
    (balance-counting, not just the nearest close — nested {% for %}/{% if %}
    blocks need this or the wrong close gets picked, corrupting both the
    outer and inner block). Returns (inner_text, end_pos_after_close).
    """
    pos = start
    depth = 1
    while depth > 0:
        next_open = open_re.search(tmpl, pos)
        next_close = close_re.search(tmpl, pos)
        if not next_close:
            raise ValueError("unterminated block — missing endfor/endif")
        if next_open and next_open.start() < next_close.start():
            depth += 1
            pos = next_open.end()
        else:
            depth -= 1
            pos = next_close.end()
    inner_end = next_close.start()
    return tmpl[start:inner_end], pos


def _render_string(tmpl: str, ctx: dict) -> str:
    # {% for x in xs %}…{% endfor %} — balance-counted so nested for-loops
    # (e.g. a per-role {% for line in role.lines %} inside {% for role in … %})
    # resolve against their OWN endfor, not the first one found anywhere.
    for_open_re = re.compile(r'\{%\s*for\s+(\w+)\s+in\s+([\w.]+)\s*%\}')
    for_close_re = re.compile(r'\{%\s*endfor\s*%\}')
    while True:
        m = for_open_re.search(tmpl)
        if not m:
            break
        var, src_name = m.group(1), m.group(2)
        inner, end_pos = _find_block(tmpl, m.end(), for_open_re, for_close_re, None)
        items = _eval(src_name, ctx) or []
        out_parts = []
        for idx, item in enumerate(items):
            inner_ctx = dict(ctx)
            inner_ctx[var] = item
            # Provide loop.index0 for simple parity checks
            inner_ctx['loop'] = {'index0': idx, 'index': idx + 1}
            out_parts.append(_render_string(inner, inner_ctx))
        tmpl = tmpl[:m.start()] + ''.join(out_parts) + tmpl[end_pos:]

    # {% if expr %}…{% endif %} — same balance-counting approach.
    # Condition capture allows '%' inside the expression (e.g. "loop.index0 % 2")
    # by only excluding a '%' that is immediately followed by '}' — that's the
    # real closing delimiter. A plain [^%]+? would stop dead at the modulo
    # operator and never match the tag at all, leaving "{% if ... %}" as
    # literal text wherever a row-alternation condition like this is used.
    if_open_re = re.compile(r'\{%\s*if\s+((?:[^%]|%(?!\}))+?)\s*%\}')
    if_close_re = re.compile(r'\{%\s*endif\s*%\}')
    while True:
        m = if_open_re.search(tmpl)
        if not m:
            break
        cond_expr = m.group(1).strip()
        inner, end_pos = _find_block(tmpl, m.end(), if_open_re, if_close_re, None)
        val = _eval_condition(cond_expr, ctx)
        tmpl = tmpl[:m.start()] + (_render_string(inner, ctx) if val else '') + tmpl[end_pos:]

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

def build_teaser_list(sections: list, articles: dict,
                      meta: dict | None = None,
                      defaults: dict | None = None) -> list:
    """Generate cover-page teaser strings dynamically from this issue's sections.

    Priority:
      1. meta['cover_teasers'] — explicit list of strings (full override)
      2. Auto from sections: 'section_name — topic_title'
         - skips section_name in cover.skip_sections (default: அடுத்த இதழில்)
         - skips sec['on_cover'] == false
         - prefers article frontmatter title if topic_title empty
      3. Cap at cover.max_teasers (default 6) for cover layout space
    """
    meta = meta or {}
    defaults = defaults or {}
    cover_cfg = dict(defaults.get('cover') or {})
    cover_cfg.update(meta.get('cover') or {})

    # Full manual override (rare — only if editors want curated cover lines)
    if meta.get('cover_teasers'):
        max_n = int(cover_cfg.get('max_teasers', 6))
        return list(meta['cover_teasers'])[:max_n]

    skip = set(cover_cfg.get('skip_sections') or ['அடுத்த இதழில்'])
    max_n = int(cover_cfg.get('max_teasers', 6))

    teasers = []
    for sec in sections:
        if sec.get('on_cover') is False:
            continue
        name = sec.get('section_name', '').strip()
        if name in skip:
            continue
        title = (sec.get('topic_title') or '').strip()
        if not title and articles:
            art = articles.get(sec.get('file'), {})
            title = (art.get('meta') or {}).get('title', '').strip()
        if title:
            teasers.append(f"{name} — {title}")
        elif name:
            teasers.append(name)
        if len(teasers) >= max_n:
            break
    return teasers


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

    # 1. Load meta + shared defaults
    meta_path = issue_dir / 'issue_meta.json'
    if not meta_path.exists():
        print(f"  ✗ Missing {meta_path}")
        sys.exit(1)
    meta = json.loads(meta_path.read_text(encoding='utf-8'))
    defaults = load_defaults()
    masthead = merge_masthead(meta, defaults)
    print(f"  ✓ Loaded meta: Issue {meta['issue_number']} — "
          f"{meta['tamil_month']} {meta['year']}")
    if defaults:
        print(f"  ✓ Merged magazine_defaults.json "
              f"({len(masthead.get('compilers') or [])} compilers)")

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
        'tiruvalluvar_year': meta.get('tiruvalluvar_year', meta['year'] + 31),
        'release_month': meta.get('release_month') or derive_release_month(meta.get('english_dates', '')),
        'css_content': css,
    }

    # 5. Build structural pages
    print(f"\n  Rendering structural pages…")
    teasers = build_teaser_list(meta['sections'], articles, meta, defaults)
    print(f"  ✓ Cover teasers ({len(teasers)}):")
    for t in teasers:
        print(f"      ◆ {t}")

    cover_logos = masthead.get('logos') or ['Images/van-logo.jpg', 'Images/vallaroli-logo.jpg']
    cover_html = render(TEMPLATES / 'cover.html', {
        **base_ctx,
        'cover_image': find_cover_image(issue_dir / 'images'),
        'teasers': teasers,
        'logo_left': cover_logos[0],
        'logo_right': cover_logos[1] if len(cover_logos) > 1 else cover_logos[0],
        'publisher': masthead.get('publisher', ''),
    })

    imprint_html = render(TEMPLATES / 'imprint.html', base_ctx)

    masthead_html = render(TEMPLATES / 'masthead.html', {
        **base_ctx,
        'masthead': masthead,
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
        # Prefer meta topic_title; fall back to article frontmatter title.
        # Subtitle (e.g. பகுதி 1) comes from article YAML, optional override
        # via sec['topic_subtitle'].
        topic_title = (sec.get('topic_title') or
                       article['meta'].get('title') or '').strip()
        topic_subtitle = (sec.get('topic_subtitle') or
                          article['meta'].get('subtitle') or '').strip()
        article_html = render(TEMPLATES / 'article_page.html', {
            **base_ctx,
            'section_name': sec['section_name'],
            'topic_title': topic_title,
            'topic_subtitle': topic_subtitle,
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

    # 9. Sync images into source/Images so the built HTML can find them
    sync_images(issue_dir / 'images', output_html.parent / 'Images', BASE_ASSETS)


def sync_images(src: Path, dst: Path, base_assets: Path) -> None:
    """Mirror the issue's images + the shared base assets into dst.

    dst always ends up containing exactly: this issue's own images, plus the
    shared base assets (logos) — nothing else. Anything left over from a
    previously-built issue is removed, so dst can't silently accumulate
    cross-issue leftovers across builds (see CLAUDE.md PART 9).
    """
    dst.mkdir(parents=True, exist_ok=True)
    wanted = {}  # filename -> source path, for everything that should end up in dst
    for pool in (src, base_assets):
        if not pool.exists():
            continue
        for img in pool.iterdir():
            if not img.is_file() or img.name.startswith('.') or img.name == 'README.md':
                continue
            wanted[img.name] = img

    copied = 0
    for name, source_path in wanted.items():
        target = dst / name
        if not target.exists() or target.stat().st_size != source_path.stat().st_size:
            shutil.copy2(source_path, target)
            copied += 1

    removed = 0
    for existing in dst.iterdir():
        if existing.is_file() and existing.name not in wanted:
            existing.unlink()
            removed += 1

    if copied or removed:
        print(f"  ✓ Synced {copied} image(s), removed {removed} stale file(s) → {dst}")


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
