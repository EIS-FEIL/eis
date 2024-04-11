# -*- coding: utf-8 -*- 
# $Id: klassitulemus.py 9 2015-06-30 06:34:46Z ahti $

import eis.model as model
from eis.model import const

from . import pages_loader
from .pdfdoc import *
from .pages.pdfutils import *
from .pages import klassitulemus

class KlassitulemusDoc(PdfDoc):

    def __init__(self, header, footer, items, c, is_landscape=False):
        self.header = header
        self.footer = footer
        self.items = items
        self.c = c
        self.page_template = klassitulemus
        self.is_landscape = is_landscape

    def _doctemplate(self, output):
        "PDFi dokumendi loomine"
        # vähendame ääri
        pagesize = self.is_landscape and landscape(A4) or A4
        leftMargin = self.is_landscape and 10*mm or 22*mm
        return SimpleDocTemplate(output,
                                 pagesize=pagesize,
                                 leftMargin=leftMargin,
                                 rightMargin=10*mm)
        
    def gen_story(self, img=None):
        story = []
        self.page_template.generate(story, self.header, self.footer, self.items, self.c, img, self.is_landscape)
        return story


