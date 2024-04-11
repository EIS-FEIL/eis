# -*- coding: utf-8 -*- 
# $Id: soorituskohad.py 9 2015-06-30 06:34:46Z ahti $

from datetime import datetime

import eis.model as model
from eis.model import const

from . import pages_loader
from .pdfdoc import *
from .pages.pdfutils import *
from .pages import soorituskohad

class SoorituskohadDoc(PdfDoc):
    pagenumbers = True
    
    def __init__(self, items, keeled, sooritajad, vaatlejad, ruumid):
        self.items = items
        self.keeled = keeled
        self.sooritajad = sooritajad
        self.vaatlejad = vaatlejad
        self.ruumid = ruumid
        self.page_template = soorituskohad

    def gen_story(self):
        story = []
        self.page_template.generate(story, self.items, self.keeled, self.sooritajad, self.vaatlejad, self.ruumid)
        return story

