"""Batch export existing essays with the approved one-page bilingual layout.

Run with a Python environment containing reportlab and pypdf. FontTools with
Brotli support is only needed when converting the bundled fonts for the first time.
Default: exclude eight-c02, which has already been delivered.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
import re
import subprocess
import sys
from xml.sax.saxutils import escape

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
W, H = A4
MARGIN, GAP = 30, 22
COL = (W - 2 * MARGIN - GAP) / 2


def load_content(excluded):
    # Reuse exactly the article site's framework and vocabulary highlighting.
    javascript = """
import {readFile} from 'node:fs/promises';
import {learningText,validateTranslations} from './scripts/essay-library.mjs';
const essays=JSON.parse(await readFile('data/essays.json','utf8'));
const translations=JSON.parse(await readFile('data/essay-translations.json','utf8'));
const vocabulary=JSON.parse(await readFile('data/essay-vocabulary.json','utf8'));
validateTranslations(essays,translations);
process.stdout.write(JSON.stringify(essays.map(essay=>({essay,blocks:
  translations[essay.id].flatMap((p,pi)=>p.map((s,si)=>({...s,pi,si,
    html:learningText(s.en,vocabulary[essay.id])})))
}))));
"""
    result = subprocess.run(['node', '--input-type=module', '-e', javascript],
                            cwd=ROOT, capture_output=True, text=True, check=True)
    data = json.loads(result.stdout)
    unknown = excluded - {entry['essay']['id'] for entry in data}
    if unknown:
        raise ValueError(f'Unknown essay IDs: {unknown}')
    return [entry for entry in data if entry['essay']['id'] not in excluded]


def register_fonts():
    ttf = ROOT / 'tmp/pdfs/merriweather-bold.ttf'
    if not ttf.exists():
        sys.path.insert(0, str(ROOT / 'tmp/pdfs/font-conversion'))
        from fontTools.ttLib import TTFont as WebFont
        font = WebFont(ROOT / 'mubu-editor/src/fonts/merriweather-bold.woff2')
        font.flavor = None
        ttf.parent.mkdir(parents=True, exist_ok=True)
        font.save(ttf)
    for name in ['Reading', 'ReadingBold']:
        pdfmetrics.registerFont(TTFont(name, str(ttf)))
    pdfmetrics.registerFontFamily('Reading', normal='Reading', bold='ReadingBold')
    pdfmetrics.registerFont(TTFont('Chinese', '/System/Library/Fonts/Supplemental/Arial Unicode.ttf'))


def styled(html):
    html = re.sub(r'<mark class="essay-learning" title="[^"]*">',
                  '<font color="#e1254e"><b>', html)
    return (html.replace('</mark>', '</b></font>')
            .replace('<span class="essay-repeated">', '<font color="#7833da"><b>')
            .replace('</span>', '</b></font>'))


def chinese_lines(text, size, width):
    lines = []
    closing, opening = '，。！？；：、）》】”’％…', '（《【“‘'
    while text:
        n = 0
        while n < len(text) and pdfmetrics.stringWidth(text[:n+1], 'Chinese', size) <= width:
            n += 1
        if n < len(text):
            while n > 1 and (text[n] in closing or text[n-1] in opening):
                n -= 1
        if not n:
            raise ValueError('Column is narrower than one character')
        lines.append(text[:n])
        text = text[n:]
    return lines


def layout(blocks, en_size, zh_size, pair_gap, paragraph_gap):
    items = []
    for block in blocks:
        indent = en_size * 1.38 if block['si'] else 0
        width = COL - indent
        en = Paragraph(styled(block['html']), ParagraphStyle(
            'en', fontName='Reading', fontSize=en_size, leading=en_size*1.31,
            textColor=HexColor('#2c3037')))
        _, en_height = en.wrap(width, 2000)
        lines = chinese_lines(block['zh'], zh_size, width)
        before = paragraph_gap if block['si'] == 0 and block['pi'] else 0
        height = before + en_height + 3 + len(lines)*zh_size*1.38 + pair_gap
        items.append(dict(block=block, en=en, en_height=en_height, lines=lines,
                          before=before, height=height, indent=indent))
    candidates = []
    for split in range(1, len(items)):
        left = sum(item['height'] for item in items[:split])
        right = sum(item['height'] for item in items[split:])
        candidates.append((max(left, right), abs(left-right), split))
    return items, min(candidates)


def draw_page(pdf, entry, page_number):
    essay, blocks = entry['essay'], entry['blocks']
    titles = chinese_lines(essay['title'], 15, W - 2*MARGIN - 90)
    pdf.setFillColor(HexColor('#20232a'))
    pdf.setFont('Chinese', 15)
    for index, title in enumerate(titles):
        pdf.drawString(MARGIN, H-34-index*18, title)
    pdf.setFont('Chinese', 8)
    pdf.setFillColor(HexColor('#686b72'))
    pdf.drawRightString(W-MARGIN, H-33, '逐句中英对照')
    question_text = escape(essay['question']).replace('？', '<font name="Chinese">？</font>')
    question = Paragraph(question_text, ParagraphStyle(
        'question', fontName='Reading', fontSize=9, leading=12,
        textColor=HexColor('#333740')))
    _, question_height = question.wrap(W-2*MARGIN, 2000)
    question_top = H-47-(len(titles)-1)*18
    question.drawOn(pdf, MARGIN, question_top-question_height)
    top = question_top-question_height-20
    pdf.setStrokeColor(HexColor('#d9dce1'))
    pdf.setLineWidth(.4)
    pdf.line(MARGIN, top+10, W-MARGIN, top+10)
    chosen = None
    # Preserve the largest possible text before considering denser spacing.
    for en_size, zh_size in [(10, 8.8), (9.7, 8.5), (9.4, 8.3), (9.1, 8.1)]:
        for pair_gap, paragraph_gap in [(7, 8), (6, 8), (5, 7), (4, 6)]:
            items, best = layout(blocks, en_size, zh_size, pair_gap, paragraph_gap)
            if best[0] <= top-44:
                chosen = (items, best[2], en_size, zh_size, pair_gap, paragraph_gap)
                break
        if chosen:
            break
    if not chosen:
        raise ValueError(f"Cannot fit {essay['id']} on one page without reducing legibility")
    items, split, en_size, zh_size, pair_gap, paragraph_gap = chosen
    bottoms = []
    for column_index, column in enumerate([items[:split], items[split:]]):
        x, y = MARGIN+column_index*(COL+GAP), top
        for item in column:
            y -= item['before']
            if item['block']['si']:
                pdf.setFillColor(HexColor('#3d3d43'))
                pdf.circle(x+en_size*.35, y-en_size*.66, en_size*.15, fill=1, stroke=0)
            item['en'].drawOn(pdf, x+item['indent'], y-item['en_height'])
            y -= item['en_height']+3
            pdf.setFont('Chinese', zh_size)
            pdf.setFillColor(HexColor('#666a71'))
            for line in item['lines']:
                pdf.drawString(x+item['indent'], y-zh_size, line)
                y -= zh_size*1.38
            y -= pair_gap
        assert y >= 44, (essay['id'], y)
        bottoms.append(round(y, 2))
    pdf.setStrokeColor(HexColor('#d3d6db'))
    pdf.setLineWidth(.45)
    pdf.line(W/2, top+10, W/2, 42)
    pdf.showPage()
    return dict(page=page_number, id=essay['id'], title=essay['title'],
                en_size=en_size, zh_size=zh_size, pair_gap=pair_gap,
                paragraph_gap=paragraph_gap, bottoms=bottoms,
                sentence_pairs=len(blocks), title_lines=len(titles))


def verify(path, entries):
    reader = PdfReader(path)
    assert len(reader.pages) == len(entries)
    normalize = lambda text: re.sub(r'\s+', '', text)
    for page, entry in zip(reader.pages, entries):
        assert abs(float(page.mediabox.width)-W) < .01
        assert abs(float(page.mediabox.height)-H) < .01
        extracted = normalize(page.extract_text())
        expected = [entry['essay']['title'], entry['essay']['question']]
        expected += [block[key] for block in entry['blocks'] for key in ['en', 'zh']]
        for text in expected:
            assert normalize(text) in extracted, (entry['essay']['id'], text)
    return len(reader.pages)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--exclude', nargs='*', default=['eight-c02'])
    parser.add_argument('--output', type=Path,
                        default=ROOT/'output/pdf/雅思范文69篇-结构化翻译-每篇一页.pdf')
    args = parser.parse_args()
    entries = load_content(set(args.exclude))
    assert entries, 'No essays selected'
    register_fonts()
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    partial = output.with_name('.'+output.name+'.partial')
    pdf = canvas.Canvas(str(partial), pagesize=A4)
    pdf.setTitle(f'雅思范文{len(entries)}篇 - 结构化翻译 - 每篇一页')
    pdf.setAuthor('IELTS Writing')
    audit = [draw_page(pdf, entry, i+1) for i, entry in enumerate(entries)]
    pdf.save()
    page_count = verify(partial, entries)
    partial.replace(output)
    audit_path = ROOT/'tmp/pdfs/structured-batch-audit.json'
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2))
    print(json.dumps(dict(output=str(output), pages=page_count,
                          sentence_pairs=sum(row['sentence_pairs'] for row in audit),
                          font_sizes=dict(Counter(row['en_size'] for row in audit)),
                          min_bottom=min(min(row['bottoms']) for row in audit),
                          verified='One A4 page per essay; full question and every English/Chinese sentence verified',
                          audit=str(audit_path)), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
