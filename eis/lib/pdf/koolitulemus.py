# -*- coding: utf-8 -*- 
import eis.model as model
from eis.model import const

from . import pages_loader
from .pdfdoc import *
from .pages.pdfutils import *
from .pages import koolitulemus

class KoolitulemusDoc(PdfDoc):

    def __init__(self, header, items, c):
        self.header = header
        self.items = items
        self.c = c
        self.page_template = koolitulemus

    def _doctemplate(self, output):
        "PDFi dokumendi loomine"
        # vähendame ääri
        return SimpleDocTemplate(output,
                                 pagesize=A4,
                                 leftMargin=22*mm,
                                 rightMargin=10*mm)
        
    def gen_story(self):
        story = []
        self.page_template.generate(story, self.header, self.items, self.c)
        return story


