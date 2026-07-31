#!/usr/bin/env node
// VAN Vallaroli — Markdown to DOCX converter
// Converts all 13 .md files to nicely formatted .docx files in Docx/

const fs = require('fs');
const path = require('path');

const NODE_PATH = path.join(process.env.HOME, '.npm-global/lib/node_modules');
const docx = require(path.join(NODE_PATH, 'docx'));

const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, HeadingLevel, BorderStyle, WidthType,
  ShadingType, VerticalAlign, PageNumber, LevelFormat,
  ExternalHyperlink, ImageRun, PageBreak,
} = docx;

// Brand colours
const C_DEEP    = '2d7a3e';
const C_MID     = '8DC63F';
const C_DARK    = '6BA82F';
const C_GOLD    = 'D4AF37';
const C_BODY    = '2B2B2B';
const C_SUBTLE  = '666666';

const FONT = 'Noto Sans Tamil';

// ── Helpers ──────────────────────────────────────────────────────────────────

function run(text, opts = {}) {
  return new TextRun({
    text,
    font: FONT,
    size: opts.size || 24,           // half-points; 24 = 12pt
    bold: opts.bold || false,
    italics: opts.italics || false,
    color: opts.color || C_BODY,
  });
}

function emptyPara() {
  return new Paragraph({ children: [new TextRun({ text: '', font: FONT })] });
}

// Build inline runs from a mixed-markdown line (bold / italic / plain)
function inlineRuns(text, baseOpts = {}) {
  const runs = [];
  // Remove image tags entirely
  text = text.replace(/!\[.*?\]\(.*?\)/g, '');
  // Remove link brackets but keep text
  text = text.replace(/\[([^\]]+)\]\([^)]+\)/g, '$1');

  // Remove emoji that may cause issues (keep Unicode Tamil OK)
  // We'll keep emojis as-is; docx renders them as □ on some systems but that's acceptable

  // Split on **bold**, *italic*, or _italic_
  const re = /(\*\*[^*]+\*\*|\*[^*]+\*|_[^_]+_)/g;
  let last = 0;
  let m;
  while ((m = re.exec(text)) !== null) {
    if (m.index > last) {
      runs.push(run(text.slice(last, m.index), baseOpts));
    }
    const token = m[0];
    if (token.startsWith('**')) {
      runs.push(run(token.slice(2, -2), { ...baseOpts, bold: true }));
    } else {
      runs.push(run(token.slice(1, -1), { ...baseOpts, italics: true }));
    }
    last = m.index + token.length;
  }
  if (last < text.length) {
    runs.push(run(text.slice(last), baseOpts));
  }
  return runs.length ? runs : [run('', baseOpts)];
}

// Strip leading markdown syntax from a line and return plain text
function stripMarkdown(text) {
  return text
    .replace(/!\[.*?\]\(.*?\)/g, '')
    .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
    .replace(/\*\*([^*]+)\*\*/g, '$1')
    .replace(/\*([^*]+)\*/g, '$1')
    .replace(/_([^_]+)_/g, '$1')
    .trim();
}

// ── Paragraph builders ──────────────────────────────────────────────────────

function headingPara(text, level) {
  const configs = {
    1: { size: 40, color: C_DEEP, bold: true, spacing: { before: 320, after: 160 } },
    2: { size: 32, color: C_MID,  bold: true, spacing: { before: 280, after: 120 } },
    3: { size: 28, color: C_DARK, bold: true, spacing: { before: 240, after: 100 } },
    4: { size: 26, color: C_GOLD, bold: true, spacing: { before: 200, after: 80  } },
    5: { size: 24, color: C_SUBTLE, bold: true, spacing: { before: 160, after: 60 } },
  };
  const cfg = configs[level] || configs[3];
  return new Paragraph({
    children: inlineRuns(stripMarkdown(text), { size: cfg.size, color: cfg.color, bold: cfg.bold }),
    spacing: cfg.spacing,
    alignment: level <= 2 ? AlignmentType.CENTER : AlignmentType.LEFT,
  });
}

function bodyPara(text) {
  return new Paragraph({
    children: inlineRuns(text),
    spacing: { before: 60, after: 60 },
    alignment: AlignmentType.JUSTIFIED,
  });
}

function quotePara(text, isSource = false) {
  return new Paragraph({
    children: inlineRuns(text, {
      size: 22,
      italics: !isSource,
      color: isSource ? C_SUBTLE : C_BODY,
    }),
    indent: { left: 720, right: 360 },
    spacing: { before: 60, after: 60 },
    alignment: AlignmentType.CENTER,
    border: {
      left: { style: BorderStyle.SINGLE, size: 12, color: C_GOLD, space: 8 },
    },
  });
}

function hrPara() {
  return new Paragraph({
    children: [run('────────────────────────', { color: 'CCCCCC', size: 18 })],
    spacing: { before: 120, after: 120 },
    alignment: AlignmentType.CENTER,
  });
}

function bulletPara(text, level, numbering) {
  return new Paragraph({
    children: inlineRuns(text),
    spacing: { before: 40, after: 40 },
    numbering: { reference: numbering, level: level },
    alignment: AlignmentType.JUSTIFIED,
  });
}

// ── Table builder ─────────────────────────────────────────────────────────────

function buildTable(rows) {
  if (!rows.length) return null;
  const ncols = rows[0].length;
  if (!ncols) return null;

  // Content width (A4 with 1-inch margins): 11906 - 2880 = 9026 DXA
  const totalWidth = 9026;
  const colW = Math.floor(totalWidth / ncols);
  const colWidths = Array(ncols).fill(colW);

  const border = { style: BorderStyle.SINGLE, size: 4, color: 'AAAAAA' };
  const borders = { top: border, bottom: border, left: border, right: border, insideH: border, insideV: border };

  return new Table({
    width: { size: totalWidth, type: WidthType.DXA },
    columnWidths: colWidths,
    rows: rows.map((cells, ri) =>
      new TableRow({
        children: cells.map((cell, ci) =>
          new TableCell({
            borders,
            width: { size: colWidths[ci], type: WidthType.DXA },
            shading: ri === 0 ? { fill: 'E8F5E9', type: ShadingType.CLEAR } : undefined,
            margins: { top: 80, bottom: 80, left: 120, right: 120 },
            children: [new Paragraph({
              children: inlineRuns(cell.trim(), ri === 0 ? { bold: true, color: C_DEEP, size: 22 } : { size: 22 }),
              alignment: AlignmentType.LEFT,
            })],
          })
        ),
      })
    ),
  });
}

// ── Markdown parser ──────────────────────────────────────────────────────────

function parseMarkdown(mdText, filename) {
  const lines = mdText.split('\n');
  const elements = [];

  const bulletRef = 'bullets_' + filename.replace(/\W/g, '_');
  const numberRef = 'numbers_' + filename.replace(/\W/g, '_');
  const numbering = { config: [
    { reference: bulletRef, levels: [
      { level: 0, format: LevelFormat.BULLET, text: '\u2022', alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 720, hanging: 360 } } } },
    ]},
    { reference: numberRef, levels: [
      { level: 0, format: LevelFormat.DECIMAL, text: '%1.', alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 720, hanging: 360 } } } },
    ]},
  ]};

  let i = 0;
  let inQuoteBlock = false;
  let quoteLines = [];
  let tableLines = [];
  let inTable = false;
  let inCodeBlock = false;
  let codeLines = [];

  function flushQuote() {
    if (quoteLines.length) {
      // Detect source line (starts with —, -, or ( )
      quoteLines.forEach((ql, idx) => {
        const stripped = ql.replace(/^>\s*/, '');
        const isSource = /^[—\-\(]|^\(|திருக்குறள்|புறநானூறு|மதுரைக்காஞ்சி|மணிமேகலை|தொல்காப்பியம்|குறுந்தொகை|கலித்தொகை|சிறுபாணாற்றுப்படை|பெரும்பாணாற்றுப்படை|வள்ளலார்|வள்ளுவர்/.test(stripped);
        elements.push(quotePara(stripped, isSource));
      });
      quoteLines = [];
    }
    inQuoteBlock = false;
  }

  function flushTable() {
    if (tableLines.length < 2) {
      tableLines = [];
      inTable = false;
      return;
    }
    // Filter out separator rows (---|---)
    const dataRows = tableLines.filter(row => !/^\|[\s\-:|]+\|/.test(row.trim()));
    if (!dataRows.length) { tableLines = []; inTable = false; return; }

    const parsed = dataRows.map(row => {
      // Split by | and trim, remove empty first/last
      const cells = row.split('|').map(c => c.trim()).filter((c, idx, arr) => idx > 0 && idx < arr.length - 1);
      return cells;
    });
    const tbl = buildTable(parsed);
    if (tbl) {
      elements.push(tbl);
      elements.push(emptyPara());
    }
    tableLines = [];
    inTable = false;
  }

  function flushCode() {
    if (codeLines.length) {
      // Display as indented paragraphs with gray background effect
      codeLines.forEach(cl => {
        elements.push(new Paragraph({
          children: [new TextRun({ text: cl, font: 'Courier New', size: 18, color: '444444' })],
          indent: { left: 720 },
          spacing: { before: 20, after: 20 },
          shading: { fill: 'F5F5F5', type: ShadingType.CLEAR },
        }));
      });
    }
    codeLines = [];
    inCodeBlock = false;
  }

  while (i < lines.length) {
    const raw = lines[i];
    const line = raw.trimEnd();

    // Code block fence
    if (line.startsWith('```')) {
      if (inCodeBlock) {
        flushCode();
      } else {
        if (inQuoteBlock) flushQuote();
        if (inTable) flushTable();
        inCodeBlock = true;
      }
      i++;
      continue;
    }
    if (inCodeBlock) {
      codeLines.push(line);
      i++;
      continue;
    }

    // Box drawing (╔══╗ style) — treat as quote
    if (/^[╔╚╠]/.test(line)) {
      i++;
      continue;
    }
    if (/^[║╝╣]/.test(line)) {
      const inner = line.replace(/^[║]\s*/, '').replace(/\s*[║]$/, '').trim();
      if (inner && !/^[╚╝═─]/.test(inner)) {
        quoteLines.push('> ' + inner);
        inQuoteBlock = true;
      }
      i++;
      continue;
    }

    // Table row
    if (line.startsWith('|')) {
      if (inQuoteBlock) flushQuote();
      inTable = true;
      tableLines.push(line);
      i++;
      continue;
    } else if (inTable) {
      flushTable();
    }

    // Blockquote
    if (line.startsWith('>')) {
      if (!inQuoteBlock) inQuoteBlock = true;
      quoteLines.push(line);
      i++;
      continue;
    } else if (inQuoteBlock) {
      flushQuote();
    }

    // Horizontal rule
    if (/^---+$/.test(line.trim()) || /^===+$/.test(line.trim())) {
      elements.push(hrPara());
      i++;
      continue;
    }

    // Headings
    const hMatch = line.match(/^(#{1,6})\s+(.*)/);
    if (hMatch) {
      elements.push(headingPara(hMatch[2], hMatch[1].length));
      i++;
      continue;
    }

    // Unordered list
    const ulMatch = line.match(/^(\s*)[-*+]\s+(.*)/);
    if (ulMatch) {
      elements.push(bulletPara(ulMatch[2], 0, bulletRef));
      i++;
      continue;
    }

    // Ordered list
    const olMatch = line.match(/^(\s*)\d+[.)]\s+(.*)/);
    if (olMatch) {
      elements.push(bulletPara(olMatch[2], 0, numberRef));
      i++;
      continue;
    }

    // Checkmark list (✓, ✅, ☑)
    const ckMatch = line.match(/^[✓✅☑✨🪷🔬🌍⚙️🔭💻🔮📚🎯💎📅👥💝🙋📢❌🎵]\s*(.*)/);
    if (ckMatch) {
      elements.push(bulletPara(line, 0, bulletRef));
      i++;
      continue;
    }

    // Empty line
    if (!line.trim()) {
      elements.push(emptyPara());
      i++;
      continue;
    }

    // Normal paragraph
    elements.push(bodyPara(line));
    i++;
  }

  // Flush any pending blocks
  if (inQuoteBlock) flushQuote();
  if (inTable) flushTable();
  if (inCodeBlock) flushCode();

  return { elements, numbering };
}

// ── Header / Footer ──────────────────────────────────────────────────────────

function makeHeader(sectionTitle) {
  return new Header({
    children: [new Paragraph({
      children: [
        run('வான் வளரொளி இதழ்', { size: 18, color: C_DEEP, bold: true }),
        run('   •   ', { size: 18, color: C_GOLD }),
        run(sectionTitle, { size: 18, color: C_SUBTLE }),
      ],
      border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: C_MID, space: 4 } },
    })],
  });
}

function makeFooter() {
  return new Footer({
    children: [new Paragraph({
      children: [
        run('பெண்ணாடம் வள்ளலார் அறநிலையம் (VAN)   •   ', { size: 16, color: C_SUBTLE }),
        new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 16, color: C_SUBTLE }),
      ],
      border: { top: { style: BorderStyle.SINGLE, size: 6, color: C_MID, space: 4 } },
      alignment: AlignmentType.CENTER,
    })],
  });
}

// ── Main converter ────────────────────────────────────────────────────────────

const contentDir = '/Users/gowri/spaceclub/e-magazine/Content';
const docxDir    = path.join(contentDir, 'Docx');

// Ensure Docx directory exists
if (!fs.existsSync(docxDir)) fs.mkdirSync(docxDir, { recursive: true });

const mdFiles = fs.readdirSync(contentDir).filter(f => f.endsWith('.md'));
console.log(`Found ${mdFiles.length} markdown files to convert.\n`);

mdFiles.forEach(mdFile => {
  const mdPath = path.join(contentDir, mdFile);
  const baseName = path.basename(mdFile, '.md');
  const docxPath = path.join(docxDir, baseName + '.docx');

  try {
    const mdText = fs.readFileSync(mdPath, 'utf8');
    const { elements, numbering } = parseMarkdown(mdText, baseName);

    // Extract title from first H1 or filename
    const titleMatch = mdText.match(/^#\s+(.+)$/m);
    const title = titleMatch ? titleMatch[1].trim() : baseName;
    const shortTitle = baseName.replace(/^\d+[-\s]*/, '').trim();

    const doc = new Document({
      numbering,
      styles: {
        default: {
          document: {
            run: { font: FONT, size: 24, color: C_BODY },
          },
        },
        paragraphStyles: [
          {
            id: 'Heading1', name: 'Heading 1', basedOn: 'Normal', next: 'Normal', quickFormat: true,
            run: { size: 40, bold: true, font: FONT, color: C_DEEP },
            paragraph: { spacing: { before: 320, after: 160 }, outlineLevel: 0 },
          },
          {
            id: 'Heading2', name: 'Heading 2', basedOn: 'Normal', next: 'Normal', quickFormat: true,
            run: { size: 32, bold: true, font: FONT, color: C_MID },
            paragraph: { spacing: { before: 280, after: 120 }, outlineLevel: 1 },
          },
          {
            id: 'Heading3', name: 'Heading 3', basedOn: 'Normal', next: 'Normal', quickFormat: true,
            run: { size: 28, bold: true, font: FONT, color: C_DARK },
            paragraph: { spacing: { before: 240, after: 100 }, outlineLevel: 2 },
          },
        ],
      },
      sections: [{
        properties: {
          page: {
            size: { width: 11906, height: 16838 },  // A4
            margin: { top: 1440, right: 1260, bottom: 1440, left: 1260 },
          },
        },
        headers: { default: makeHeader(shortTitle) },
        footers: { default: makeFooter() },
        children: elements,
      }],
    });

    Packer.toBuffer(doc).then(buf => {
      fs.writeFileSync(docxPath, buf);
      console.log(`✓  ${mdFile}`);
      console.log(`   → ${path.basename(docxPath)}`);
    }).catch(err => {
      console.error(`✗  ${mdFile}: ${err.message}`);
    });

  } catch (err) {
    console.error(`✗  ${mdFile}: ${err.message}`);
  }
});
