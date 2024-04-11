# -*- coding: utf-8 -*- 
# $Id: testikohamarkused.py 9 2015-06-30 06:34:46Z ahti $

import eis.model as model
from eis.model import const

from . import pages_loader
from .pdfdoc import *
from .pages.pdfutils import *
from .pages import testikohamarkused

class TestikohamarkusedDoc(PdfDoc):
    #pagenumbers = True
    
    def __init__(self, toimumisaeg, items):
        self.toimumisaeg = toimumisaeg
        self.items = items
        self.page_template = testikohamarkused

    def _doctemplate(self, output):
        "PDFi dokumendi loomine"
        return SimpleDocTemplate(output, 
                                 topMargin=10*mm, bottomMargin=10*mm, 
                                 rightMargin=10*mm, leftMargin=20*mm)

    def gen_story(self):
        story = []       
        self.page_template.generate(story, self.toimumisaeg, self.items)
        return story


