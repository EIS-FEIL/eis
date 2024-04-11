"Väljastusümbrikku lisatavate materjalide PDF dokument"

from reportlab.platypus import *
from datetime import datetime
import eis.model as model       
from eis.model import const
from .pdfdoc import *

class MaterjalDoc(PdfDoc):
    pagenumbers = True
    preview = False
    
    def __init__(self, toimumisaeg, params, order_by=[]):
        self.toimumisaeg = toimumisaeg
        self.order_by = ','.join(order_by)
        self.piirkond_id = params.get('piirkond_id')
        self.testikoht_id = params.get('testikoht_id')
        self.params = params
        self._register_barcode_font()

    def _doctemplate(self, output):
        "PDFi dokumendi loomine"
        return SimpleDocTemplate(output, 
                                 topMargin=10*mm, bottomMargin=10*mm, 
                                 rightMargin=10*mm, leftMargin=20*mm)
 
    def _first_page(self, canvas, doc):
        if self.preview:
            canvas.saveState()
            canvas.setFont("Helvetica", 150)
            canvas.setStrokeGray(0.90)
            canvas.setFillGray(0.90)
            watermark = 'eelvaade'
            canvas.drawCentredString(105*mm, 60*mm, watermark)
            canvas.drawCentredString(105*mm, 230*mm, watermark)
            canvas.restoreState()

    def _later_pages(self, canvas, doc):
        return self._first_page(canvas, doc)
        
    def gen_story(self):
        avamisprotokoll_t = self._load_template('avamisprotokoll')
        toimumisprotokoll_t = self._load_template('toimumisprotokoll')
        yleandmisprotokoll_t = self._load_template('yleandmisprotokoll')
        hindamisprotokoll_t = self._load_template('hindamisprotokoll')
        hindamisprotokoll3_t = self._load_template('hindamisprotokoll3')        
        nimekiri_t = self._load_template('nimekiri')
        ryhmanimekiri_t = self._load_template('ryhmanimekiri')
        regnimekiri_t = self._load_template('regnimekiri')
        saatekiri_t = self._load_template('saatekiri')        
        lisatingimused_t = self._load_template('lisatingimused')
        shindajakoodid_t = self._load_template('shindajakoodid')
        
        if not self.is_loaded:
            self.error = 'Materjali liik on valimata'
        if self.error:
            return
        
        if lisatingimused_t:
            return self.gen_story_lisatingimused(lisatingimused_t)

        story = []
        q = (model.SessionR.query(model.Testikoht, model.Testipakett)
             .filter(model.Testikoht.toimumisaeg_id==self.toimumisaeg.id)
             .outerjoin(model.Testikoht.testipaketid)
             .join(model.Testikoht.koht)
             .outerjoin(model.Koht.piirkond)
             .outerjoin(model.Testipakett.testiruum))

        if self.testikoht_id:
            # soovitakse ainult antud testikoha väljatrükki
            q = q.filter(model.Testikoht.id==int(self.testikoht_id))
        elif self.piirkond_id:
            q = q.filter(model.Koht.piirkond_id==self.piirkond_id)

        if self.order_by:
            q = q.order_by(model.sa.text(self.order_by + ',testiruum.tahis'))

        testikohad_id = []
        for rcd in q.all():
            testikoht, testipakett = rcd
            lang = testipakett and testipakett.lang or None

            # testiprotokollid
            qtpr = (model.SessionR.query(model.Testiprotokoll)
                    .join(model.Testiprotokoll.testiruum))
            if testipakett:
                qtpr = qtpr.filter(model.Testiprotokoll.testipakett_id==testipakett.id)
            else:
                qtpr = qtpr.filter(model.Testiruum.testikoht_id==testikoht.id)
            testiprotokollid = qtpr.order_by(model.Testiprotokoll.tahis).all()
            
            if self.params.get('nimekiri') and testipakett and testipakett.testiruum_id:
                # igal ruumil on oma pakett ja peaümbrik, 
                # paketid pannakse kasti ja pakettide juurde, väljaspool peaümbrikku,
                # jäetakse tähestikuline nimekiri
                if testikoht.id not in testikohad_id:
                    # kui selle koha nimekirja pole veel tehtud, siis teeme, kordama ei hakka
                    testikohad_id.append(testikoht.id)
                    qi = (model.SessionR.query(model.Sooritaja.eesnimi,
                                              model.Sooritaja.perenimi,
                                              model.Ruum.tahis,
                                              model.Testiprotokoll.tahis)
                          .join(model.Testiprotokoll.testiruum)
                          .filter(model.Testiruum.testikoht_id==testikoht.id)
                          .join(model.Testiprotokoll.sooritused)
                          .join(model.Sooritus.sooritaja)
                          .filter(model.Sooritaja.staatus>const.S_STAATUS_REGAMATA)
                          .filter(model.Sooritus.testikoht_id==testikoht.id)
                          .filter(model.Sooritus.staatus!=const.S_STAATUS_VABASTATUD)
                          .outerjoin(model.Testiruum.ruum)
                          .order_by(model.Sooritaja.perenimi,model.Sooritaja.eesnimi))
                    items = qi.all()
                    nimekiri_t.generate(story, self.toimumisaeg, testikoht, lang, items)

            if self.params.get('saatekiri') and testipakett:
                # ainult p-test
                saatekiri_t.generate(story, self.toimumisaeg, testikoht, testipakett)

            if self.params.get('nimekiri') and (not testipakett or not testipakett.testiruum_id):
                # tähestikuline nimekiri juhul, kui testikoha kohta on üks pakett
                # leitakse testikoha kõigi selles keeles sooritajate nimekiri
                qi = (model.SessionR.query(model.Sooritaja.eesnimi,
                                          model.Sooritaja.perenimi,
                                          model.Ruum.tahis,
                                          model.Testiprotokoll.tahis)
                      .join(model.Testiprotokoll.testiruum)
                      .filter(model.Testiruum.testikoht_id==testikoht.id)
                      .join(model.Testiprotokoll.sooritused)
                      .join(model.Sooritus.sooritaja)
                      .filter(model.Sooritaja.staatus>const.S_STAATUS_REGAMATA)
                      .filter(model.Sooritus.staatus!=const.S_STAATUS_VABASTATUD)
                      .outerjoin(model.Testiruum.ruum)
                      .order_by(model.Sooritaja.perenimi,model.Sooritaja.eesnimi))
                items = qi.all()
                nimekiri_t.generate(story, self.toimumisaeg, testikoht, lang, items)

            if self.params.get('ryhmanimekiri'):
                # leitakse testikoha kõik protokollirühmad selles keeles
                for tpr in testiprotokollid:
                    ryhmanimekiri_t.generate(story, self.toimumisaeg, testikoht, lang, tpr)
                # ryhmanimekirjade vahel ei ole lehekyljevahetust, lisame selle peale viimast ryhma
                story.append(PageBreak())

            if self.params.get('regnimekiri'):
                # leitakse testikoha kõik protokollirühmad selles keeles
                for tpr in testiprotokollid:
                    # leitakse selle protokollirühma sooritajate nimekiri
                    qi = (model.SessionR.query(model.Sooritaja.eesnimi,
                                             model.Sooritaja.perenimi,
                                             model.Kasutaja.isikukood,
                                             model.Kasutaja.synnikpv)
                          .filter(model.Sooritaja.staatus>const.S_STAATUS_REGAMATA)
                          .join(model.Sooritaja.sooritused)
                          .filter(model.Sooritus.testiprotokoll_id==tpr.id)
                          .filter(model.Sooritus.staatus!=const.S_STAATUS_VABASTATUD)
                          .join(model.Sooritaja.kasutaja)
                          .order_by(model.Sooritaja.perenimi,model.Sooritaja.eesnimi))
                    items = qi.all()
                    regnimekiri_t.generate(story, self.toimumisaeg, testikoht, lang, items, tpr)
                    story.append(PageBreak())

            if self.params.get('avamisprotokoll'):
                avamisprotokoll_t.generate(story, self.toimumisaeg, testikoht, testipakett)
            if self.params.get('toimumisprotokoll'):
                if testipakett:
                    testiruum_id = testipakett.testiruum_id or None
                    toimumisprotokoll = testikoht.get_toimumisprotokoll(lang, testiruum_id)
                    if toimumisprotokoll:
                        toimumisprotokoll_t.generate(story, testikoht, toimumisprotokoll)
                else:
                    for toimumisprotokoll in testikoht.toimumisprotokollid:
                        toimumisprotokoll_t.generate(story, testikoht, toimumisprotokoll)
                        
            if self.params.get('shindajakoodid'):
                shindajakoodid_t.generate(story, self.toimumisaeg, testikoht, testipakett)               

            for tpr in testiprotokollid:
                if self.params.get('yleandmisprotokoll'):
                    yleandmisprotokoll_t.generate(story, self.toimumisaeg, testikoht, testipakett, tpr)
            
                # otsime kõik hindamisprotokollid
                qhpr = (model.SessionR.query(model.Hindamisprotokoll, model.Sisestuskogum)
                        .filter(model.Hindamisprotokoll.testiprotokoll_id==tpr.id)
                        .join(model.Hindamisprotokoll.sisestuskogum)
                        .order_by(model.Sisestuskogum.tahis,model.Hindamisprotokoll.liik))

                if self.params.get('hindamisprotokoll'):
                    for hpr_rcd in qhpr.filter(model.Hindamisprotokoll.liik<const.HINDAJA3).all():
                        hpr, skogum = hpr_rcd
                        
                        for hkogum in skogum.hindamiskogumid:
                            kvalik = hkogum.get_komplektivalik()
                            for komplekt in self.toimumisaeg.komplektid:
                                if komplekt.komplektivalik_id == kvalik.id:
                                    hindamisprotokoll_t.generate(story, self.toimumisaeg, testikoht, lang, tpr, hpr, skogum, hkogum, komplekt)
                                    if not hkogum.erinevad_komplektid:
                                        # esimese komplekti põhjal koostatud protokoll kehtib 
                                        # kõigile protokollidele, mistõttu neid rohkem pole vaja teha
                                        break

                if self.params.get('hindamisprotokoll3'):
                    for hpr_rcd in qhpr.filter(model.Hindamisprotokoll.liik==const.HINDAJA3).all():
                        hpr, skogum = hpr_rcd
                        
                        for hkogum in skogum.hindamiskogumid:
                            kvalik = hkogum.get_komplektivalik()
                            for komplekt in self.toimumisaeg.komplektid:
                                if komplekt.komplektivalik_id == kvalik.id:
                                    hindamisprotokoll3_t.generate(story, self.toimumisaeg, testikoht, lang, tpr, hpr, skogum, hkogum, komplekt)
                                    if not hkogum.erinevad_komplektid:
                                        # esimese komplekti põhjal koostatud protokoll kehtib 
                                        # kõigile protokollidele, mistõttu neid rohkem pole vaja teha
                                        break

        return story

    def gen_story_lisatingimused(self, template):
        q = model.SessionR.query(model.Kasutaja.isikukood,
                                model.Kasutaja.synnikpv,
                                model.Sooritaja.eesnimi,
                                model.Sooritaja.perenimi,
                                model.Sooritus,
                                model.Kasutaja.lisatingimused).\
            join(model.Kasutaja.sooritajad).\
            join(model.Sooritaja.sooritused).\
            filter(model.Sooritus.toimumisaeg_id==self.toimumisaeg.id)

        
        erivajadustega = q.filter(model.Sooritus.on_erivajadused_kinnitatud==True).\
            order_by(model.Sooritaja.perenimi, model.Sooritaja.eesnimi).\
            all()
        
        lisatingimustega = q.filter(model.Kasutaja.lisatingimused!=None).\
            filter(model.Kasutaja.lisatingimused!='').\
            order_by(model.Sooritaja.perenimi, model.Sooritaja.eesnimi).\
            all()

        story = []
        template.generate(story, self.toimumisaeg, erivajadustega, lisatingimustega)
        return story


        

        
