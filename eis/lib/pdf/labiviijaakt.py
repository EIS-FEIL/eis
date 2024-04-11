from itertools import groupby

import eis.model as model
from eis.model import const

from . import pages_loader
from .pdfdoc import *
from .pages.pdfutils import *
from .pages import (
    labiviijaakt_sisestaja,
    labiviijaakt_vaatleja,
    labiviijaakt_hindaja,
    labiviijaakt_tasemeeksam,
    labiviijaakt_seadus,
    labiviijaakt_riigieksam,
    labiviijaakt_tesisestaja,
    labiviijaakt_sesisestaja,
    labiviijaakt_tehindaja,
    labiviijaakt_sehindaja
    )

class LabiviijaaktDoc(PdfDoc):

    def __init__(self, items, tname, grupeeritud=False, grupid_id=[], testiliik=None, taiendavinfo=None):
        self.items = items
        self.grupeeritud = grupeeritud
        self.grupid_id = grupid_id
        self.testiliik = testiliik
        self.taiendavinfo = taiendavinfo
        
        if tname == 'sisestaja':
            self.page_template = labiviijaakt_sisestaja
        elif tname == 'tesisestaja':
            self.page_template = labiviijaakt_tesisestaja
        elif tname == 'sesisestaja':
            self.page_template = labiviijaakt_sesisestaja
        elif tname == 'vaatleja':
            self.page_template = labiviijaakt_vaatleja
        elif tname == 'hindaja':
            self.page_template = labiviijaakt_hindaja
        elif tname == 'tehindaja':
            self.page_template = labiviijaakt_tehindaja
        elif tname == 'sehindaja':
            self.page_template = labiviijaakt_sehindaja
        elif tname == 'tasemeeksam':
            self.page_template = labiviijaakt_tasemeeksam
        elif tname == 'seadus':
            self.page_template = labiviijaakt_seadus
        elif tname == 'riigieksam':
            # kõik muud mallid on ka selle liigiga
            self.page_template = labiviijaakt_riigieksam
        else:
            raise Exception('ootamatu tname väärtus %s' % tname)
        
    def gen_story(self):
        story = []
        if self.grupeeritud:
            # yhe isiku andmed
            self.page_template.generate(story, self.items, self.grupid_id, self.testiliik, self.taiendavinfo)
        else:
            # mitme isiku andmed, grupeerime isikute kaupa
            for (kasutaja_id), items in groupby(self.items, lambda r: r[0]):
                self.page_template.generate(story, items, self.grupid_id, self.testiliik, self.taiendavinfo)
            
        return story
