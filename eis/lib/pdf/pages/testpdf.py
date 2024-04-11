# -*- coding: utf-8 -*- 
# $Id: testpdf.py 890 2016-09-29 13:46:02Z ahti $
"PDF testimine"

from eis.lib.pdf.pages.pdfutils import *
from eis.lib.pdf.pages.stylesheet import *
import eis.lib.helpers as h

def generate(story):
    # from eis.lib.pdf.pdfdoc import *
    # fn_path = '/srv/eis/etc/'
    # pdfmetrics.registerFont(TTFont('Times-Roman', fn_path + 'times.ttf'))
    # pdfmetrics.registerFont(TTFont('Times-Bold', fn_path + 'timesbd.ttf'))
    # pdfmetrics.registerFont(TTFont('Times-Italic', fn_path + 'timesi.ttf'))
    # addMapping('Times-Roman', 0, 0, 'Times-Roman') #normal
    # addMapping('Times-Roman', 0, 1, 'Times-Italic') #italic
    # addMapping('Times-Roman', 1, 0, 'Times-Bold') #bold
    story.append(Paragraph('õÕ test', N))
    story.append(Paragraph('õÕ test', NB))
    if True:
        buf = "Маршрут: из Мемфиса в Новый Орлеан"
        story.append(Paragraph(buf, N))
        story.append(Paragraph('<b>%s</b>' % buf, N))
        story.append(Paragraph(buf, NB))
        
