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

root=Path.cwd(); data=json.loads((root/'tmp/pdfs/structured-content.json').read_text())
essay=data['essay'];blocks=data['blocks']
for name,file in [('Reading','Arial.ttf'),('ReadingBold','Arial Bold.ttf'),('Chinese','Arial Unicode.ttf')]:
    pdfmetrics.registerFont(TTFont(name,'/System/Library/Fonts/Supplemental/'+file))
pdfmetrics.registerFontFamily('Reading',normal='Reading',bold='ReadingBold')
w,h=A4; margin=27; gap=25; col=(w-2*margin-gap)/2
out=root/'output/pdf/未成年人与成年人是否同罚-结构化翻译-清晰分区版.pdf'
c=canvas.Canvas(str(out),pagesize=A4)
c.setTitle(essay['title']+' - 结构化翻译（清晰分区版）')
c.setFillColor(HexColor('#222831'));c.setFont('Chinese',15)
c.drawString(margin,h-31,essay['title'])
c.setFont('Chinese',7.5);c.setFillColor(HexColor('#747b85'))
c.drawRightString(w-margin,h-30,'中英对照 / 单页阅读')
p=Paragraph(escape(essay['question']),ParagraphStyle('question',fontName='Reading',fontSize=8.8,leading=11.6,textColor=HexColor('#343b45')))
_,ph=p.wrap(w-2*margin-14,1000)
qtop=h-43
c.setFillColor(HexColor('#f3f5f7'));c.roundRect(margin,qtop-ph-7,w-2*margin,ph+12,3,fill=1,stroke=0)
p.drawOn(c,margin+7,qtop-ph)
top=qtop-ph-18

def styled(html):
    html=re.sub(r'<mark class="essay-learning" title="[^"]*">','<font color="#d6234d"><b>',html)
    html=html.replace('</mark>','</b></font>')
    return html.replace('<span class="essay-repeated">','<font color="#7833c5"><b>').replace('</span>','</b></font>')

def zh_lines(text,size,width):
    lines=[];rest=text;closing='，。！？；：、）》】”’％…';opening='（《【“‘'
    while rest:
        n=0
        while n<len(rest) and pdfmetrics.stringWidth(rest[:n+1],'Chinese',size)<=width:n+=1
        if n<len(rest):
            while n>1 and (rest[n] in closing or rest[n-1] in opening):n-=1
        lines.append(rest[:n]);rest=rest[n:]
    return lines

def layout(ens,zhs):
    items=[]
    for b in blocks:
        indent=8 if b['si'] else 0
        en=Paragraph(styled(b['html']),ParagraphStyle('en',fontName='Reading',fontSize=ens,leading=ens*1.23,textColor=HexColor('#252b34')))
        _,eh=en.wrap(col-indent,2000)
        lines=zh_lines(b['zh'],zhs,col-indent-7)
        height=eh+3+len(lines)*zhs*1.30+8
        items.append(dict(b=b,en=en,eh=eh,lines=lines,height=height,indent=indent))
    def height(column):
        return sum(i['height'] for i in column)+sum(19 if n==0 else 24 for n,i in enumerate(column) if n==0 or i['b']['si']==0)
    choices=[]
    for split in range(1,len(items)):
        l=height(items[:split]);r=height(items[split:]);choices.append((max(l,r),abs(l-r),split,l,r))
    return items,min(choices)

for ens,zhs in [(10,8.8),(9.8,8.6),(9.6,8.5),(9.4,8.4)]:
    items,best=layout(ens,zhs)
    if best[0]<=top-26:break
assert best[0]<=top-26
_,_,split,_,_=best
bottoms=[]
for ci,column in enumerate([items[:split],items[split:]]):
    x=margin+ci*(col+gap);y=top
    for ii,item in enumerate(column):
        b=item['b']
        if ii==0 or b['si']==0:
            if ii:y-=5
            c.setFillColor(HexColor('#edf0f4'));c.roundRect(x,y-14,col,14,2,fill=1,stroke=0)
            c.setFillColor(HexColor('#414b59'));c.rect(x,y-14,2,14,fill=1,stroke=0)
            c.setFont('ReadingBold',8);c.drawString(x+7,y-10,f'{b["pi"]+1:02d}')
            c.setFont('Chinese',7.8)
            continuation='（续）' if b['si'] else ''
            c.drawString(x+25,y-10,f'第 {b["pi"]+1} 段{continuation}')
            y-=19
        if b['si']:
            c.setFillColor(HexColor('#687382'));c.circle(x+1.8,y-ens*.48,1,fill=1,stroke=0)
        item['en'].drawOn(c,x+item['indent'],y-item['eh'])
        y-=item['eh']+3
        zhHeight=len(item['lines'])*zhs*1.30
        c.setStrokeColor(HexColor('#cfd5dd'));c.setLineWidth(.7)
        c.line(x+item['indent']+1,y-.8,x+item['indent']+1,y-zhHeight+1)
        c.setFont('Chinese',zhs);c.setFillColor(HexColor('#636d7b'))
        for line in item['lines']:
            c.drawString(x+item['indent']+7,y-zhs,line);y-=zhs*1.30
        y-=8
    bottoms.append(y)
    assert y>=26
    print('column',ci+1,'bottom',round(y,2),'pairs',len(column))
c.setStrokeColor(HexColor('#c2c9d2'));c.setLineWidth(.65)
c.line(w/2,top,w/2,min(bottoms)+5)
c.save()
r=PdfReader(str(out));assert len(r.pages)==1
norm=lambda s:re.sub(r'\s+','',s)
text=norm(r.pages[0].extract_text())
for s in [essay['question']]+[b[k] for b in blocks for k in ['en','zh']]:assert norm(s) in text,s
assert '第3段（续）' in text
print('Verified: 1 A4 page, complete question and 14 sentence pairs; paragraph continuation marked')
print('Font sizes:',ens,zhs)
print(out)
