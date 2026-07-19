#!/usr/bin/env python3
"""
mmd_parser.py — Parse Magazine Markdown (MMD) files.

MMD is a strict subset of CommonMark plus 4 directive extensions for
magazine elements. See docs/MMD_Specification.md for the formal spec.

Public API:
    parse_mmd_file(path) → dict {
        'meta': {section, title, subtitle, author},
        'body_html': '<p>…</p><div class="subhead">…</div>…',
        'warnings': [list of soft issues],
    }

Supported MMD elements:
    Frontmatter           --- YAML ---
    Paragraphs            normal text, separated by blank lines
    Subheads              ## Subhead text
    Bullet lists          - item       (auto-wrapped in <ul>)
    Slim quote            :::quote source="…"  …verse…  :::
    Highlights box        :::box title="…"  …list…  :::
    Image                 :::image src="file.jpg" caption="…" type="float"  :::
    Closing block         :::closing  …text…  :::
"""
import re
import sys
from pathlib import Path
from html import escape


# ─── Frontmatter parsing (mini YAML — handles flat key: value lines) ────────

def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Strip the --- YAML --- block from top, return (meta_dict, rest)."""
    if not text.startswith('---'):
        return {}, text
    parts = text.split('---', 2)
    if len(parts) < 3:
        return {}, text
    fm_block, body = parts[1], parts[2]
    meta = {}
    for line in fm_block.strip().splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if ':' not in line:
            continue
        k, _, v = line.partition(':')
        meta[k.strip()] = v.strip().strip('"').strip("'")
    return meta, body.lstrip('\n')


# ─── Directive parsing — :::name attr="val" … ::: blocks ─────────────────────

DIRECTIVE_OPEN = re.compile(r'^:::(\w+)(?:\s+(.+?))?\s*$')
DIRECTIVE_CLOSE = re.compile(r'^:::\s*$')
ATTR_RE = re.compile(r'(\w+)=(?:"([^"]*)"|\'([^\']*)\'|(\S+))')


def parse_attrs(s: str) -> dict:
    """Parse attr="val" attr='val' attr=val pairs."""
    if not s:
        return {}
    attrs = {}
    for m in ATTR_RE.finditer(s):
        key = m.group(1)
        val = m.group(2) or m.group(3) or m.group(4) or ''
        attrs[key] = val
    return attrs


# ─── Block-level body parser ─────────────────────────────────────────────────

def parse_body(body: str, warnings: list) -> str:
    """Parse MMD body into HTML. Walks line by line, recognising:
       directive blocks (:::name … :::), subheads (##), lists (-),
       paragraphs (default)."""
    lines = body.splitlines()
    out = []
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        stripped = line.strip()

        # Blank line — skip
        if not stripped:
            i += 1
            continue

        # Directive block
        m = DIRECTIVE_OPEN.match(stripped)
        if m:
            name = m.group(1)
            attrs = parse_attrs(m.group(2) or '')
            # Collect lines until :::
            block_lines = []
            i += 1
            while i < n and not DIRECTIVE_CLOSE.match(lines[i].strip()):
                block_lines.append(lines[i])
                i += 1
            if i >= n:
                warnings.append(f"unclosed directive :::{name}")
            else:
                i += 1   # skip closing :::
            out.append(render_directive(name, attrs, block_lines, warnings))
            continue

        # Subhead
        if stripped.startswith('## '):
            text = stripped[3:].strip()
            out.append(f'<div class="subhead">{escape(text)}</div>')
            i += 1
            continue

        # Bullet list — collect consecutive `- ` lines
        if stripped.startswith('- '):
            items = []
            while i < n and lines[i].strip().startswith('- '):
                items.append(lines[i].strip()[2:].strip())
                i += 1
            li_html = ''.join(f'<li>{escape(it)}</li>' for it in items)
            out.append(f'<ul>{li_html}</ul>')
            continue

        # Article title (single #) — bypass (already in frontmatter)
        if stripped.startswith('# '):
            i += 1
            continue

        # Default: paragraph — collect until blank or directive/subhead
        para_lines = []
        while i < n:
            s = lines[i].strip()
            if not s:
                break
            if s.startswith('## ') or s.startswith('# '):
                break
            if s.startswith(':::'):
                break
            if s.startswith('- '):
                break
            para_lines.append(s)
            i += 1
        para_text = ' '.join(para_lines)
        if para_text:
            # First paragraph of body gets lead-para class
            cls = ' class="lead-para"' if not any('<p ' in o or '<p>' in o for o in out) else ''
            out.append(f'<p{cls}>{escape(para_text)}</p>')

    return '\n        '.join(out)


# ─── Directive renderers ─────────────────────────────────────────────────────

def render_directive(name: str, attrs: dict, lines: list, warnings: list) -> str:
    """Convert a :::name … ::: block into its HTML representation."""
    text = '\n'.join(lines).strip()

    if name == 'quote':
        source = attrs.get('source', '')
        # Each non-blank line becomes a verse line, joined by <br>
        verse_lines = [escape(L.strip()) for L in lines if L.strip()]
        verse_html = '<br>'.join(verse_lines)
        src_html = (f'<div class="quote-source">— {escape(source)}</div>'
                    if source else '')
        return (f'<div class="slim-quote">'
                f'<div class="quote-text">{verse_html}</div>'
                f'{src_html}</div>')

    if name == 'box':
        title = attrs.get('title', '')
        # Each `- item` becomes <li>
        items = []
        for L in lines:
            s = L.strip()
            if s.startswith('- '):
                items.append(s[2:].strip())
            elif s:
                items.append(s)
        li_html = ''.join(f'<li>{escape(it)}</li>' for it in items)
        title_html = (f'<div class="box-title">{escape(title)}</div>'
                      if title else '')
        return (f'<div class="highlights-box">'
                f'{title_html}<ul>{li_html}</ul></div>')

    if name == 'image':
        src = attrs.get('src', '')
        caption = attrs.get('caption', '')
        img_type = attrs.get('type', 'float')   # float | banner | half
        type_class = {
            'float': 'img-right',
            'banner': 'img-banner',
            'half': 'img-half',
        }.get(img_type, 'img-right')
        if not src:
            warnings.append("image directive missing src=")
            return ''
        return (f'<figure class="article-figure {type_class}">'
                f'<img src="Images/{escape(src)}" alt="{escape(caption)}">'
                f'<figcaption class="img-caption">{escape(caption)}</figcaption>'
                f'</figure>')

    if name == 'closing':
        # Each line becomes a closing-row; em-dash lines become sign-off
        rows = []
        for L in lines:
            s = L.strip()
            if not s:
                continue
            if s.startswith('—') or s.startswith('-'):
                # sign-off block
                rows.append(f'<div class="sign-off">{escape(s)}</div>')
            elif rows and 'sign-off' in rows[-1]:
                # name following sign-off
                rows.append(f'<div class="sign-name">{escape(s)}</div>')
            else:
                rows.append(f'<p>{escape(s)}</p>')
        rows.append('<div class="lotus-end">❀</div>')
        return f'<div class="closing">{"".join(rows)}</div>'

    warnings.append(f"unknown directive :::{name}")
    return f'<!-- unknown directive: {name} -->'


# ─── Public API ──────────────────────────────────────────────────────────────

def parse_mmd_file(path: Path) -> dict:
    """Parse one MMD file. Returns dict with 'meta', 'body_html', 'warnings'."""
    text = Path(path).read_text(encoding='utf-8')
    meta, body = parse_frontmatter(text)
    warnings: list[str] = []
    body_html = parse_body(body, warnings)
    return {
        'meta': meta,
        'body_html': body_html,
        'warnings': warnings,
    }


# ─── CLI test mode ───────────────────────────────────────────────────────────

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python mmd_parser.py <article.md>")
        sys.exit(1)
    result = parse_mmd_file(Path(sys.argv[1]))
    print("META:", result['meta'])
    print()
    print("BODY HTML:")
    print(result['body_html'])
    if result['warnings']:
        print()
        print("WARNINGS:", result['warnings'])
