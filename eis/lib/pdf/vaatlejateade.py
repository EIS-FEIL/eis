from datetime import datetime

import eis.model as model
from eis.model import const

from . import pages_loader
from .pdfdoc import *
from .pages.pdfutils import *
from .pages import vaatlejateade, vaatlejameeldetuletus

class VaatlejateadeDoc(PdfDoc):

    def __init__(self, handler, tyyp):
        self.handler = handler
        self.tyyp = tyyp
        if tyyp == model.Kiri.TYYP_LABIVIIJA_MEELDE:
            self.page_template = vaatlejameeldetuletus
        else:
            self.page_template = vaatlejateade


    def _doctemplate(self, output):
        "PDFi dokumendi loomine"
        # vähendame ääri
        return SimpleDocTemplate(output, leftMargin=18*mm, rightMargin=18*mm)
        
    def gen_story(self, items, get_labiviijad, taiendavinfo):
        story = []
        for k in items:
            k_story = []
            labiviijad = get_labiviijad(k)
            self.page_template.generate(k_story, 
                                        k,
                                        labiviijad,
                                        taiendavinfo)
            story.extend(k_story)
            for lv in labiviijad:
                if self.tyyp == model.Kiri.TYYP_LABIVIIJA_MEELDE:
                    lv.meeldetuletusaeg = datetime.now()
                else:
                    lv.teateaeg = datetime.now()

            k_d = VaatlejateadeDoc(self.handler, self.tyyp)
            k_data = k_d.generate_from_story(k_story)
            teema = 'Vaatleja teade'
            kiri = model.Kiri(saatja_kasutaja_id=self.handler.c.user.id,
                              tyyp=self.tyyp,
                              teema=teema,
                              teatekanal=const.TEATEKANAL_POST,
                              filename='labiviijateade.pdf',
                              filedata=k_data)
            for lv in labiviijad:
                model.Labiviijakiri(labiviija=lv, kiri=kiri)
            model.Kirjasaaja(kiri=kiri, kasutaja_id=k.id)

        model.Session.commit()

                    
        return story


