# -*- coding: utf-8 -*- 
# $Id: testpdf.py 890 2016-09-29 13:46:02Z ahti $

from datetime import datetime

import eis.model as model
from eis.model import const

from . import pages_loader
from .pdfdoc import *
from .pages.pdfutils import *
from .pages import testpdf

class TestpdfDoc(PdfDoc):
    pagenumbers = False
    
    def __init__(self):
        pass

    # def _register_times_font(self):
    #     # kirjutame vaikimisi fondifaili yle selleks, 
    #     # et saada läti tähti, mida vaikimisi font ei paku
    #     FN_TIMESBD_FONT = '/tmp/timesbd1c.ttf'
    #     FN_TIMESBD_FONT = '/tmp/TimesNewRomanBold.ttf'
    #     #FN_TIMESBD_FONT = '/tmp/timesbd2.ttf'

    #     pdfmetrics.registerFont(TTFont('Times-Roman', FN_TIMES_FONT))
    #     pdfmetrics.registerFont(TTFont('Times-Bold', FN_TIMESBD_FONT))
    #     pdfmetrics.registerFont(TTFont('Times-Italic', FN_TIMESI_FONT))
    #     addMapping('Times-Roman', 0, 0, 'Times-Roman') #normal
    #     addMapping('Times-Roman', 0, 1, 'Times-Italic') #italic
    #     addMapping('Times-Roman', 1, 0, 'Times-Bold') #bold
    #     #addMapping('Times-Roman', 1, 1, 'Times-BoldItalic') #italic and bold 

    def _doctemplate(self, output):
        "PDFi dokumendi loomine"
        return SimpleDocTemplate(output,
                                 pagesize=landscape(A4),
                                 topMargin=10*mm, bottomMargin=10*mm, 
                                 rightMargin=10*mm, leftMargin=10*mm)
    def gen_story(self):
        story = []
        testpdf.generate(story)
        return story

if __name__ == '__main__':
    doc = TestpdfDoc()
    data = doc.generate()
    f = open('tmp.pdf', 'wb')
    f.write(data)
    f.close()
    print(len(data))
    
