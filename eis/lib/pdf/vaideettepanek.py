# -*- coding: utf-8 -*- 
# $Id: vaideettepanek.py 9 2015-06-30 06:34:46Z ahti $

import eis.model as model
from eis.model import const

from . import pages_loader
from .pdfdoc import *
from .pages.pdfutils import *
from .pages import vaideettepanek, vaideettepanek_hindajatega

class VaideettepanekDoc(PdfDoc):

    kasutaja = None
    txt = None
    
    def __init__(self, handler, vaie, diff, hindajatega=False):
        self.handler = handler
        self.vaie = vaie
        self.diff = diff
        if hindajatega:
            self.page_template = vaideettepanek_hindajatega
        else:
            self.page_template = vaideettepanek
        
    def gen_story(self):
        story = []
        self.txt = self.page_template.generate(story, self.vaie, self.diff)
        return story
