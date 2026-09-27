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
A heading (`## ` through `###### `) becomes a subhead with the green
left-bar style. The design has only one subhead style, so every level
renders identically — use `###`+ only to signal nesting in your source,
not to get a different look.

```markdown
## முன்னுரை
### வேள் பாரி
```

Articles typically have 2–6 subheads.

### 2b. Inline bold
`**text**` becomes `<strong>text</strong>`. Works inside paragraphs, bullet
list items, and box items. No other inline emphasis (italics, links, etc.)
is supported — anything else is printed literally.

### 3. Bullet list
Lines starting with `- ` become an unordered list.

```markdown
- First item
- Second item
- Third item
```

### 3b. Numbered list
Lines starting with `1. `, `2. ` … become an ordered list. Use for step-by-step
instructions or a references/ஆதாரம் list — do NOT use plain `1. text` lines
back to back with no list markup expectation; the parser only recognizes this
exact `N. ` prefix pattern.

```markdown
1. First step
2. Second step
3. Third step
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
| `float-left` | 60×45mm left-floated thumbnail | Second image in a row — alternate sides so text doesn't get squeezed into a narrow column between two same-side floats |
| `banner` | Full-width hero, height capped at 75mm (cover crop) | Wide section openers and landscapes |
| `banner-full` | Full width, the photo's own height, no crop | A full-width photo that is not a wide panorama |
| `half` | 80mm centered, no border | Diagrams, single objects, artifact/figurine photos |
| `portrait` | 45mm centered, no border | A single author/subject portrait at an article's top, before the lead paragraph |

**Never put two consecutive `float` (or two consecutive `float-left`) images back to back with only a short paragraph between them** — the paragraph gets squeezed into a narrow ragged column between the stacked floats. Alternate `float` / `float-left`, or separate them with enough body text / a `half` image to clear the float before the next one starts.

The `src` must match a filename in the issue's `images/` folder.

### 7. Closing block
Author sign-off at the end of an article.

```markdown
:::closing
நாம் மேலும் வளர்வோம்.
— குமாரவேல்
நிர்வாக இயக்குநர்
வான் அறநிலையம்
:::
```

Lines are split automatically: any line ending in `./!/?/।` (a full sentence)
stays plain closing prose. The **first line that isn't a full sentence**
starts the signature card, and the lines after it fill sign-off → name →
title → org-name in order. A leading `—` on the sign-off line is optional
(not required to trigger the split, but still fine to include) — write the
signature block as short label-like lines, not full sentences, and the
parser finds the boundary on its own. A decorative ❀ is added automatically
at the end.

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

Run before handing an issue to the pipeline:

```bash
python validate_mmd.py issues/Issue-NN/articles/*.md --issue issues/Issue-NN
```

It catches:
- Missing/malformed frontmatter or required fields
- Section name not matching a `section_name` in `issue_meta.json`
- Image files referenced but missing from `images/`
- English loan words (செந்தமிழ் check)
- Em-dash typos (`--`/`----` instead of `—`)
- Unclosed `:::` directives
- A rough page-count estimate per article

The build-time parser (`mmd_parser.py`) also emits soft warnings for
unknown directives or missing `src=` on an image, but `validate_mmd.py`
is the pre-flight check to run first — it's the one authors/editors should
use before content ever reaches the pipeline.
