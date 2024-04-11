# -*- coding: utf-8 -*- 
# $Id: hindamiserinevused.py 9 2015-06-30 06:34:46Z ahti $

from datetime import datetime

import eis.model as model
from eis.model import const

from . import pages_loader
from .pdfdoc import *
from .pages.pdfutils import *
from .pages import hindamiserinevused

class HindamiserinevusedDoc(PdfDoc):
    pagenumbers = True
    
    def __init__(self, ta, hkogum, q, query_ylesandehinded, punktides):
        self.ta = ta
        self.hindamiskogum = hkogum
        self.q = q
        self.query_ylesandehinded = query_ylesandehinded
        self.punktides = punktides

    def gen_story(self):
        story = []
        hindamiserinevused.generate(story, self.ta, self.hindamiskogum, self.q, self.query_ylesandehinded, self.punktides)
        return story

