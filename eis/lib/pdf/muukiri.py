from datetime import datetime
import eis.model as model
from eis.model import const

from . import pages_loader
from .pdfdoc import *
from .pages.pdfutils import *
from .pages import muukiri

class MuukiriDoc(PdfDoc):
    pagenumbers = True
    
    def __init__(self, handler, testiliik, protsess=None):
        self.handler = handler
        self.testiliik = testiliik
        self.protsess = protsess
        self.page_template = muukiri
        self._register_arialnarrow_font()

    def _doctemplate(self, output):
        "PDFi dokumendi loomine"
        # vähendame ylemist äärt, et aadress jääks ymbriku aadressiaknasse
        return SimpleDocTemplate(output, topMargin=13*mm, leftMargin=15*mm, rightMargin=15*mm, bottomMargin=6*mm)
        
    def gen_story(self, kasutajad, get_sooritused, taiendavinfo=None):
        story = []
        aeg = datetime.now()
        total = len(kasutajad)
        for ind, k in enumerate(kasutajad):
            sooritused = get_sooritused(k)
            if len(sooritused):
                sooritaja_story = []
                if self.testiliik not in (const.TESTILIIK_RIIGIEKSAM, const.TESTILIIK_RV):
                    k = k.kasutaja                
                self.page_template.generate(sooritaja_story, 
                                            k,
                                            taiendavinfo)
                story.extend(sooritaja_story)

                sooritaja_d = MuukiriDoc(self.handler, self.testiliik)
                sooritaja_data = sooritaja_d.generate_from_story(sooritaja_story)

                kiri = model.Kiri(saatja_kasutaja_id=self.handler.c.user.id,
                                  tyyp=model.Kiri.TYYP_MUU,
                                  filename='teade.pdf',
                                  filedata=sooritaja_data,
                                  teema='Teade',
                                  teatekanal=const.TEATEKANAL_POST)

                for sooritaja in set([rcd.sooritaja for rcd in sooritused]):
                    model.Sooritajakiri(sooritaja=sooritaja, kiri=kiri)
                    sooritaja.meeldetuletusaeg = aeg
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

