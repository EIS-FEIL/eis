# -*- coding: utf-8 -*- 
# $Id: mootmisvead.py 9 2015-06-30 06:34:46Z ahti $

import eis.model as model
from eis.model import const

from . import pages_loader
from .pdfdoc import *
from .pages.pdfutils import *
from .pages import mootmisvead

class MootmisveadDoc(PdfDoc):
    pagenumbers = True
    
    def __init__(self, header, items, testimiskord, staatus_jrk):
        self.header = header
        self.items = items
        self.testimiskord = testimiskord
        self.staatus_jrk = staatus_jrk

    def _doctemplate(self, output):
        "PDFi dokumendi loomine"
        return SimpleDocTemplate(output,
                                 pagesize=landscape(A4),
                                 topMargin=10*mm, bottomMargin=10*mm, 
                                 rightMargin=10*mm, leftMargin=10*mm)
    def gen_story(self):
        story = []
        mootmisvead.generate(story, self.header, self.items, self.testimiskord, self.staatus_jrk)
        return story

