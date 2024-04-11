from datetime import datetime
from pypdf import PdfWriter
import eis.model as model
from eis.model import const

from . import pages_loader
from .pdfdoc import *
from .pages.pdfutils import *
from .pages import kohateade_r, kohateade_rv, kohateade_se, kohateade_te, kohateade_ss, kohateade_ke

class KohateadeDoc(PdfDoc):
    pagenumbers = True
    
    def __init__(self, handler, testiliik, protsess=None):
        self.handler = handler
        self.testiliik = testiliik
        self.protsess = protsess
        if testiliik == const.TESTILIIK_RIIGIEKSAM:
            self.page_template = kohateade_r
        elif testiliik == const.TESTILIIK_RV:
            self.page_template = kohateade_rv            
        elif testiliik == const.TESTILIIK_TASE:
            self.page_template = kohateade_te
        elif testiliik == const.TESTILIIK_SEADUS:
            self.page_template = kohateade_se
        elif testiliik == const.TESTILIIK_SISSE:
            self.page_template = kohateade_ss
        elif testiliik == const.TESTILIIK_KUTSE:
            self.page_template = kohateade_ke                        
        else:
            raise Exception('Testiliigile %s ei ole kohateateid ette nähtud' % testiliik)

        self._register_arialnarrow_font()

    def _doctemplate(self, output):
        "PDFi dokumendi loomine"
        # vähendame ylemist äärt, et aadress jääks ymbriku aadressiaknasse
        return SimpleDocTemplate(output, topMargin=13*mm, leftMargin=15*mm, rightMargin=15*mm, bottomMargin=8*mm)

    def generate(self, **kw):
        kasutajad = kw.get('kasutajad')
        get_sooritused = kw.get('get_sooritused')
        taiendavinfo = kw.get('taiendavinfo')
        log.info('KohateadeDoc generate')
        merger = PdfWriter()
        aeg = datetime.now()
        total = len(kasutajad)
        for ind, k in enumerate(kasutajad):
            sooritused = get_sooritused(k)
            if len(sooritused):
                story = []
                self.page_template.generate(story, 
                                            k,
                                            sooritused,
                                            taiendavinfo)

                # igale isikule oma fail
                sooritaja_d = KohateadeDoc(self.handler, self.testiliik)
                filedata = sooritaja_d.generate_from_story(story)
                # isiku fail lisatakse suurde, mis läheb väljatrükkimiseks
                merger.append(io.BytesIO(filedata))

                # isiku fail salvestatakse minu teadete alla
                kiri = model.Kiri(saatja_kasutaja_id=self.handler.c.user.id,
                                  tyyp=model.Kiri.TYYP_SOORITUSKOHATEADE,
                                  filename='soorituskohateade.pdf',
                                  filedata=filedata,
                                  teema='Kohateade',
                                  teatekanal=const.TEATEKANAL_POST)

                for sooritaja in set([rcd.sooritaja for rcd in sooritused]):
                    model.Sooritajakiri(sooritaja=sooritaja, kiri=kiri)
                    sooritaja.meeldetuletusaeg = aeg

                if self.testiliik not in (const.TESTILIIK_RIIGIEKSAM, const.TESTILIIK_RV):
                    k = k.kasutaja
                model.Kirjasaaja(kiri=kiri, kasutaja=k)

                if self.protsess:
                    protsent = round(ind * 100 / total, -1)
                    self._save_protsess(protsent)

        output = io.BytesIO()
        merger.write(output)
        merger.close()
        data = output.getvalue()
        output.close()
        
        if self.protsess:
            buf = "Koostatud {n} kirja".format(n=total)
            self.protsess.set_viga(buf)
        model.Session.commit()
        return data

    def _save_protsess(self, protsent):
        if self.protsess.lopp:
            raise ProcessCanceled()
        if protsent > self.protsess.edenemisprotsent:
            self.protsess.edenemisprotsent = protsent
            #model.Session.commit()


