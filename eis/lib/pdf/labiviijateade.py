from datetime import datetime
import eis.model as model
from eis.model import const

from . import pages_loader
from .pdfdoc import *
from .pages.pdfutils import *
from .pages import labiviijateade, labiviijameeldetuletus

class LabiviijateadeDoc(PdfDoc):

    def __init__(self, handler, tyyp, testiliik):
        self.handler = handler
        self.tyyp = tyyp
        self.testiliik = testiliik
        if tyyp == model.Kiri.TYYP_LABIVIIJA_MEELDE:
            self.page_template = labiviijameeldetuletus
        else:
            self.page_template = labiviijateade


    def _doctemplate(self, output):
        "PDFi dokumendi loomine"
        # vähendame ääri
        return SimpleDocTemplate(output, leftMargin=18*mm, rightMargin=18*mm)
        
    def gen_story(self, items, get_labiviijad):
        story = []
        aeg = datetime.now()
        for item in items:
            k_story = []
            labiviijad = get_labiviijad(item)
            self.page_template.generate(k_story, 
                                        item,
                                        labiviijad,
                                        self.testiliik)
            story.extend(k_story)

            k_d = LabiviijateadeDoc(self.handler, self.tyyp, self.testiliik)
            k_data = k_d.generate_from_story(k_story)
            
            for lv in labiviijad:
                if self.tyyp == model.Kiri.TYYP_LABIVIIJA_MEELDE:
                    lv.meeldetuletusaeg = aeg
                    teema = 'Läbiviija meeldetuletus'
                else:
                    lv.teateaeg = aeg
                    teema = 'Läbiviija teade'

            kiri = model.Kiri(saatja_kasutaja_id=self.handler.c.user.id,
                              tyyp=self.tyyp,
                              teema=teema,
                              teatekanal=const.TEATEKANAL_POST,
                              filename='labiviijateade.pdf',
                              filedata=k_data)
            for lv in labiviijad:
                model.Labiviijakiri(labiviija=lv, kiri=kiri)
            model.Kirjasaaja(kiri=kiri, kasutaja_id=item[0])

        model.Session.commit()
        return story


