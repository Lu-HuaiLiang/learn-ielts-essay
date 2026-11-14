import json,re
from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pypdf import PdfReader

root=Path.cwd()
essay=next(e for e in json.loads((root/'data/essays.json').read_text()) if e['id']=='eight-c02')
translations=json.loads((root/'data/essay-translations.json').read_text())[essay['id']]
paras=[p.replace('**','') for p in essay['paragraphs']]
assert all(' '.join(s['en'] for s in tr)==p for p,tr in zip(paras,translations))
zh=[''.join(s['zh'] for s in tr) for tr in translations]
pdfmetrics.registerFont(TTFont('Chinese','/System/Library/Fonts/Supplemental/Arial Unicode.ttf'))
output=root/'output/pdf/未成年人与成年人是否同罚-范文与翻译.pdf'
c=canvas.Canvas(str(output),pagesize=A4)
c.setTitle(essay['title']+' - 范文与翻译')
c.setAuthor('IELTS Writing')
w,h=A4
margin=50
width=w-2*margin

def chinese_lines(text, size):
    lines=[]
    rest=text
    closing='，。！？；：、）》】”’％…'
    opening='（《【“‘'
    while rest:
        n=0
        while n<len(rest) and pdfmetrics.stringWidth(rest[:n+1], 'Chinese', size)<=width:
            n+=1
        if n<len(rest):
            while n>1 and (rest[n] in closing or rest[n-1] in opening):
                n-=1
        lines.append(rest[:n])
        rest=rest[n:]
    return lines

def draw_text(text, font, size, leading, y):
    if font=='Chinese':
        lines=chinese_lines(text,size)
        c.setFont(font,size)
        for i,line in enumerate(lines):
            c.drawString(margin,y-size-i*leading,line)
        return len(lines)*leading
    style=ParagraphStyle('text',fontName=font,fontSize=size,leading=leading,splitLongWords=False)
    p=Paragraph(escape(text),style)
    _,ph=p.wrap(width,1000)
    p.drawOn(c,margin,y-ph)
    return ph

def draw_page(title,label,question,body,font,size,leading):
    y=h-48
    c.setFont('Chinese',16)
    c.drawString(margin,y,title)
    y-=30
    c.setFont('Chinese',10)
    c.drawString(margin,y,'题目' if font=='Times-Roman' else '题目翻译')
    y-=10
    ph=draw_text(question,font,size,leading,y)
    y-=ph+23
    c.setFont('Chinese',10)
    c.drawString(margin,y,label)
    y-=12
    for txt in body:
        ph=draw_text(txt,font,size,leading,y)
        y-=ph+11
    assert y>45, f'Page content overflows: {y}'
    c.setFont('Times-Roman',9)
    c.drawCentredString(w/2,26,str(c.getPageNumber()))
    print('page',c.getPageNumber(),'bottom',round(y,1),'paragraphs',len(body))
    c.showPage()

# Preserve the source question verbatim, including its original word "published".
draw_page(essay['title'],'范文',essay['question'],paras,'Times-Roman',11.2,15.8)
question_zh='犯下抢劫、暴力袭击等严重罪行的年轻人，应受到与成年人相同的惩罚。你在多大程度上同意或不同意这一观点？'
draw_page(essay['title'],'翻译',question_zh,zh,'Chinese',11,19.4)
c.save()
r=PdfReader(str(output))
assert len(r.pages)==2
normalize=lambda s:re.sub(r'\s+','',s)
for i,(question,body) in enumerate([(essay['question'],paras),(question_zh,zh)]):
    extracted=normalize(r.pages[i].extract_text())
    for text in [question]+body:
        assert normalize(text) in extracted, f'Missing text on page {i+1}'
print(output)
print('Verified: 2 pages, complete question and 5 complete paragraphs per page')
