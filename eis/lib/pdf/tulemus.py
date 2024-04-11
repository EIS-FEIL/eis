"Tulemuste teavitused TE ja SE eksamitel"

from datetime import datetime

import eis.model as model
from eis.model import const

from . import pages_loader
from .pdfdoc import *
from .pages.pdfutils import *
from .pages import tulemus_te, tulemus_se

class TulemusDoc(PdfDoc):
    pagenumbers = True
    
    def __init__(self, handler, testiliik, protsess=None):
        self.handler = handler
        self.testiliik = testiliik
        self.protsess = protsess
        if testiliik == const.TESTILIIK_TASE:
            self.page_template = tulemus_te
        elif testiliik == const.TESTILIIK_SEADUS:
            self.page_template = tulemus_se
        else:
            raise Exception('Testiliigile %s ei ole teateid ette nähtud' % testiliik)

    def _doctemplate(self, output):
        "PDFi dokumendi loomine"
        # vähendame ylemist äärt, et aadress jääks ymbriku aadressiaknasse
        return SimpleDocTemplate(output,
                                 leftMargin=15*mm,
                                 rightMargin=15*mm,
                                 topMargin=13*mm,
                                 bottomMargin=25*mm)
        
    def gen_story(self, items, taiendavinfo=None):
        aeg = datetime.now()
        story = []
        total = len(items)
        for ind, item in enumerate(items):
            sooritaja = model.Sooritaja.get(item[5])
            sooritaja_story = []
            self.page_template.generate(sooritaja_story, sooritaja, taiendavinfo)

            story.extend(sooritaja_story)

            sooritaja_d = TulemusDoc(self.handler, self.testiliik)
            sooritaja_data = sooritaja_d.generate_from_story(sooritaja_story)

            kiri = model.Kiri(saatja_kasutaja_id=self.handler.c.user.id,
                              tyyp=model.Kiri.TYYP_TULEMUS,
                              filename='tulemus.pdf',
                              filedata=sooritaja_data,
                              teema='Tulemuste teavitus',
                              teatekanal=const.TEATEKANAL_POST)

            model.Sooritajakiri(sooritaja=sooritaja, kiri=kiri)
            sooritaja.meeldetuletusaeg = aeg
            k = sooritaja.kasutaja
            model.Kirjasaaja(kiri=kiri, kasutaja=k)
            if self.protsess:
                protsent = round(ind * 100 / total, -1)
                self._save_protsess(protsent)
        if self.protsess:
            buf = "Koostatud {n} kirja".format(n=total)
            self.protsess.set_viga(buf)
        model.Session.commit()
        return story

    def _save_protsess(self, protsent):
        if self.protsess.lopp:
            raise ProcessCanceled()
        if protsent > self.protsess.edenemisprotsent:
            self.protsess.edenemisprotsent = protsent
            #model.Session.commit()

