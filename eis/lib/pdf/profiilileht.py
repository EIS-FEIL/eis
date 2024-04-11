# -*- coding: utf-8 -*- 

import eis.model as model
from eis.model import const

from . import pages_loader
from .pdfdoc import *
from .pages.pdfutils import *
from .pages import profiilileht

class ProfiililehtDoc(PdfDoc):

    kasutaja = None
    
    def __init__(self, handler, sooritus, header, items):
        self.handler = handler
        self.sooritus = sooritus
        self.header = header
        self.items = items
        self.page_template = profiilileht
        
    def _doctemplate(self, output):
        "PDFi dokumendi loomine"
        return SimpleDocTemplate(output,
                                 pagesize=A4,
                                 topMargin=20*mm, bottomMargin=20*mm, 
                                 rightMargin=17*mm, leftMargin=17*mm)

        
    def gen_story(self):
        story = []
        self.page_template.generate(story, self.handler, self.sooritus, self.header, self.items)
        return story
