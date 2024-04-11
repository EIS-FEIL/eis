# -*- coding: utf-8 -*- 
# $Id: vaideavaldus.py 9 2015-06-30 06:34:46Z ahti $

import eis.model as model
from eis.model import const

from . import pages_loader
from .pdfdoc import *
from .pages.pdfutils import *
from .pages import vaideavaldus

class VaideavaldusDoc(PdfDoc):

    kasutaja = None
    
    def __init__(self, handler, vaie):
        self.handler = handler
        self.vaie = vaie

        self.page_template = vaideavaldus
        
    def gen_story(self):
        story = []
        self.page_template.generate(story, self.vaie)
        return story
