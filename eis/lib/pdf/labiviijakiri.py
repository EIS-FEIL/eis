from itertools import groupby

import eis.model as model
from eis.model import const

from . import pages_loader
from .pdfdoc import *
from .pages.pdfutils import *
from .pages import (
    labiviijaakt_sisestaja,
    labiviijakiri_vaatleja,
    labiviijaakt_hindaja,
    labiviijakiri_tasemeeksam,
    labiviijakiri_seadus,
    labiviijakiri_riigieksam,
    labiviijakiri_tesisestaja,
    labiviijakiri_sesisestaja,
    labiviijakiri_tehindaja,
    labiviijakiri_sehindaja
    )

class LabiviijakiriDoc(PdfDoc):

    def __init__(self, items, tname, grupeeritud=False, grupid_id=[], testiliik=None, taiendavinfo=None):
        self.items = items
        self.grupeeritud = grupeeritud
        self.grupid_id = grupid_id
        self.testiliik = testiliik
        self.taiendavinfo = taiendavinfo
        
        if tname == 'sisestaja':
            self.page_template = labiviijaakt_sisestaja
        elif tname == 'tesisestaja':
            self.page_template = labiviijakiri_tesisestaja
        elif tname == 'sesisestaja':
            self.page_template = labiviijakiri_sesisestaja
        elif tname == 'vaatleja':
            self.page_template = labiviijakiri_vaatleja
        elif tname == 'hindaja':
            self.page_template = labiviijaakt_hindaja
        elif tname == 'tehindaja':
            self.page_template = labiviijakiri_tehindaja
        elif tname == 'sehindaja':
            self.page_template = labiviijakiri_sehindaja
        elif tname == 'tasemeeksam':
            self.page_template = labiviijakiri_tasemeeksam
        elif tname == 'seadus':
            self.page_template = labiviijakiri_seadus
        elif tname == 'riigieksam':
            # kõik muud testiliigid ka selle malliga
            self.page_template = labiviijakiri_riigieksam
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
