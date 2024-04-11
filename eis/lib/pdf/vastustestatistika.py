# -*- coding: utf-8 -*- 

from datetime import datetime

import eis.model as model
from eis.model import const

from . import pages_loader
from .pdfdoc import *
from .pages.pdfutils import *
from .pages import vastustestatistika

class VastustestatistikaDoc(PdfDoc):
    pagenumbers = True
    
    def __init__(self, args):
        self.args = args

    def _doctemplate(self, output):
        "PDFi dokumendi loomine"
        doc = SimpleDocTemplate(output,
                                pagesize=A4,
                                topMargin=15*mm, bottomMargin=10*mm, 
                                rightMargin=10*mm, leftMargin=10*mm)
        test = self.args[0]
        doc.title = 'Testi %s vastuste statistika' % (test.id)
        self.page_template = vastustestatistika
        return doc
    
    def gen_story(self):
        story = []
        self.page_template.generate(story, self.args)
        return story

