# -*- coding: utf-8 -*- 
"Konsultatsiooni materjalid"

from reportlab.platypus import *
import sqlalchemy as sa
import eis.model as model       
from eis.model import const, sa
from .pdfdoc import *

class KonsnimekiriDoc(PdfDoc):
    #pagenumbers = True
    
    def __init__(self, toimumisaeg, params, order_by=[]):
        self.toimumisaeg = toimumisaeg
        self.order_by = ','.join(order_by)
        self.piirkond_id = params.get('piirkond_id')
        self.params = params
        self._register_barcode_font()

    def _doctemplate(self, output):
        "PDFi dokumendi loomine"
        return SimpleDocTemplate(output, 
                                 topMargin=10*mm, bottomMargin=10*mm, 
                                 rightMargin=10*mm, leftMargin=20*mm)
        
    def gen_story(self):
        konsnimekiri_t = self._load_template('konsnimekiri')
        konsprotokoll_t = self._load_template('konsprotokoll')

        if not self.is_loaded:
            self.error = 'Materjali liik on valimata'
        if self.error:
            return
        
        story = []

        # testikohtade päring
        q = model.SessionR.query(model.Testikoht, model.Piirkond).\
            filter(model.Testikoht.toimumisaeg_id==self.toimumisaeg.id).\
            join(model.Testikoht.koht).\
            outerjoin(model.Koht.piirkond)

        # testikoha piirkonnas olevate sooritajate päring
        qi = model.SessionR.query(model.Sooritaja.eesnimi,
                                 model.Sooritaja.perenimi,
                                 model.Kasutaja.isikukood,
                                 model.Kasutaja.synnikpv)
        qi = qi.join(model.Sooritaja.kasutaja).\
            filter(model.Sooritaja.soovib_konsultatsiooni==True).\
            filter(model.Sooritaja.staatus>const.S_STAATUS_REGAMATA).\
            join((model.Testikonsultatsioon,
                  sa.and_(model.Testikonsultatsioon.eksam_testimiskord_id==model.Sooritaja.testimiskord_id,
                          model.Testikonsultatsioon.kons_testimiskord_id==self.toimumisaeg.testimiskord_id)))

        #if self.testikoht_id:
        #    # soovitakse ainult antud testikoha väljatrükki
        #    q = q.filter(model.Testikoht.id==int(self.testikoht_id))
        if self.piirkond_id:
            prk = model.Piirkond.get(self.piirkond_id)
            piirkonnad_id = prk.get_alamad_id()
            q = q.filter(model.Koht.piirkond_id.in_(piirkonnad_id))

        if self.order_by:
            q = q.order_by(sa.text(self.order_by))

        for rcd in q.all():
            testikoht, prk = rcd
            if prk:
                piirkonnad_id = prk.get_ylemad_id()
            else:
                piirkonnad_id = []

            q2 = qi.filter(model.Sooritaja.piirkond_id.in_(piirkonnad_id)).\
                order_by(model.Sooritaja.perenimi,model.Sooritaja.eesnimi)
            items = q2.all()

            if self.params.get('konsnimekiri'):
                konsnimekiri_t.generate(story, self.toimumisaeg, testikoht, items)

            if self.params.get('konsprotokoll'):
                konsprotokoll_t.generate(story, self.toimumisaeg, testikoht, items)

        return story

