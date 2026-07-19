# Magazine Markdown (MMD) Specification

The formal content format for authors. One `.md` file per article.

## File structure

```
[YAML frontmatter]
[blank line]
[body content using MMD]
```

## Frontmatter (required)

```yaml
---
section: திருக்குறள் ஆய்வு          # must match issue_meta.json section_name
title:   நட்பு — ஓர் ஆய்வு         # large topic title on page 1
subtitle: திருவள்ளுவர் காட்டும்...    # optional one-line teaser
author:  திருமுருகன்                  # appears as byline on page 1
---
```

| Field | Required | Purpose |
|---|---|---|
| `section` | yes | Must exactly match a `section_name` from `issue_meta.json` |
| `title` | yes | Becomes the large topic title on the section's first page |
| `subtitle` | no | Short tagline shown beneath the title |
| `author` | yes | Author byline on page 1 |

## Body elements

### 1. Paragraph
Plain text separated by blank lines. The first paragraph gets `.lead-para` styling automatically.

```markdown
First paragraph. Multiple sentences are fine.

Second paragraph after a blank line.
```

### 2. Subhead
A second-level heading (`## `) becomes a subhead with the green left-bar style.

```markdown
## முன்னுரை
```

Articles typically have 2–6 subheads.

### 3. Bullet list
Lines starting with `- ` become an unordered list.

```markdown
- First item
- Second item
- Third item
```

### 4. Slim quote (verse / pull-quote)
A `:::quote` directive with optional `source` attribute.

```markdown
:::quote source="திருக்குறள் 421"
அறிவற்றம் காக்கும் கருவி செறுவார்க்கும்
உள்ளழிக்க லாகா அரண்.
:::
```

Each non-blank line inside becomes a verse line (joined by `<br>` in HTML).

### 5. Highlights box
A `:::box` directive with `title` attribute and bulleted items inside.

```markdown
:::box title="இந்த இதழில்..."
- திருக்குறள் ஆய்வு
- சங்க இலக்கியம்
- நூல் மதிப்புரை
:::
```

### 6. Image
A `:::image` directive with `src` and `caption` attributes. Optional `type` selects layout.

```markdown
:::image src="lotus-01.jpg" caption="கோயில் குளத்தில் தாமரை" type="float"
:::
```

| `type=` | Visual | When to use |
|---|---|---|
| `float` (default) | 60×45mm right-floated thumbnail | Most images |
| `banner` | Full-width hero | Section openers, dramatic shots |
| `half` | 100mm centered | Diagrams, single objects |

The `src` must match a filename in the issue's `images/` folder.

### 7. Closing block
Author sign-off at the end of an article.

```markdown
:::closing
நாம் மேலும் வளர்வோம்.
— குமாரவேல்
:::
```

Lines starting with `—` are styled as sign-off; subsequent lines become the name. A decorative ❀ is added automatically.

## Rules

- **Tamil only**: no English loan words (use செந்தமிழ் — `கணினி` not `கம்ப்யூட்டர்`)
- **Em-dash for citations**: `—` (U+2014), never `----` or `--`
- **No manual page breaks**: pagination is automatic
- **No HTML tags**: only the elements above; arbitrary HTML is not preserved
- **No images embedded in text**: use `:::image` directives only

## Complete example

```markdown
---
section: திருக்குறள் ஆய்வு
title: நட்பு — ஓர் ஆய்வு
subtitle: திருவள்ளுவர் காட்டும் நட்பின் இலக்கணம்
author: திருமுருகன்
---

தமிழ் கூறும் நல்லுலக அன்பர்களுக்கு வணக்கம்.

வள்ளுவர் நட்பு அதிகாரத்தில் சொல்வது...

:::image src="lotus.jpg" caption="நட்பு — தாமரை போல"
:::

## நட்பின் இயல்பு

வள்ளுவர் நட்பை ஆன்ம உறவாக சித்தரிக்கிறார்.

:::quote source="திருக்குறள் 781"
செயற்கரிய யாவுள நட்பின் அதுபோல
வினைக்கரிய யாவுள காப்பு.
:::

இக்குறள் நட்பின் இரண்டு பரிமாணங்களைச் சொல்கிறது.

:::closing
— திருமுருகன்
:::
```

## Validation

Future enhancement: `validate_mmd.py` will catch errors before submission:
- Missing required frontmatter
- Section name not in `issue_meta.json`
- Image files that don't exist
- English loan words
- Unclosed `:::` directives

For now, the parser warns about basic issues at build time.
