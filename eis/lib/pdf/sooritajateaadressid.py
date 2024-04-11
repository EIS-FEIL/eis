# -*- coding: utf-8 -*- 
# $Id: sooritajateaadressid.py 9 2015-06-30 06:34:46Z ahti $

import eis.model as model
from eis.model import const

from . import pages_loader
from .pdfdoc import *
from .pages.pdfutils import *
from .pages import sooritajateaadressid

class SooritajateaadressidDoc(PdfDoc):
    #pagenumbers = True
    
    def __init__(self, toimumisaeg, items):
        self.toimumisaeg = toimumisaeg
        self.items = items
        self.page_template = sooritajateaadressid

    def _doctemplate(self, output):
        "PDFi dokumendi loomine"
        return SimpleDocTemplate(output,
                                 pagesize=landscape(A4),
                                 leftMargin=10*mm,
                                 rightMargin=10*mm)

    def gen_story(self):
        story = []       
        self.page_template.generate(story, self.toimumisaeg, self.items)
        return story


