import json,re
from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from pypdf import PdfReader

root=Path.cwd()
data=json.loads((root/'tmp/pdfs/structured-content.json').read_text())
essay=data['essay']; blocks=data['blocks']
for name,file in [('Reading','Arial.ttf'),('ReadingBold','Arial Bold.ttf'),('Chinese','Arial Unicode.ttf')]:
    pdfmetrics.registerFont(TTFont(name,'/System/Library/Fonts/Supplemental/'+file))
pdfmetrics.registerFontFamily('Reading',normal='Reading',bold='ReadingBold')
w,h=A4
margin=30; gap=22; col=(w-2*margin-gap)/2
out=root/'output/pdf/未成年人与成年人是否同罚-结构化翻译-单页.pdf'
c=canvas.Canvas(str(out),pagesize=A4)
c.setTitle(essay['title']+' - 结构化翻译（单页）')
c.setFont('Chinese',15)
c.setFillColor(HexColor('#20232a'))
c.drawString(margin,h-34,essay['title'])
c.setFont('Chinese',8)
c.setFillColor(HexColor('#686b72'))
c.drawRightString(w-margin,h-33,'逐句中英对照')
questionStyle=ParagraphStyle('question',fontName='Reading',fontSize=9,leading=12,textColor=HexColor('#333740'))
p=Paragraph(escape(essay['question']),questionStyle)
_,ph=p.wrap(w-2*margin,1000)
qtop=h-47
p.drawOn(c,margin,qtop-ph)
top=qtop-ph-20
c.setStrokeColor(HexColor('#d9dce1')); c.setLineWidth(.4)
c.line(margin,top+10,w-margin,top+10)

# Convert the same highlights used on the article page to PDF inline spans.
def styled(html):
    html=re.sub(r'<mark class="essay-learning" title="[^"]*">','<font color="#e1254e"><b>',html)
    html=html.replace('</mark>','</b></font>')
    html=html.replace('<span class="essay-repeated">','<font color="#7833da"><b>').replace('</span>','</b></font>')
    return html

def zh_lines(text,size,width):
    lines=[]; rest=text
    closing='，。！？；：、）》】”’％…'; opening='（《【“‘'
    while rest:
        n=0
        while n<len(rest) and pdfmetrics.stringWidth(rest[:n+1],'Chinese',size)<=width: n+=1
        if n<len(rest):
            while n>1 and (rest[n] in closing or rest[n-1] in opening): n-=1
        lines.append(rest[:n]);rest=rest[n:]
    return lines

# A sentence and its translation always stay together within one column.
def layout(enSize,zhSize):
    items=[]
    for b in blocks:
        indent=enSize*1.38 if b['si'] else 0
        textwidth=col-indent
        en=Paragraph(styled(b['html']),ParagraphStyle('en',fontName='Reading',fontSize=enSize,leading=enSize*1.31,textColor=HexColor('#2c3037')))
        _,eh=en.wrap(textwidth,2000)
        lines=zh_lines(b['zh'],zhSize,textwidth)
        zhHeight=len(lines)*zhSize*1.38
        before=8 if b['si']==0 and b['pi'] else 0
        height=before+eh+3+zhHeight+7
        items.append(dict(b=b,en=en,eh=eh,lines=lines,before=before,height=height,indent=indent))
    candidates=[]
    for split in range(1,len(items)):
        left=sum(i['height'] for i in items[:split]);right=sum(i['height'] for i in items[split:])
        candidates.append((max(left,right),abs(left-right),split,left,right))
    best=min(candidates)
    return items,best

for ens,zhs in [(10,8.8),(9.7,8.5),(9.4,8.3),(9.1,8.1)]:
    items,best=layout(ens,zhs)
    if best[0]<top-30: break
assert best[0]<top-30, 'Content cannot fit legibly'
_,_,split,leftHeight,rightHeight=best
for colIndex,column in enumerate([items[:split],items[split:]]):
    x=margin+colIndex*(col+gap);y=top
    for item in column:
        y-=item['before']
        if item['b']['si']:
            c.setFillColor(HexColor('#3d3d43'))
            c.circle(x+ens*.35,y-ens*.66,ens*.15,fill=1,stroke=0)
        item['en'].drawOn(c,x+item['indent'],y-item['eh'])
        y-=item['eh']+3
        c.setFont('Chinese',zhs);c.setFillColor(HexColor('#666a71'))
        for line in item['lines']:
            c.drawString(x+item['indent'],y-zhs,line)
            y-=zhs*1.38
        y-=7
    assert y>30
    print('column',colIndex+1,'bottom',round(y,1),'sentence pairs',len(column))
c.setStrokeColor(HexColor('#d3d6db'))
c.setLineWidth(.45)
c.line(w/2, top+10, w/2, 42)
c.save()
r=PdfReader(str(out));assert len(r.pages)==1
normalize=lambda s:re.sub(r'\s+','',s)
extracted=normalize(r.pages[0].extract_text())
for text in [essay['question']]+[b[k] for b in blocks for k in ['en','zh']]:
    assert normalize(text) in extracted, text
print('Verified: one A4 page, all',len(blocks),'English/Chinese pairs and full question')
print('English size',ens,'Chinese size',zhs)
print(out)
