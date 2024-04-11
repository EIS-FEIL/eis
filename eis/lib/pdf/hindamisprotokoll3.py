# -*- coding: utf-8 -*- 
# $Id: hindamisprotokoll3.py 9 2015-06-30 06:34:46Z ahti $
"III hindamise protokollid"

from reportlab.platypus import *

import eis.model as model       
from eis.model import const
from .pdfdoc import *
from .pages import hindamisprotokoll_tavaline

class Hindamisprotokoll3Doc(PdfDoc):
    pagenumbers = True
    
    def __init__(self, toimumisaeg, hindaja):
        self.toimumisaeg = toimumisaeg
        self.hindaja = hindaja
        self._register_barcode_font()

    def _doctemplate(self, output):
        "PDFi dokumendi loomine"
        return SimpleDocTemplate(output, 
                                 topMargin=10*mm, bottomMargin=10*mm, 
                                 rightMargin=10*mm, leftMargin=20*mm)
        
    def gen_story(self):
        hindamisprotokoll_t = hindamisprotokoll_tavaline
        
        story = []
        # otsime kõik antud hindaja hindamisprotokollid
        qhpr = model.SessionR.query(model.Hindamisprotokoll, model.Sisestuskogum, model.Testiprotokoll,
                                   model.Testikoht, model.Testipakett).\
               join(model.Hindamisprotokoll.sisestuskogum).\
               filter(model.Hindamisprotokoll.hindamised.any(model.Hindamine.labiviija==self.hindaja)).\
               join(model.Hindamisprotokoll.testiprotokoll).\
               join(model.Testiprotokoll.testipakett).\
               join(model.Testipakett.testikoht).\
               order_by(model.Testiprotokoll.tahised)
        for hpr_rcd in qhpr.all():
            hpr, skogum, tpr, testikoht, testipakett = hpr_rcd
            for hkogum in skogum.hindamiskogumid:
                kvalik = hkogum.get_komplektivalik()
                for komplekt in self.toimumisaeg.komplektid:
                    if komplekt.komplektivalik == kvalik:
                        hindamisprotokoll_t.generate(story, self.toimumisaeg, testikoht, testipakett.lang, tpr, hpr, skogum, hkogum, komplekt)
                        if not hkogum.erinevad_komplektid:
                            # esimese komplekti põhjal koostatud protokoll kehtib 
                            # kõigile protokollidele, mistõttu neid rohkem pole vaja teha
                            break

        return story
