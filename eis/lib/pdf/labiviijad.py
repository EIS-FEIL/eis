# -*- coding: utf-8 -*- 
# $Id: labiviijad.py 9 2015-06-30 06:34:46Z ahti $

import eis.model as model
from eis.model import const

from . import pages_loader
from .pdfdoc import *
from .pages.pdfutils import *
from .pages import labiviijad

class LabiviijadDoc(PdfDoc):

    def __init__(self, header, items, title):
        self.header = header
        self.items = items
        self.title = title
        self.page_template = labiviijad

    def _doctemplate(self, output):
        "PDFi dokumendi loomine"
        # vähendame ääri
        return SimpleDocTemplate(output,
                                 pagesize=landscape(A4),
                                 leftMargin=10*mm,
                                 rightMargin=10*mm)
        
    def gen_story(self):
        story = []
        
        self.page_template.generate(story, self.header, self.items, self.title)
        return story


