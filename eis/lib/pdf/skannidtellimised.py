# -*- coding: utf-8 -*- 

from datetime import datetime

import eis.model as model
from eis.model import const

from . import pages_loader
from .pdfdoc import *
from .pages.pdfutils import *
from .pages import skannidtellimised

class SkannidTellimisedDoc(PdfDoc):
    pagenumbers = True
    
    def __init__(self, header, items):
        self.header = header
        self.items = items

    def _doctemplate(self, output):
        "PDFi dokumendi loomine"
        return SimpleDocTemplate(output,
                                 pagesize=landscape(A4),
                                 topMargin=10*mm, bottomMargin=10*mm, 
                                 rightMargin=10*mm, leftMargin=10*mm)
    def gen_story(self):
        story = []
        skannidtellimised.generate(story, self.header, self.items)
        return story

