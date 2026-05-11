#!/usr/bin/env python3
"""
Build VAN Vallaroli Chittirai 2026 v3.0
Full author content — zero condensation, zero cuts.
Only structural HTML wrapping applied.
"""
import re, sys, os, docx, zipfile

BASE    = '/Users/gowri/spaceclub/e-magazine'
CONTENT = f'{BASE}/Content/Issue-01'
SRC     = f'{BASE}/VAN_Vallaroli_Chittirai2026_v2_0_20260502.html'
OUT     = f'{BASE}/VAN_Vallaroli_Chittirai2026_v4_4_20260512.html'

# ════════════════════════════════════════════════════════════════════════════
# 1. EXTRACT STRUCTURAL PARTS FROM v2_0
# ════════════════════════════════════════════════════════════════════════════
with open(SRC, encoding='utf-8') as f:
    src_lines = f.readlines()

def find_line(pat):
    for i, l in enumerate(src_lines):
        if pat in l:
            return i
    raise ValueError(f'Pattern not found: {pat}')

i_cover    = find_line('<!-- PAGE 1 — COVER')
i_imprint  = find_line('<!-- PAGE 4 — IMPRINT')
i_masthead = find_line('<!-- PAGE 5 — CREDITS')
i_toc      = find_line('<!-- PAGE 6 — TABLE')
i_theme    = find_line('<div id="theme-picker">')

HEAD     = ''.join(src_lines[:i_cover])
COVER    = ''.join(src_lines[i_cover:i_imprint])
IMPRINT  = ''.join(src_lines[i_imprint:i_masthead])
MASTHEAD = ''.join(src_lines[i_masthead:i_toc])
TAIL     = ''.join(src_lines[i_theme:])

# Fix 1 — Imprint date: சித்திரை → மே
IMPRINT = IMPRINT.replace('[ சித்திரை — 2026 ]', '[ மே — 2026 ]')
IMPRINT = IMPRINT.replace('திருவள்ளுவர் ஆண்டு ௨௦௫௭ — சித்திரை',
                           'திருவள்ளுவர் ஆண்டு ௨௦௫௭ — வைகாசி')

# Fix title
HEAD = re.sub(r'<title>[^<]*</title>',
              '<title>வான் வளரொளி இதழ் — சித்திரை 2026 — இதழ் 1</title>', HEAD)

# Patch print CSS — ROOT CAUSE FIX (v4.3):
# The source CSS already uses flexbox on .page (display:flex, flex-direction:column)
# with .content-area { flex:1 } and .page-footer { margin-top:auto }.
# We must NOT override with max-height or position:absolute — those break the layout
# and clip bottom content (the "last few lines cut off" bug).
# Only add: overflow:hidden on page (boundary clip) + ensure page-break is set.
HEAD = HEAD.replace(
    '@media print {',
    '@media print {\n'
    '  /* v4.3 fix: let source flexbox layout control height — no max-height override */\n'
    '  .page { overflow: hidden !important; }\n'
    '  /* content-area fills space between header and footer via flex:1 — no clip needed */\n'
    '  .content-area { overflow: hidden !important; }\n'
    '  /* footer stays at bottom via margin-top:auto — no position:absolute needed */\n'
)

# Additional CSS patches — fix cover badge clipping and lead-para size
HEAD = HEAD.replace('</style>',
    '  /* keep cover badge within page — position above bottom-band to avoid teaser overlap */\n'
    '  .cover { position: relative !important; overflow: hidden !important; }\n'
    '  .cover-issue-badge { right: 10mm !important; bottom: calc(29% + 6mm) !important; }\n'
    '  /* harmonise lead-para with body text */\n'
    '  .lead-para { font-size: 12.5pt !important; line-height: 1.65 !important; }\n'
    '  /* issue-banner text always readable on dark background */\n'
    '  .issue-badge, .issue-title, .issue-subtitle { color: #fff8e8 !important; }\n'
    '  /* larger logos on imprint (page 2) and masthead (page 3) */\n'
    '  .imprint-logo { height: 44mm !important; max-width: 65mm !important; }\n'
    '  .masthead-logo { height: 44mm !important; max-height: 44mm !important; max-width: 65mm !important; }\n'
    '  /* Fix word-spacing in justified Tamil text — prevent stretched inter-word gaps */\n'
    '  .body-text p { word-spacing: normal !important; letter-spacing: normal !important; overflow-wrap: anywhere !important; }\n'
    '</style>'
)

# ════════════════════════════════════════════════════════════════════════════
# 2. MODIFY COVER PAGE
# ════════════════════════════════════════════════════════════════════════════
# Remove கல்வி சிறப்பிதழ் pill — actual class in HTML is "pill pill-special"
COVER = re.sub(r'\s*<span class="pill pill-special">[^<]*</span>', '', COVER)

# Fix teasers-label — strip "கல்வி சிறப்பிதழ் ·" prefix, keep "இந்த இதழில்"
COVER = re.sub(r'(<div class="teasers-label">)[^<]*(</div>)',
               r'\1இந்த இதழில்\2', COVER)

# Replace ALL teaser items inside <div class="teasers"> block
# Root cause: old regex stopped at first inner </div>; now match ALL teaser-item divs
new_teaser_items = (
    '\n        <div class="teaser-item"><span class="teaser-dot">&#x25C6;</span>'
    '<span class="teaser-text">திருக்குறள் — அறிவுடைமை அதிகாரம்</span></div>'
    '\n        <div class="teaser-item"><span class="teaser-dot">&#x25C6;</span>'
    '<span class="teaser-text">சங்க இலக்கியம் — தாமரையின் அறச்செய்தி</span></div>'
    '\n        <div class="teaser-item"><span class="teaser-dot">&#x25C6;</span>'
    '<span class="teaser-text">தமிழகக் கலைகள் — கோயில் கட்டிடக்கலை</span></div>'
    '\n        <div class="teaser-item"><span class="teaser-dot">&#x25C6;</span>'
    '<span class="teaser-text">ஒழுக்க வாழ்க்கை — வள்ளலாரின் நெறி</span></div>'
    '\n        <div class="teaser-item"><span class="teaser-dot">&#x25C6;</span>'
    '<span class="teaser-text">இயற்கை தரும் இன்பம் — மலை அழகு</span></div>'
    '\n        <div class="teaser-item"><span class="teaser-dot">&#x25C6;</span>'
    '<span class="teaser-text">சிறுகதை &nbsp;•&nbsp; நூல் மதிப்புரை &nbsp;•&nbsp; செய்திகள்</span></div>\n      '
)
# Match the FULL teasers block including all nested teaser-item divs, then outer </div>
COVER = re.sub(
    r'<div class="teasers">(\s*<div class="teaser-item">.*?</div>\s*)+</div>',
    '<div class="teasers">' + new_teaser_items + '</div>',
    COVER, flags=re.DOTALL
)

# Replace website with YouTube channel everywhere in cover
COVER = re.sub(
    r'(?:இணையதளம்\s*:\s*)?(?:www\.vallalar\.org|http[^\s<"\']*vallalar[^\s<"\']*)',
    'வலையொளி: https://www.youtube.com/@pennadamvallalararanilayam',
    COVER
)

# Also fix in TAIL (closing page / theme area if any)
TAIL = re.sub(
    r'(?:இணையதளம்\s*:\s*)?(?:www\.vallalar\.org|http[^\s<"\']*vallalar[^\s<"\']*)',
    'வலையொளி: https://www.youtube.com/@pennadamvallalararanilayam',
    TAIL
)
# Cut TAIL at the first </html> — everything after is old v2 junk pages
# The old regex failed because v2 page comments are multi-line (<!-- \n PAGE N)
html_end = TAIL.find('</html>')
if html_end != -1:
    TAIL = TAIL[:html_end + len('</html>')] + '\n'

# ════════════════════════════════════════════════════════════════════════════
# 2b. POST-PROCESS MASTHEAD — name order + YouTube replace
# ════════════════════════════════════════════════════════════════════════════
# Swap: வானதி should come before திருமுருகன் in the contributors list
MASTHEAD = re.sub(
    r'(<li>தயவு திருமுருகன்</li>\s*<li>தயவு வானதி</li>)',
    '<li>தயவு வானதி</li>\n              <li>தயவு திருமுருகன்</li>',
    MASTHEAD
)
# Replace website with YouTube channel
MASTHEAD = MASTHEAD.replace(
    '<div class="masthead-contact-heading">இணையதளம்:</div>',
    '<div class="masthead-contact-heading">வலையொளி:</div>'
)
MASTHEAD = MASTHEAD.replace('www.vallalar.org',
    'https://www.youtube.com/@pennadamvallalararanilayam')

# ════════════════════════════════════════════════════════════════════════════
# 3. PAGE-BUILDING HELPERS
# ════════════════════════════════════════════════════════════════════════════
ISSUE_INFO = "இதழ் எண்: 1 &nbsp;|&nbsp; சித்திரை 2026"
LOGO       = "Images/van-logo.jpg"

def sec_header(topic_title, section_label):
    return f'''      <div class="section-header">
        <div class="topic-title">{topic_title}</div>
        <div class="section-label-row">
          <span class="lotus-icon">❀</span>
          <span class="section-label">{section_label}</span>
          <span class="lotus-icon">❀</span>
        </div>
        <div class="title-underline"></div>
      </div>'''

def cont_banner(name, info='தொடர்ச்சி'):
    return f'''      <div class="continuation-banner">
        <span class="cont-section-name">{name}</span>
        <span class="cont-page-info">{info}</span>
      </div>'''

def make_page(num, section_name, header_html, body_html):
    return f'''
  <!-- PAGE {num} ═══════════════════════════════════════════════════════════ -->
  <div class="page">
    <div class="glossy"></div>
    <span class="corner-tl">❈</span>
    <span class="corner-br">❈</span>
    <div class="page-header">
      <span class="section-name">{section_name}</span>
      <span class="mag-name">வான் வளரொளி இதழ்</span>
    </div>
    <div class="content-area">
{header_html}
      <div class="section-divider">&#x2022; &nbsp;&nbsp; &#x2022; &nbsp;&nbsp; &#x2022;</div>
      <div class="body-text">
{body_html}
      </div>
    </div>
    <div class="page-footer">
      <span class="issue-info">{ISSUE_INFO}</span>
      <span class="page-number">{num}</span>
      <img class="van-logo-footer" src="{LOGO}" alt="VAN">
    </div>
  </div>'''

# HTML primitives
def pp(text, cls=''):
    c = f' class="{cls}"' if cls else ''
    return f'        <p{c}>{text}</p>'

def subhead(text):
    return f'        <div class="subhead">{text}</div>'

def divider():
    return '        <div class="section-divider">&#x2022; &nbsp;&nbsp; &#x2022; &nbsp;&nbsp; &#x2022;</div>'

def slim_quote(lines, source):
    body = '<br>\n          '.join(lines)
    return f'''        <div class="slim-quote">
          <div class="quote-text">{body}</div>
          <div class="quote-source">{source}</div>
        </div>'''

def highlights(title, items):
    lis = '\n'.join(f'            <li>{i}</li>' for i in items)
    return f'''        <div class="highlights-box">
          <div class="box-title">{title}</div>
          <ul>
{lis}
          </ul>
        </div>'''

def numbered_list(items):
    lis = '\n'.join(f'            <li>{i}</li>' for i in items)
    return f'''        <ol class="numbered-list">
{lis}
        </ol>'''

def byline(text):
    return f'        <div class="author-byline">{text}</div>'

def nl():
    return ''  # blank line in HTML output

# ── Weight-based page splitter ────────────────────────────────────────────
# Prevents content overflow/clip by estimating rendered height of each item.

def _item_weight(html_item):
    """Estimate rendered height in units (1 unit ≈ one body text line ~6.4mm).
    Float images (img-right/left) are assigned lower weight because text wraps
    alongside them — they share vertical space rather than blocking it fully."""
    s = html_item
    if 'article-figure' in s:
        if 'img-banner' in s:
            return 10   # full-width banner ~64mm (blocking — no wrap)
        elif 'img-half' in s:
            return 8    # centred half-width ~51mm (blocking — no wrap)
        else:
            return 5    # floated column img-right/left: text wraps alongside
    if 'highlights-box' in s:
        return 3 + s.count('<li>')
    if 'slim-quote' in s:
        return 3 + s.count('<br>') + 1
    if 'numbered-list' in s:
        return 2 + s.count('<li>')
    if 'subhead' in s:
        return 2
    if 'section-divider' in s:
        return 1
    if 'closing' in s:
        return 5
    if 'author-byline' in s or 'lotus-end' in s:
        return 1
    if 'lead-para' in s:
        text_len = len(re.sub(r'<[^>]+>', '', s))
        return max(2, text_len // 38)
    # Normal paragraph — estimate by character count (Tamil ~38 chars/line)
    text_len = len(re.sub(r'<[^>]+>', '', s))
    return max(1, text_len // 38)

# Target ~50 weight units per page:
# - 35 text lines × (1 unit/line) = 35; allow 15 units for images/verse overhead
# - Float images reduce effective cost; this calibration gives ~5 pages for thamarai
_PAGE_MAX_W = 50

def weight_split(items, max_w=_PAGE_MAX_W):
    """Split items into pages never exceeding max_w weight per page.
    Orphan guard: never ends a page on a subhead."""
    pages_out = []
    current = []
    current_w = 0
    for item in items:
        iw = _item_weight(item)
        if (current
                and current_w + iw > max_w
                and not current[-1].strip().startswith('<div class="subhead">')):
            pages_out.append(current)
            current = [item]
            current_w = iw
        else:
            current.append(item)
            current_w += iw
    if current:
        pages_out.append(current)
    return pages_out

# ── Section start-page tracker (used to build dynamic TOC) ────────────────
_sec_start = {}

def mark_sec(name):
    """Record current pn as the start page of a named section."""
    _sec_start[name] = pn

# ════════════════════════════════════════════════════════════════════════════
# 4. READ ALL CONTENT FILES
# ════════════════════════════════════════════════════════════════════════════
def read_docx(fname):
    try:
        doc = docx.Document(fname)
        result = []
        for p in doc.paragraphs:
            raw = p.text.strip().replace('\xa0', ' ')  # normalise Word nbsp
            if raw:
                # Split on internal newlines (some Word paras embed \n for sub-paragraphs)
                for part in raw.split('\n'):
                    part = part.strip()
                    if part:
                        result.append(part)
        return result
    except Exception as e:
        print(f'  docx fallback for {os.path.basename(fname)}: {e}')
        with zipfile.ZipFile(fname) as z:
            xml = z.read('word/document.xml').decode('utf-8', errors='ignore')
        raw = re.findall(r'<w:t[^>]*>([^<]+)</w:t>', xml)
        return [t.strip().replace('\xa0', ' ') for t in raw if t.strip()]

def read_md(fname):
    with open(fname, encoding='utf-8') as f:
        return f.read()

print('Reading content files...')
p01 = read_docx(f'{CONTENT}/01 - தலையங்கம்.docx')
p02 = read_docx(f'{CONTENT}/02-திருக்குறள்_அறிவுடைமை_ஓர் ஆய்வு.docx')
p03 = read_docx(f'{CONTENT}/03-kathai-புதுமைப்பித்தன்-01.docx')
p04 = read_docx(f'{CONTENT}/04-தமிழகக் கலைகள்-01.docx')
p05 = read_docx(f'{CONTENT}/05-ஓர்-ஒழுக்கம்.docx')
p06 = read_docx(f'{CONTENT}/06-VAN-Activities.docx')
md07 = read_md(f'{CONTENT}/07-book_review_md.md')
md08 = read_md(f'{CONTENT}/08-தாமரை_Dv2.md')
print(f'  01: {len(p01)} paras | 02: {len(p02)} | 03: {len(p03)} | 04: {len(p04)} | 05: {len(p05)} | 06: {len(p06)}')

# ════════════════════════════════════════════════════════════════════════════
# 5. BUILD CONTENT PAGES
# ════════════════════════════════════════════════════════════════════════════
pages = []
pn = 5  # content starts at page 5 (cover=1, imprint=2, masthead=3, toc=4)

# ── Helper: strip decorator lines ──────────────────────────────────────────
def is_deco(s):
    return re.match(r'^[─━═\-\•◆🪷❀ ]+$', s) is not None

def clean_paras(paras):
    return [p for p in paras if not is_deco(p) and len(p) > 1]

# ════════════════════════════════════════════════════════════════════════════
# PAGE 5–6: தலையங்கம் (EDITORIAL)
# ════════════════════════════════════════════════════════════════════════════
# p01 structure: [title, title2, salutation, paras..., 'இவ்விதழில்:', list items, closing, org, issue#...]
paras_01 = clean_paras(p01)

# Identify sections
# After clean_paras: [0]=title, [1]=subtitle, [2]="அன்பார்ந்த வாசகர்களே,", [3..]=body
title_01   = paras_01[0]   # வான் வளரொளி இதழ் - தலையங்கம்
subtitle_01 = paras_01[1]  # தமிழர்களின் அறநெறியும்...
salut_01   = paras_01[2]   # அன்பார்ந்த வாசகர்களே,
# Ensure salutation ends with comma
if not salut_01.endswith(','):
    salut_01 = salut_01.rstrip() + ','

# Body paragraphs before 'இவ்விதழில்'
body_paras = []
list_paras = []
closing_started = False
in_list = False

for i, t in enumerate(paras_01[3:], 3):
    if 'இவ்விதழில்' in t:
        in_list = True
        continue
    if in_list and any(t.startswith(x) for x in ['அன்புடன்', 'பெண்ணாடம்', 'இதழ்', 'மாதம்', 'வருடம்']):
        break
    if in_list:
        list_paras.append(t)
    elif 'இவ்விதழின் நோக்கம்' in t:
        body_paras.append(('subhead', t))
    elif t.startswith('────') or is_deco(t):
        pass
    else:
        body_paras.append(('para', t))

# Page 5 body — first ~8 paras
body_p5_items = body_paras[:8]
body_p5 = '\n'.join([
    pp(salut_01, 'lead-para'),
] + [
    subhead(txt) if kind == 'subhead' else pp(txt)
    for kind, txt in body_p5_items
])

mark_sec('தலையங்கம்')
pages.append(make_page(pn,
    'தலையங்கம்',
    sec_header('தமிழர் மாண்பு', 'தலையங்கம்'),
    body_p5
))
pn += 1

# Page 6 — remaining body + இவ்விதழில் list + closing
body_p6_items = body_paras[8:]
closing_lines = [
    pp(paras_01[-7]) if len(paras_01) > 7 else '',  # final para
]
# Find closing para
closing_para = next((t for _, t in reversed(body_p6_items) if len(t) > 40), '')
body_p6_parts = [subhead(txt) if kind == 'subhead' else pp(txt)
                 for kind, txt in body_p6_items if txt != closing_para]

list_clean = [t for t in list_paras if t and not is_deco(t) and t[0] in '🪷◆❀•' or len(t) > 5]
list_clean = [re.sub(r'^[🪷◆❀•]\s*', '', t) for t in list_clean if t]

body_p6 = '\n'.join(body_p6_parts + [
    highlights('இந்த இதழில்...', list_clean) if list_clean else '',
    divider(),
    pp(closing_para) if closing_para else '',
    f'''        <div class="closing">
          <div class="sign-off">அன்புடன்,</div>
          <div class="sign-name">மு. முத்துஜோதி</div>
          <div class="sign-title">பொறுப்பாசிரியர்</div>
          <div class="org-name">பெண்ணாடம் வள்ளலார் அறநிலையம்</div>
          <div class="lotus-end">❀</div>
        </div>''',
])

pages.append(make_page(pn,
    'தலையங்கம்',
    cont_banner('தலையங்கம்'),
    body_p6
))
pn += 1

# ════════════════════════════════════════════════════════════════════════════
# PAGE 7–10: திருக்குறள் — அறிவுடைமை
# ════════════════════════════════════════════════════════════════════════════
paras_02 = clean_paras(p02)
# Structure: title, முன்னுரை, intro paras..., then repeated blocks of:
#   [heading, குறள்: ..., (line1), (line2), விளக்கம்: ...]

def build_kural_html(paras):
    """Convert திருக்குறள் paragraphs to HTML."""
    html_parts = []
    i = 0
    while i < len(paras):
        t = paras[i]
        # Section headings — skip empty ones (immediately followed by another heading)
        if re.match(r'^(முன்னுரை|அறிவுடைமையின்|ஆய்வின்|முடிவுரை|அறிவின்)', t):
            next_t = paras[i+1] if i+1 < len(paras) else ''
            # Skip அறிவுடைமையின் பயன்கள் if empty (next para is also a heading)
            if 'அறிவுடைமையின் பயன்கள்' in t and re.match(r'^ஆய்வின்', next_t):
                i += 1; continue
            html_parts.append(subhead(t))
        # Kural intro: numbered (like "10. அறிவு ஒன்றே...")
        elif re.match(r'^\d+\.?\s+\S', t) and len(t) < 60:
            html_parts.append(subhead(t))
        # Kural subheading: short phrase immediately before a குறள்: line
        # e.g. "அறிவே அழிவற்ற கருவி", "மனதை நல்வழியில் செலுத்துதல்"
        elif (len(t) <= 45 and not t.endswith('.')
              and i + 1 < len(paras) and paras[i+1].startswith('குறள்:')):
            html_parts.append(subhead(t))
        # குறள்: line
        elif t.startswith('குறள்:'):
            kural_text = t.replace('குறள்:', '').strip()
            kural_lines = [kural_text] if kural_text else []
            j = i + 1
            while j < len(paras) and not paras[j].startswith('விளக்கம்'):
                if paras[j] and not paras[j].startswith('குறள்'):
                    kural_lines.append(paras[j])
                j += 1
            # Get விளக்கம்
            vilagam = ''
            if j < len(paras) and paras[j].startswith('விளக்கம்:'):
                vilagam = paras[j].replace('விளக்கம்:', '').strip()
                i = j
            # Inline kural number: "verse. 422." → "verse. — 422"
            if kural_lines:
                last = kural_lines[-1]
                m_num = re.search(r'\.\s*(\d+)\.\s*$', last)
                if m_num:
                    kural_lines[-1] = last[:m_num.start()].rstrip() + f'. — {m_num.group(1)}'
            html_parts.append(slim_quote(kural_lines, ''))
            if vilagam:
                html_parts.append(pp(vilagam))
        # விளக்கம் (standalone)
        elif t.startswith('விளக்கம்:'):
            html_parts.append(pp(t.replace('விளக்கம்:', '').strip()))
        # Bullet items (முடிவுரை section)
        elif t in ('அறிவு என்பது வாழ்க்கையின் மிகப் பெரிய செல்வம்.',
                   'அறிவுடன் ஒழுக்கமும் இணைந்தால் மட்டுமே அது முழுமை பெறும்.',
                   'ஆராய்ச்சி, சிந்தனை, அனுபவம் – இவை மூன்றும் சேர்ந்ததே உண்மையான அறிவு',
                   'அறிவில்லாத வாழ்க்கை தன்னைத்தானே அழிக்கும்.'):
            html_parts.append(pp(f'❀ {t}'))
        elif t in ('சுய கட்டுப்பாடு.', 'பகுத்தறிவு .', 'தொலைநோக்கு பார்வை .', 'சமூக இணக்கம்.'):
            html_parts.append(pp(f'&emsp;• {t}'))
        elif len(t) > 10:
            html_parts.append(pp(t))
        i += 1
    return html_parts

# Embed Thiruvalluvar image as base64
import base64
_tv_img_path = f'{CONTENT}/thiruvalluvar.jpeg'
if os.path.exists(_tv_img_path):
    with open(_tv_img_path, 'rb') as _f:
        _tv_b64 = base64.b64encode(_f.read()).decode()
    THIRUVALLUVAR_IMG = (
        f'        <figure class="article-figure img-half">'
        f'<img src="data:image/jpeg;base64,{_tv_b64}" alt="திருவள்ளுவர்">'
        f'<figcaption class="img-caption">திருவள்ளுவர்</figcaption>'
        f'</figure>'
    )
else:
    THIRUVALLUVAR_IMG = ''

kural_html = build_kural_html(paras_02[1:])  # skip title

def smart_chunk_kural(items, n_chunks):
    """Split kural HTML into n_chunks, never ending a chunk on a subhead line
    (which would orphan the kural verse + explanation on the next page)."""
    target = max(1, len(items) // n_chunks)
    chunks, current = [], []
    for item in items:
        current.append(item)
        if (len(current) >= target
                and len(chunks) < n_chunks - 1
                and not current[-1].strip().startswith('<div class="subhead">')):
            chunks.append(current)
            current = []
    if current:
        chunks.append(current)
    # Pad to n_chunks if needed
    while len(chunks) < n_chunks:
        chunks.append([])
    return chunks

kp = smart_chunk_kural(kural_html, 4)

mark_sec('திருக்குறள் ஆய்வு')
pages.append(make_page(pn, 'திருக்குறள் ஆய்வு',
    sec_header('திருக்குறள் அறிவுடைமை — ஒர் ஆய்வு', 'திருக்குறள் ஆய்வு'),
    '\n'.join([THIRUVALLUVAR_IMG] + kp[0])))
pn += 1
for part in kp[1:]:
    pages.append(make_page(pn, 'திருக்குறள் ஆய்வு',
        cont_banner('திருக்குறள் ஆய்வு'),
        '\n'.join(part)))
    pn += 1

# ════════════════════════════════════════════════════════════════════════════
# PAGE 11–14: சிறுகதை — பால்வண்ணம் பிள்ளை (4 pages — was 3, increased to prevent overflow)
# ════════════════════════════════════════════════════════════════════════════
paras_03 = clean_paras(p03)
# Structure: title, (pen-name), story paras..., citation, author bio paras

# Find where bio starts (after the citation line with em-dash and year)
bio_start = 0
for i, t in enumerate(paras_03):
    if re.search(r'(மணிக்கொடி|1934|1953|புதிய ஒளி)', t):
        bio_start = i
        break

story_paras = paras_03[2:bio_start]   # skip title and pen-name header
citation    = paras_03[bio_start] if bio_start else ''
bio_paras   = paras_03[bio_start+1:] if bio_start else []

# Build story HTML
story_html = []
for i, t in enumerate(story_paras):
    if i == 0:
        story_html.append(pp(t, 'lead-para'))
    else:
        story_html.append(pp(t))

# Split into 4 pages (v4.4: was 3 — increased to fix content overflow/cut-off)
sp = max(1, len(story_html) // 4)
s1 = story_html[:sp]
s2 = story_html[sp:2*sp]
s3 = story_html[2*sp:3*sp]
s4 = story_html[3*sp:]

mark_sec('சிறுகதை')
pages.append(make_page(pn, 'சிறுகதை',
    sec_header('பால்வண்ணம் பிள்ளை', 'சிறுகதை'),
    '\n'.join([byline('புதுமைப்பித்தன்')] + s1)))
pn += 1

pages.append(make_page(pn, 'சிறுகதை',
    cont_banner('சிறுகதை'),
    '\n'.join(s2)))
pn += 1

pages.append(make_page(pn, 'சிறுகதை',
    cont_banner('சிறுகதை'),
    '\n'.join(s3)))
pn += 1

# Last story page: story end + citation + bio
bio_html = [pp(t) for t in bio_paras]
pages.append(make_page(pn, 'சிறுகதை',
    cont_banner('சிறுகதை'),
    '\n'.join(s4 + [
        divider(),
        pp(citation) if citation else '',
        subhead('புதுமைப்பித்தன் — ஒரு அறிமுகம்'),
    ] + bio_html[:4])))
pn += 1

# ════════════════════════════════════════════════════════════════════════════
# PAGE 14–18: தமிழகக் கலைகள் — கோயில் கட்டிடக்கலை
# ════════════════════════════════════════════════════════════════════════════
paras_04 = clean_paras(p04)

def build_kalai_html(paras):
    html = []
    _TEMPLE_IMAGES = {
        'சலுவன்': ('Content/Issue-01/ancient-tamiltemple-01.jpg',
                   'சலுவன்குப்பம் முருகன் கோயில்'),
        'வேப்பத்தூர்': ('Content/Issue-01/ancient-tamiltemple-02.jpg',
                        'வேப்பத்தூர் பெருமாள் கோயில்'),
    }
    for i, t in enumerate(paras):
        # ── Section headings (MUST come before numbered-item check) ──────────
        # Matches: lines ending in ':', or lines starting with known section keywords.
        # "2. திருமால் கோட்டங்கள் (திருமாலிருங்குன்றம்)" must be a subhead,
        # not a numbered reference — so we check headings first.
        if (len(t) < 75
              and (t.endswith(':')
                   or re.match(
                       r'^[0-9.\s]*(கோட்டங்கள்|பழந்|சலுவன்|வேப்பத்|தனித்துவ்|மயிலை'
                       r'|குடவாயில்|திருமுருகன்\s+கோட்|திருமால்\s+கோட்|அகப்பொருள்'
                       r'|தமிழர் கோயில்|கோட்டம்\s*\()', t))):
            html.append(subhead(t))
            # Attach temple image immediately after its subheading
            for key, (img_src, caption) in _TEMPLE_IMAGES.items():
                if key in t:
                    html.append(
                        f'        <figure class="article-figure img-right">'
                        f'<img src="{img_src}" alt="{caption}">'
                        f'<figcaption class="img-caption">{caption}</figcaption>'
                        f'</figure>'
                    )
                    break

        # ── Numbered reference list items ────────────────────────────────────
        elif re.match(r'^\d+\.\s', t):
            html.append(pp(f'&emsp;{t}'))

        # ── Verse/poem lines: ASCII double-quote + ellipsis ─────────────────
        elif t[:1] == chr(34) and '...' in t:
            html.append(slim_quote([t], ''))

        # ── Short definition labels (கோட்டம் = ..., etc.) ───────────────────
        elif re.match(r'^(கோட்டம்|கோயில்|தளி)\s*=', t):
            html.append(pp(f'<strong>{t}</strong>'))

        elif i == 0:
            html.append(pp(t, 'lead-para'))
        else:
            html.append(pp(t))
    return html

kalai_html = build_kalai_html(paras_04[2:])  # skip title lines

chunk4 = max(1, len(kalai_html) // 5)
kparts = [kalai_html[i*chunk4:(i+1)*chunk4] for i in range(4)]
kparts.append(kalai_html[4*chunk4:])

mark_sec('தமிழகக் கலைகள்')
pages.append(make_page(pn, 'தமிழகக் கலைகள்',
    sec_header('தமிழகக் கோயிற் கட்டிடக் கலைகள் — ஓர் அறிமுகம்', 'தமிழகக் கலைகள்'),
    '\n'.join([byline('திருமுருகன்')] + kparts[0])))
pn += 1

for part in kparts[1:]:
    if part:
        pages.append(make_page(pn, 'தமிழகக் கலைகள்',
            cont_banner('தமிழகக் கலைகள்'),
            '\n'.join(part)))
        pn += 1

# ════════════════════════════════════════════════════════════════════════════
# PAGE (next): நூல் மதிப்புரை — வாசிப்பது எப்படி?
# Markdown → HTML
# ════════════════════════════════════════════════════════════════════════════
def md_to_html(md_text):
    """Convert markdown to HTML elements list."""
    lines = md_text.split('\n')
    html = []
    in_blockquote = False
    bq_lines = []

    def flush_bq():
        nonlocal in_blockquote, bq_lines
        if bq_lines:
            html.append(slim_quote(bq_lines, ''))
            bq_lines = []
        in_blockquote = False

    i = 0
    while i < len(lines):
        line = lines[i]

        # Skip image references
        if line.strip().startswith('!['):
            i += 1; continue

        # Horizontal rule → divider
        if re.match(r'^---+$', line.strip()):
            flush_bq()
            html.append(divider())
            i += 1; continue

        # Blockquote
        if line.startswith('>'):
            flush_bq()
            bq_text = re.sub(r'^>\s*', '', line).strip()
            if bq_text:
                bq_lines.append(bq_text)
            in_blockquote = True
            # Peek ahead for more bq lines
            while i+1 < len(lines) and lines[i+1].startswith('>'):
                i += 1
                bq_text = re.sub(r'^>\s*', '', lines[i]).strip()
                if bq_text:
                    bq_lines.append(bq_text)
            flush_bq()
            i += 1; continue

        flush_bq()

        # H1
        if line.startswith('# '):
            i += 1; continue  # skip top-level title (already in section-header)

        # H2
        if line.startswith('## '):
            text = re.sub(r'^##\s+', '', line).strip()
            text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
            html.append(subhead(text))
            i += 1; continue

        # H3
        if line.startswith('### '):
            text = re.sub(r'^###\s+', '', line).strip()
            text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
            html.append(subhead(text))
            i += 1; continue

        # H4
        if line.startswith('#### '):
            text = re.sub(r'^####\s+', '', line).strip()
            html.append(subhead(text))
            i += 1; continue

        # Unordered list
        if re.match(r'^[-*]\s', line):
            items = []
            while i < len(lines) and re.match(r'^[-*]\s', lines[i]):
                item = re.sub(r'^[-*]\s+', '', lines[i]).strip()
                item = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', item)
                items.append(item)
                i += 1
            html.append(highlights('', items) if len(items) > 2 else
                        '\n'.join(pp(f'• {it}') for it in items))
            continue

        # Numbered list
        if re.match(r'^\d+\.\s', line):
            items = []
            while i < len(lines) and re.match(r'^\d+\.\s', lines[i]):
                item = re.sub(r'^\d+\.\s+', '', lines[i]).strip()
                item = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', item)
                items.append(item)
                i += 1
            html.append(numbered_list(items))
            continue

        # Table → skip (rating tables don't translate well)
        if line.startswith('|'):
            i += 1; continue

        # Empty line
        if not line.strip():
            i += 1; continue

        # Normal paragraph
        text = line.strip()
        if not text:
            i += 1; continue

        # Apply inline markdown
        text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)  # strip links

        html.append(pp(text))
        i += 1

    return html

# ════════════════════════════════════════════════════════════════════════════
# PAGES: நூல் மதிப்புரை — 2-page crisp editorial review
# ════════════════════════════════════════════════════════════════════════════
nuul_body_p1 = '\n'.join([
    highlights('நூல் விவரம்', [
        '<strong>ஆசிரியர்:</strong> செல்வேந்திரன்',
        '<strong>வெளியீடு:</strong> எழுத்து பிரசுரம்',
        '<strong>பக்கங்கள்:</strong> 98 &nbsp;·&nbsp; <strong>விலை:</strong> ₹119',
        '<strong>வகை:</strong> வழிகாட்டி கட்டுரைத் தொகுப்பு',
        '<strong>மதிப்பீடு:</strong> ★★★★★',
    ]),
    pp('இன்று ஒவ்வொரு வீட்டிலும் கைப்பேசி இருக்கிறது; நூல் இல்லை. வீடியோ பார்க்கும் நேரம் மணிக்கணக்கில்; வாசிக்கும் நேரம் நிமிடக்கணக்கில். இந்தச் சூழலில் <em>வாசிப்பது எப்படி?</em> என்று கேட்பது தாமதமான கேள்வி அல்ல — தேவையான கேள்வி.', 'lead-para'),
    pp('தூத்துக்குடி மாவட்டம் சாத்தான்குளத்தில் வளர்ந்த செல்வேந்திரன் படிப்பில்லாத வீட்டில் பிறந்தார். அப்பாவின் தீப்பெட்டி வணிகத்தில் வேலை பார்த்தார்; தொலைதூரக் கல்வியில் பட்டம் பெற்றார். வாசிப்புதான் அந்த மாற்றத்தைக் கொண்டு வந்தது என்கிறார் — அதனை இந்த 98 பக்க நூலில் அலசுகிறார்.'),
    pp('"இந்நூலின் நோக்கம் அறிவுரை சொல்லுதல் அல்ல" என்று முன்னுரையிலேயே தெளிவாக்குகிறார். கல்வி, அரசியல், சினிமா, நிர்வாகம் என அனைத்து துறைகளிலும் வாசிப்பு குறைவால் ஏற்படும் சமூக இழப்பை விவரித்து, தீர்வை நோக்கி நம்மை அழைக்கிறார்.'),
    divider(),
    subhead('மூன்று வகை வாசிப்புகள்'),
    pp('நூல் வாசிப்பை மூன்றாக வகைப்படுத்துகிறது: பொழுதுபோக்கு வாசிப்பு, அறிவு பெறும் வாசிப்பு, ஆழ்ந்த சிந்தனைக்கான வாசிப்பு. ஒவ்வொன்றும் தேவை; ஒன்றை மட்டுமே செய்வது முழுமை தராது.'),
    pp('வீடியோ பார்க்கும்போது காட்சிகள் வருகின்றன; புத்தகம் படிக்கும்போது நாமே காட்சிகளை உருவாக்குகிறோம். கற்பனை ஆற்றல் வளர்வது இங்கேதான். ஆழமான விளக்கங்கள், நுட்பமான சிந்தனைகள் — வீடியோவில் மேலோட்டமாகவும் நூலில் ஆழமாகவும் கிடைக்கும்.'),
    slim_quote(
        ['முயலைப் பிடிக்க நினைத்தால் அதன் பின்னால் ஓடாதே;',
         'முயல் எங்கே ஓடும் எனக் கணித்து அங்கே காத்திரு!'],
        '— ஆப்பிரிக்கப் பழமொழி (நூலில் மேற்கோள்)'
    ),
    pp('வாசிப்பை திட்டமிட்டு நடத்துவதை இந்த உருவகம் அழகாக விளக்குகிறது — எந்த நூல் படிக்க வேண்டும், எப்போது, எப்படி என்ற தெளிவு முக்கியம் என்கிறார்.'),
])

mark_sec('நூல் மதிப்புரை')
pages.append(make_page(pn, 'நூல் மதிப்புரை',
    sec_header('வாசிப்பது எப்படி?', 'நூல் மதிப்புரை'),
    nuul_body_p1))
pn += 1

nuul_body_p2 = '\n'.join([
    subhead('நினைவில் நிற்கும் வரிகள்'),
    slim_quote(
        ['பெரியாரையும் அம்பேத்கரையும் படித்த ஒருவன் சாதியைத் தூக்கிப் பிடிக்க மாட்டான்.',
         'சலீம் அலி படித்தவன் சுற்றுச்சூழலைப் பாதுகாப்பான்.'],
        '— நூலில் மேற்கோள்'
    ),
    pp('வாசிப்பு மனிதனை மாற்றும் சக்தி கொண்டது என்பதை இந்த ஒரு வரி சொல்கிறது. நூலின் கடைசி அத்தியாயம் — <em>வாசகனின் கடமை</em> — மிக நுண்ணிய உண்மை ஒன்றைக் கூறுகிறது:'),
    slim_quote(
        ['நீங்கள் நல்ல வாசகன் எனில் இன்னொருவனை வாசிக்கச் சொல்லாதீர்கள்.',
         'வாசித்ததை சொல்லுங்கள். போதும்.'],
        '— செல்வேந்திரன்'
    ),
    pp('திணிப்பு அல்ல, பகிர்வு — இந்த வித்தியாசம் வாசிப்பு கலாச்சாரை உருவாக்கும்.'),
    divider(),
    subhead('நடைமுறை வழிகாட்டல்'),
    highlights('தொடங்குவோர்க்கு ஐந்து வழிகள்', [
        'தினமும் 15 நிமிடம் ஒதுக்குங்கள் — பழக்கம் வரும்',
        'ஆர்வமான விஷயத்தில் தொடங்குங்கள் — சிறுகதை, கட்டுரை, வாழ்க்கை வரலாறு',
        'கடினமான நூலை அட்டவணையிலிருந்து அணுகுங்கள்',
        'புரியாத சொற்களை குறித்து வையுங்கள் — அகராதி பழக்கமாகும்',
        'நூலகம் இலவசம் — வீண் விடாதீர்கள்',
    ]),
    pp('நூலின் இறுதியில் வாசிக்கத் தொடங்க விரும்புவோருக்கான பரிந்துரைப் பட்டியல் உள்ளது — தமிழ் இலக்கியம், மொழிபெயர்ப்பு நூல்கள், நாவல்கள் என பல்வேறு தளங்களில்.'),
    divider(),
    subhead('மதிப்பீடும் பரிந்துரையும்'),
    pp('98 பக்கங்களில் ஒரு வாசிப்பு தத்துவம் சொல்வது கஷ்டம். செல்வேந்திரன் அதை செய்திருக்கிறார் — திணிக்காமல், பிரசங்கிக்காமல், தன் வாழ்வின் வழியாக. எழுத்து நடை எளிமையானது; அணுகுமுறை அன்பானது; நடைமுறை வழிகாட்டல் நம்பகமானது.'),
    pp('வீட்டில் பதின்ம வயதினர் இருந்தால் கட்டாயம் கொடுங்கள். ஆசிரியர்கள் வகுப்பில் வாசித்துக் காட்டலாம். பெற்றோர்கள் குழந்தைகளுடன் விவாதிக்கலாம். ₹119 — ஒரு சிறிய முதலீடு, பெரிய மாற்றம்.'),
    divider(),
    '''        <div class="closing">
          <div class="sign-off">— நூல் மதிப்புரை குழு</div>
          <div class="org-name">வான் வளரொளி இதழ்</div>
          <div class="lotus-end">❀</div>
        </div>''',
])

pages.append(make_page(pn, 'நூல் மதிப்புரை',
    cont_banner('நூல் மதிப்புரை'),
    nuul_body_p2))
pn += 1

# ════════════════════════════════════════════════════════════════════════════
# PAGE (next): ஓர் ஒழுக்கம்
# ════════════════════════════════════════════════════════════════════════════
paras_05 = clean_paras(p05)

def build_ozhukkam_html(paras):
    html = []
    in_kural_block = False
    kural_lines = []

    for i, t in enumerate(paras):
        # Skip title lines
        if i < 2 and ('வான் வளரொளி' in t or 'ஓர் ஒழுக்கம்' in t):
            continue
        # Section headings
        if any(t.startswith(s) for s in ['அதிகாலை', 'வள்ளலார் காட்டும்', 'ஒழுக்கத்தின்',
                                           'நம் அக முன்னேற்றத்துக்கான', 'இறைவன் திருவார்த்தை',
                                           'காலமுள்ளபோதே', 'புறச்செயல்களும்', 'முதல் ஒழுக்கம்',
                                           'காலை ஐந்து', 'அற இலக்கியத்தில்', 'அமுதக் காற்று',
                                           'எழுவது மட்டும்', 'இன்றே தொடங்குவோம்']):
            html.append(subhead(t))
        # Kural couplet (two indented lines forming a verse)
        elif re.match(r'^(ஒழுக்கம்|வைகறை|நல்லறமும்|தந்தையும்|முந்தையோர்)', t):
            kural_lines.append(t)
        elif kural_lines and re.match(r'^(உயிரினும்|முறை\.|)', t):
            kural_lines.append(t)
            html.append(slim_quote(kural_lines, '— திருக்குறள் / ஆத்திச்சூடி'))
            kural_lines = []
        # கடவுள் / வள்ளலார் quote
        elif t.startswith('"') and t.endswith('"'):
            html.append(slim_quote([t], '— வள்ளலார்'))
        elif i == 0:
            html.append(pp(t, 'lead-para'))
        else:
            if kural_lines:
                kural_lines.append(t)
            else:
                html.append(pp(t))

    if kural_lines:
        html.append(slim_quote(kural_lines, ''))
    return html

oz_html = build_ozhukkam_html(paras_05)
chunk5 = max(1, len(oz_html) // 3)

mark_sec('ஓர் ஒழுக்கம்')
pages.append(make_page(pn, 'ஓர் ஒழுக்கம்',
    sec_header('அதிகாலை துயிலெழல்', 'ஓர் ஒழுக்கம்'),
    '\n'.join([byline('ஹரிஹரனார்')] + oz_html[:chunk5])))
pn += 1

pages.append(make_page(pn, 'ஓர் ஒழுக்கம்',
    cont_banner('ஓர் ஒழுக்கம்'),
    '\n'.join(oz_html[chunk5:2*chunk5])))
pn += 1

pages.append(make_page(pn, 'ஓர் ஒழுக்கம்',
    cont_banner('ஓர் ஒழுக்கம்'),
    '\n'.join(oz_html[2*chunk5:] + [
        divider(),
        '        <div class="lotus-end">❀</div>',
    ])))
pn += 1

# ════════════════════════════════════════════════════════════════════════════
# PAGE (next): சங்க இலக்கியம் — தாமரை
# ════════════════════════════════════════════════════════════════════════════
def md_to_html_thamarai(md_text):
    """Special parser for தாமரை article that handles verse box markup.
    Inserts lotus images after each section heading (fix 12)."""
    IC = 'Content/Issue-01'

    def lotus_img(src, caption):
        return (f'        <figure class="article-figure img-right">'
                f'<img src="{IC}/{src}" alt="{caption}">'
                f'<figcaption class="img-caption">{caption}</figcaption></figure>')

    # Map section keywords → lotus image to insert after heading
    _LOTUS_MAP = {
        'இயற்கையும் தாவரமும்':        ('lotus-sangam-painting-01.jpg', 'சங்ககால தாமரை — சித்திர பாணி'),
        'கவிதையின் உவமைகள்':          ('lotus-01.jpg',                  'தாமரை மலர்'),
        'ஆன்மீகச் சின்னம்':            ('lotus-02.jpg',                  'தாமரை — ஆன்மீக சின்னம்'),
        'அறிவியலும் பாரம்பரியமும்':    ('lotus-03.jpg',                  'தாமரை இலையில் நீர்த்துளி — தாமரை விளைவு'),
        'பண்பாட்டு மரபும் மருத்துவமும்':('lotus-04.jpg',                 'கோயில் குளத்தில் தாமரை'),
        'நடைமுறைப் பயன்':             ('lotus-05.jpg',                  'தாமரை — வாழ்வின் நெறி'),
    }

    lines = md_text.split('\n')
    html = []
    i = 0
    while i < len(lines):
        line = lines[i]

        # Verse box: ╔...╗ ... ╚...╝
        if line.strip().startswith('╔'):
            verse_lines = []
            source_line = ''
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('╚'):
                content = lines[i].strip()
                # Strip ║ delimiters
                content = re.sub(r'^║\s*', '', content)
                content = re.sub(r'\s*║\s*$', '', content)
                content = content.strip()
                if content:
                    if re.search(r'[(\(].*[)\)]|[0-9]+:[0-9]', content) or \
                       re.match(r'^\(', content) or \
                       re.search(r'(குறுந்தொகை|புறநானூறு|கலித்தொகை|பரிபாடல்|சிறுபாணாற்|பெரும்பாண்|திருமுருகாற்|நூல்)', content):
                        source_line = content
                    else:
                        verse_lines.append(content)
                i += 1
            # skip ╚ line
            if i < len(lines):
                i += 1
            if verse_lines:
                # Remove source line attribution per editorial policy — saves space
                html.append(slim_quote(verse_lines, ''))
            continue

        # H3 / H4 — and insert lotus image after matching section headings
        if line.startswith('### ') or line.startswith('#### '):
            text = re.sub(r'^#+\s+', '', line).strip()
            # Strip numbering prefix ("1. ", "2. " etc.) for matching
            text_bare = re.sub(r'^\d+\.\s+', '', text)
            html.append(subhead(text))
            for kw, (img_src, caption) in _LOTUS_MAP.items():
                if kw in text_bare:
                    html.append(lotus_img(img_src, caption))
                    break
            i += 1; continue

        # ── Skip / stop guards — MUST come before any formatting checks ────────
        # (The bold-pattern check below would otherwise render **படங்கள்...** as
        # a paragraph before the break condition is ever reached.)
        stripped = line.strip()
        if stripped.startswith('**மூலங்கள்') or stripped.startswith('மூலங்கள்'):
            i += 1; continue
        if stripped.startswith('**படங்கள்') or stripped.startswith('படங்கள்'):
            break  # Everything from here onwards is image editorial commentary
        if re.match(r'^[௧௨௩௪௫]\.\s', stripped):
            i += 1; continue
        if stripped.startswith('குறிப்பு: அனைத்து படங்களும்'):
            i += 1; continue

        # Bold intro line
        if re.match(r'^\*\*[^*]+\*\*$', stripped):
            text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', stripped)
            html.append(pp(text))
            i += 1; continue

        # Numbered practical tips (**௧.** etc.)
        if re.match(r'^\*\*[௧௨௩௪௫1-9]', stripped):
            text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', stripped)
            html.append(pp(text))
            i += 1; continue

        # Horizontal rule
        if re.match(r'^---+$', stripped):
            html.append(divider())
            i += 1; continue

        # Empty
        if not stripped:
            i += 1; continue

        # Normal paragraph
        text = line.strip()
        text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
        if text:
            html.append(pp(text))
        i += 1

    return html

thamarai_html = md_to_html_thamarai(md08)
# v4.4: use weight_split — images + verse boxes make element-count splits unreliable
th_pages = weight_split(thamarai_html)
print(f'  Thamarai: {len(thamarai_html)} items → {len(th_pages)} pages '
      f'(weights: {[sum(_item_weight(x) for x in p) for p in th_pages]})')

mark_sec('சங்க இலக்கியம்')
pages.append(make_page(pn, 'சங்க இலக்கியம்',
    sec_header('தாமரை மலரின் அறச்செய்தி', 'சங்க இலக்கியம்'),
    '\n'.join([byline('கௌரிசங்கர்')] + th_pages[0])))
pn += 1
for th_part in th_pages[1:]:
    if th_part:
        pages.append(make_page(pn, 'சங்க இலக்கியம்',
            cont_banner('சங்க இலக்கியம்'),
            '\n'.join(th_part)))
        pn += 1

# ════════════════════════════════════════════════════════════════════════════
# PAGE (next): இயற்கை தரும் இன்பம் — Munnar photo feature
# ════════════════════════════════════════════════════════════════════════════
# Use munnar-nature-images-02.webp (second image = alternate/better choice)
IMG_NATURE = 'Content/Issue-01/munnar-nature-images-02.webp'

nature_body = f'''        <figure class="article-figure img-banner">
          <img src="{IMG_NATURE}" alt="மலை அழகு — இயற்கை தரும் இன்பம்">
          <figcaption class="img-caption">மூடுபனியில் மலை — இயற்கையின் கவிதை</figcaption>
        </figure>
        {divider()}
        <p class="lead-para">இயற்கை கொடுக்கும் இன்பம் வேறு எதுவும் தர இயலாது. மலைகளின் மடியில் படர்ந்து கிடக்கும் மூடுபனி, பச்சை நிற காடுகள், ஓடும் அருவிகள் — இவை நம் உயிரை உற்சாகப்படுத்தும் மூலசக்தி.</p>
        {byline('கௌரிசங்கர்')}'''

mark_sec('இயற்கை தரும் இன்பம்')
pages.append(make_page(pn, 'இயற்கை தரும் இன்பம்',
    sec_header('இயற்கை தரும் இன்பம்', 'இயற்கை தரும் இன்பம்'),
    nature_body))
pn += 1

# ════════════════════════════════════════════════════════════════════════════
# PAGE (next): அறநிலையச் செய்திகள்
# Fully structured builder — handles bold headings, images, date/text fixes
# (Fixes 10, 16, 19, 21, 22, 23)
# ════════════════════════════════════════════════════════════════════════════
IC6 = 'Content/Issue-01'

def _van_img_right(src, caption):
    return (f'        <figure class="article-figure img-right">'
            f'<img src="{IC6}/{src}" alt="{caption}">'
            f'<figcaption class="img-caption">{caption}</figcaption></figure>')

def _van_img_half(src, caption):
    return (f'        <figure class="article-figure img-half">'
            f'<img src="{IC6}/{src}" alt="{caption}">'
            f'<figcaption class="img-caption">{caption}</figcaption></figure>')

act_p1 = [
    pp('பெண்ணாடம் வள்ளலார் அறநிலையம் கடலூர் மாவட்டம் திட்டக்குடி வட்டத்திலுள்ள '
       'பெண்ணாடம் என்னும் ஊரில் இயங்கிவரும் ஆதரவற்ற முதியோர் மற்றும் மாணவர் '
       'வாழ்விடமாகும்.', 'lead-para'),
    pp('இவ்வறநிலையம் இங்கு வசிக்கும் முதியவர் மற்றும் மாணவர் நலனை பேணுவதோடு '
       'தமிழ்வளர்ச்சி, மருத்துவம், சுற்றுப்புற மாணவர் நலன், சுற்றுசூழல் நலன் '
       'குறித்து பல்வேறு சமூக தொண்டுகள் ஆற்றும் நிறுவனமாகும்.'),
    pp('இங்கு மாத மாதம், ஆண்டுதோறும் எனப் பல்வேறு நிகழ்வுகள் அறநிலையத்திலும் '
       'Zoom தளத்திலும் நிகழ்ந்து வருகிறது. அத்தகைய நிகழ்வுகள் மாதந்தோறும் வரும் '
       'இதழிலும் கண்டு வாசகர்கள் கலந்து கொண்டு பயன்பெறலாம்.'),
    divider(),
    subhead('<strong>கோடைக்கால திறனூக்க பயிற்சி:</strong>'),
    _van_img_right('VAN-kids-01.jpg', 'கோடைக்கால திறனூக்க பயிற்சி — மாணவர்கள்'),
    pp('ஒரு ஆண்டுக்கு ஒரு முறை நடத்தப்படும் நிகழ்வாகும். இதில் அறநிலைய மாணவர்கள் '
       'மட்டுமல்லாமல் பெண்ணாடத்தைச் சுற்றியுள்ள தனியார் மற்றும் அரசு பள்ளி மாணவர்கள் '
       'இதில் பங்கேற்றுப் பயனடைகின்றனர்.'),
    pp('இவ்வாண்டு ஏப்ரல் 24-ம் தேதி தொடங்கி மே 2ம் தேதி வரை நடந்தது.'),
    _van_img_right('VAN-kids-02.jpg', 'கைவினை செயல்பாடு — கோடைப் பயிற்சி'),
    pp('இதில் யோகா, இசை (வாய்ப்பட்டு), கணினி பயிற்சி, எளிய முறை கணிதம், '
       'கைவினை பொருட்கள் செய்தல், உணவு பற்றிய விழிப்புணர்வு, புத்தகம் வாசிப்பு '
       'போன்ற பல்வேறு பயிற்சிகள் மாணவர்களுக்கு வழங்கப்படுகிறது.'),
]

act_p2 = [
    subhead('இலவச ஹோமியோபதி மருத்துவ முகாம்'),
    _van_img_right('VAN-MedCamp-001.jpg', 'மருத்துவ முகாம் — Dr. அருள்'),
    pp('இது மாதம் ஒரு முறை நடைபெறும் நிகழ்வாகும். ஒவ்வொரு மாத பூசத்தன்றும் '
       'இம்மருத்துவ முகாம் நடைபெற்று வருகிறது.'),
    _van_img_right('VAN-MedCamp-002.jpg', 'மருத்துவ முகாம் — நோயாளிகள்'),
    pp('இது Dr. அருள் MD (ஓமியோபதி) பட்டம் பெற்ற மருத்துவரால் நடத்தப்படுகிறது. '
       'பக்க விளைவுகள் இல்லாத இம்மருத்துவத்தில் பெண்ணாடம் சுற்றுவட்டாரத்தில் '
       'உள்ள பொதுமக்கள் பயனடைந்து வருகின்றனர். மருந்துகளும் கட்டணமின்றி '
       'வழங்கப்படுகிறது.'),
    divider(),
    subhead('மாதப்பூசம் — விளக்கு வழிபாடும் அன்னதானமும்'),
    _van_img_right('VAN-LampLit-01.jpg', 'மாதப்பூசம் — விளக்கேற்றல்'),
    pp('இது மாத பூச நாளன்று அறநிலையத்தில் நடைபெறும் நிகழ்வாகும். இதில் '
       'பெண்ணாடம் சுற்றுவட்டாரத்திலுள்ள மகளிர் கலந்து கொள்கின்றனர்.'),
    _van_img_right('VAN-Feeding-01.jpg', 'அன்னதானம்'),
    pp('இவ்வழிபாட்டுக்கு தேவையான பொருட்களை அறநிலையமே வழங்குகிறது. '
       'வழிபாட்டு நிறைவில் பொதுமக்களுக்கும் வழிபாட்டில் கலந்துகொள்வோருக்கும் '
       'அன்னதானம் வழங்கப்படுகிறது.'),
    divider(),
    subhead('<strong>மாணவர்களின் கோடைக்கால சுற்றுலா ஏப்ரல் 2026</strong>'),
    _van_img_right('VAN-kidsTour-01.jpg', 'சுற்றுலா — ஏற்காடு'),
    pp('இதுவும் ஆண்டுக்கு ஒருமுறை நடக்கும் நிகழ்வு. இது அறநிலைய மாணவர்களுக்கானது.'),
    _van_img_right('VAN-kidsTour-02.jpg', 'மாணவர்கள் — மலை இயற்கை மடியில்'),
    pp('இவ்வருடம் ஏப்ரல் மாதம் மாணவர்கள் மலைப் பிரதேசமான ஏற்காட்டுக்கு '
       'அழைத்துச் செல்லப்பட்டனர்.'),
]

mark_sec('அறநிலையச் செய்திகள்')
pages.append(make_page(pn, 'அறநிலையச் செய்திகள்',
    sec_header('வள்ளலார் அறநிலைய செய்திகள்', 'அறநிலையச் செய்திகள்'),
    '\n'.join([byline('குமாரவேல்')] + act_p1)))
pn += 1

pages.append(make_page(pn, 'அறநிலையச் செய்திகள்',
    cont_banner('அறநிலையச் செய்திகள்'),
    '\n'.join(act_p2)))
pn += 1

# ════════════════════════════════════════════════════════════════════════════
# PAGE (last): அடுத்த இதழில் + வாசகர் குரல்
# ════════════════════════════════════════════════════════════════════════════
closing_page_body = f'''
{subhead('வாசகர் குரல்')}
        <p>உங்கள் கருத்துகள், எண்ணங்கள், பாராட்டுகள், திருத்தங்கள் — அனைத்தும் இந்த இதழின் உயிரோட்டம்! அடுத்த இதழில் உங்கள் கருத்துகளை வெளியிடுவோம்.</p>
{divider()}
{highlights('இதழில் பங்களிக்க / தொடர்புகொள்ள', [
    'கட்டுரைகள், கவிதைகள், இயற்கை படங்கள் அனுப்பலாம்',
    '<strong>மின்னஞ்சல்:</strong> vallalararanilayampdm@gmail.com',
    '<strong>WhatsApp:</strong> +91 97880 33666',
    '<strong>வலையொளி:</strong> https://www.youtube.com/@pennadamvallalararanilayam',
    f'அடுத்த இதழ் வெளியீடு: <strong>வைகாசி 2026 — ஜூன் 2026</strong>',
])}
        <div class="closing">
          <p>வான் வளரொளி இதழின் முதல் பயணம் இங்கே நிறைவுபெறுகிறது. உங்கள் வாசிப்பும் ஆதரவும் இந்த அறப்பணியை தொடர வைக்கும். மீண்டும் வைகாசியில் சந்திப்போம்!</p>
          <div class="lotus-end">❀</div>
        </div>'''

mark_sec('அடுத்த இதழில்')
pages.append(make_page(pn, 'அடுத்த இதழில்',
    sec_header('வைகாசி 2026 — இதழ் 2', 'அடுத்த இதழில் • வாசகர் குரல்'),
    closing_page_body))
total_pages = pn
print(f'  Total content pages: {total_pages} (incl. 4 structural = {total_pages} pages)')
print(f'  Section start pages: {_sec_start}')

# ════════════════════════════════════════════════════════════════════════════
# 6. BUILD TOC — page numbers derived dynamically from _sec_start
# ════════════════════════════════════════════════════════════════════════════
def sp(name, fallback):
    """Look up section start page, falling back if mark_sec wasn't called."""
    return _sec_start.get(name, fallback)

toc_entries = [
    ('தலையங்கம்',               'தமிழர்களின் அறநெறியும் தமிழ் உணர்வும்',  sp('தலையங்கம்', 5),   '#8DC63F'),
    ('திருக்குறள் ஆய்வு',       'அறிவுடைமை — பத்துக் குறட்பாக்கள்',        sp('திருக்குறள் ஆய்வு', 7),  '#D4AF37'),
    ('சிறுகதை',                 'பால்வண்ணம் பிள்ளை — புதுமைப்பித்தன்',     sp('சிறுகதை', 11),    '#2d7a3e'),
    ('தமிழகக் கலைகள்',          'கோயிற் கட்டிடக் கலை — ஓர் அறிமுகம்',     sp('தமிழகக் கலைகள்', 14),   '#6BA82F'),
    ('நூல் மதிப்புரை',          'வாசிப்பது எப்படி? — செல்வேந்திரன்',      sp('நூல் மதிப்புரை', 19),   '#8DC63F'),
    ('ஓர் ஒழுக்கம்',            'அதிகாலை துயிலெழல் — வள்ளலாரின் நெறி',    sp('ஓர் ஒழுக்கம்', 21),     '#D4AF37'),
    ('சங்க இலக்கியம்',          'தாமரை மலரின் அறச்செய்தி',                 sp('சங்க இலக்கியம்', 24),   '#2d7a3e'),
    ('இயற்கை தரும் இன்பம்',    'மலை அழகு',                                 sp('இயற்கை தரும் இன்பம்', 27), '#6BA82F'),
    ('அறநிலையச் செய்திகள்',    'வள்ளலார் அறநிலைய நிகழ்வுகள்',            sp('அறநிலையச் செய்திகள்', 28), '#8DC63F'),
    ('அடுத்த இதழில்',           'வைகாசி 2026 • வாசகர் குரல்',              sp('அடுத்த இதழில்', total_pages), '#D4AF37'),
]

toc_rows = ''
for i, (sec, desc, pg, color) in enumerate(toc_entries):
    alt = ' row-alt' if i % 2 == 1 else ''
    toc_rows += f'''        <div class="toc-row{alt}">
          <div class="toc-accent" style="background:{color};"></div>
          <div class="toc-content">
            <div class="toc-section">{sec}</div>
            <div class="toc-desc">{desc}</div>
          </div>
          <div class="toc-dots"></div>
          <div class="toc-page" style="color:{color};">{pg}</div>
        </div>\n'''

TOC_PAGE = f'''
  <!-- PAGE 4 — TABLE OF CONTENTS ══════════════════════════════════════════ -->
  <div class="page">
    <div class="glossy"></div>
    <span class="corner-tl">❈</span>
    <span class="corner-br">❈</span>
    <div class="page-header">
      <span class="section-name">பொருளடக்கம்</span>
      <span class="mag-name">வான் வளரொளி இதழ்</span>
    </div>
    <div class="content-area">
      <div class="issue-banner">
        <div class="banner-text">
          <div class="banner-title">இதழ் 1 &nbsp;·&nbsp; சித்திரை 2026</div>
          <div class="banner-sub">பெண்ணாடம் வள்ளலார் அறநிலையம்</div>
        </div>
      </div>
      <div class="toc-list">
{toc_rows}      </div>
    </div>
    <div class="page-footer">
      <span class="issue-info">{ISSUE_INFO}</span>
      <span class="page-number">4</span>
      <img class="van-logo-footer" src="{LOGO}" alt="VAN">
    </div>
  </div>'''

# ════════════════════════════════════════════════════════════════════════════
# 7. ASSEMBLE AND WRITE
# ════════════════════════════════════════════════════════════════════════════
body = (
    COVER
    + IMPRINT
    + MASTHEAD
    + TOC_PAGE
    + '\n'.join(pages)
)

# Fix any remaining Tamil numeral page refs in imprint/masthead footers
body = re.sub(r'<span class="page-number">([௧௨௩௪௫௬௭௮௯௰]+)</span>',
              lambda m: f'<span class="page-number">{m.group(1)}</span>', body)

# Replace Tamil numerals in page-number spans specifically
tamil_to_arabic = str.maketrans('௧௨௩௪௫௬௭௮௯௰', '1234567890')
def fix_page_nums(m):
    return f'<span class="page-number">{m.group(1).translate(tamil_to_arabic)}</span>'
body = re.sub(r'<span class="page-number">([^<]+)</span>', fix_page_nums, body)

# Also fix issue-info Tamil numerals
body = body.replace('இதழ் எண்: ௧', 'இதழ் எண்: 1')
body = body.replace('சித்திரை ௨௦௨௬', 'சித்திரை 2026')

# Fix Tamil numerals in IMPRINT body text
body = body.replace('வான் வளரொளி இதழ் — ௧', 'வான் வளரொளி இதழ் — 1')
body = body.replace('திருவள்ளுவர் ஆண்டு ௨௦௫௭', 'திருவள்ளுவர் ஆண்டு 2057')

# Fix editorial "கல்வி மாத சிறப்பிதழில்" → "இதழில்"
body = body.replace('இம்மாத கல்வி மாத சிறப்பிதழில்', 'இம்மாத இதழில்')
body = body.replace('கல்வி மாத சிறப்பிதழில்', 'இதழில்')

# Fix 2 — Editorial lead-para: ensure salutation ends with comma
body = body.replace(
    '<p class="lead-para">அன்பார்ந்த வாசகர்களே</p>',
    '<p class="lead-para">அன்பார்ந்த வாசகர்களே,</p>')
body = body.replace(
    '<p class="lead-para">அன்பார்ந்த வாசகர்களே\n</p>',
    '<p class="lead-para">அன்பார்ந்த வாசகர்களே,</p>')

# Fix 3 — Page 5 editorial: final corrected form (with அறமே)
body = body.replace(
    '"வீரத்திற்கும் மறத்திற்கும் அறமே துணை"',
    '"வீரத்திற்கும் கருணைக்கும் அறமே துணை"')
body = body.replace(
    '"வீரத்திற்கும் அறமே துணை"',
    '"வீரத்திற்கும் கருணைக்கும் அறமே துணை"')
body = body.replace(
    '"வீரத்திற்கும் கருணைக்கும் துணை"',
    '"வீரத்திற்கும் கருணைக்கும் அறமே துணை"')

body = body.replace(
    'அறத்தையும் ஒழுக்கத்தையும் வாழ்ந்தவர்கள்,',
    'அறத்தையும் ஒழுக்கத்தையும் கண்களாக கொண்டு வாழ்ந்தவர்கள்,')
body = body.replace(
    'அறத்தையும் ஒழுக்கத்தையும் வாழ்ந்தவர்கள்',
    'அறத்தையும் ஒழுக்கத்தையும் கண்களாக கொண்டு வாழ்ந்தவர்கள்')

# Fix — Page 21: ஹரிஹரனார் → ஹரிஹரன்
body = body.replace('ஹரிஹரனார்', 'ஹரிஹரன்')

# Fix — Page 10: remove "(Take Home Message)" from subhead
body = body.replace(
    'ஆய்வின் முடிவுரை (Take Home Message)',
    'ஆய்வின் முடிவுரை:')

# Fix 7 — Page 14: சொலவடை → பழக்கம்
body = body.replace('சொலவடை', 'பழக்கம்')

# Fix 13 — Dr.Arul → Dr. அருள் (also any remaining raw form)
body = body.replace('Dr.Arul', 'Dr. அருள்')
body = body.replace('Dr. Arul', 'Dr. அருள்')

# Fix — கி பி abbreviation spacing (content from docx fragments)
body = re.sub(r'\bகி\s+பி\b', 'கி.பி.', body)
body = re.sub(r'\bகி\.\s+பி\.', 'கி.பி.', body)

# Fix — kalai article greeting comma
body = body.replace(
    'தமிழ் கூறும் நல்லுலக அன்பர்களுக்கு வணக்கம்</p>',
    'தமிழ் கூறும் நல்லுலக அன்பர்களுக்கு வணக்கம்,</p>')

# ════════════════════════════════════════════════════════════════════════════
# செந்தமிழ் POST-PROCESSING — fix loan words carried in from source files
# ════════════════════════════════════════════════════════════════════════════
# Story (1934 Pudumaippitthan) uses period vocabulary; magazine policy overrides
body = body.replace('ஸ்கூல் பைனல் வகுப்பில்', 'பள்ளி இறுதி வகுப்பில்')
body = body.replace('ஸ்கூல் பைனல்', 'பள்ளி இறுதி')
# VAN Activities educational table
body = re.sub(r'<td>ஸ்கூல்</td>', '<td>பள்ளி</td>', body)

final = HEAD + body + '\n' + TAIL

with open(OUT, 'w', encoding='utf-8') as f:
    f.write(final)

size = os.path.getsize(OUT)
lines_out = final.count('\n')
print(f'\n✅ Written: {OUT}')
print(f'   {lines_out:,} lines | {size/1024:.0f} KB')
