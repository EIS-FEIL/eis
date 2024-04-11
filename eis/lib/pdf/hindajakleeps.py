# -*- coding: utf-8 -*- 
# $Id: hindajakleeps.py 9 2015-06-30 06:34:46Z ahti $

from datetime import datetime

import eis.model as model
from eis.model import const

from . import pages_loader
from .pdfdoc import *
from .pages.pdfutils import *
from .pages import hindajakleeps

class HindajakleepsDoc(PdfDoc):
    pagenumbers = True
    
    def __init__(self, q, toimumisaeg, yhekaupa):
        self.q = q
        self.toimumisaeg = toimumisaeg
        self.yhekaupa = yhekaupa

    def _doctemplate(self, output):
        return SimpleDocTemplate(output, 
                                 pagesize=(100*mm,50*mm),
                                 leftMargin=0*mm,
                                 rightMargin=0*mm,
                                 topMargin=4*mm,
                                 bottomMargin=1*mm)
        
    def gen_story(self):
        story = []
        if self.yhekaupa:
            for hkogum, hindaja1, hindaja2 in self.q.all():
                hindajakleeps.generate(story, self.toimumisaeg, hkogum, hindaja1, None)
            for hkogum, hindaja1, hindaja2 in self.q.all():
                if hindaja2:
                    hindajakleeps.generate(story, self.toimumisaeg, hkogum, None, hindaja2)
        else:
            for hkogum, hindaja1, hindaja2 in self.q.all():
                hindajakleeps.generate(story, self.toimumisaeg, hkogum, hindaja1, hindaja2)            
        return story


