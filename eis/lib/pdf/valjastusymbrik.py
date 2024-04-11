import sqlalchemy as sa
from reportlab.lib.units import mm
from .pdfdoc import PdfDoc, SimpleDocTemplate, C4

import eis.model as model       
from eis.model.usersession import _

class ValjastusymbrikDoc(PdfDoc):
    pagenumbers = True
    
    def __init__(self, toimumisaeg, params, order_by):
        self.toimumisaeg = toimumisaeg
        self.order_by = ','.join(order_by)
        self.piirkond_id = params.get('piirkond_id')
        self.testikoht_id = params.get('testikoht_id')
        self.params = params
        self.on_kleeps = 'kleeps' in params

    def _doctemplate(self, output):
        "PDFi dokumendi loomine"
        if self.on_kleeps:
            return SimpleDocTemplate(output, 
                                     pagesize=(100*mm,50*mm),
                                     leftMargin=0*mm,
                                     rightMargin=0*mm,
                                     topMargin=2*mm,
                                     bottomMargin=1*mm)
        else:
            return SimpleDocTemplate(output, pagesize=C4)
        
    def gen_story(self):
        valjastusymbrik_t = self._load_template('valjastusymbrik')
        if not valjastusymbrik_t:
            self.error = _('Väljastusümbriku mall on valimata')
            return
        if not self.toimumisaeg.on_paketid:
            self.error = _("E-testis ei kasutata ümbrikke")
            return
        
        # väljastusümbrike liigid
        
        vliigid_id = [liik_t['liik_id'] for liik_t in valjastusymbrik_t]

        story = []
        q = (model.Session.query(model.Valjastusymbrik,
                                 model.Valjastusymbrikuliik,
                                 model.Testiruum.algus,
                                 model.Testiruum.tahis,
                                 model.Ruum.tahis,
                                 model.Testipakett,
                                 model.Koht)
             .filter(model.Valjastusymbrik.valjastusymbrikuliik_id.in_(vliigid_id))
             .join(model.Valjastusymbrik.valjastusymbrikuliik)
             .filter(model.Valjastusymbrikuliik.toimumisaeg_id==self.toimumisaeg.id)
             .join(model.Valjastusymbrik.testipakett)
             .outerjoin(model.Valjastusymbrik.testiruum)
             .outerjoin(model.Testiruum.ruum)
             .join(model.Testipakett.testikoht)
             .join(model.Testikoht.koht)
             .outerjoin(model.Koht.piirkond)
             )

        if self.testikoht_id:
            # soovitakse ainult antud testikoha väljatrükki
            q = q.filter(model.Testikoht.id==int(self.testikoht_id))
        elif self.piirkond_id:
            q = q.filter(model.Koht.piirkond_id==int(self.piirkond_id))
            
        q = q.order_by(sa.text(self.order_by + ',testiruum.tahis'))
        
        for rcd in q.all():
            ymbrik, yliik, tr_algus, tr_tahis, ruum_tahis, tpakett, koht = rcd

            if tr_tahis:
                # mitu samaliigilist ymbrikut on samas testipaketis enne seda ymbrikku
                cnt_index = yliik.get_count(tpakett.id, ymbrik.kursus_kood, tr_tahis)
            else:
                # ymbrik on kogu paketi kohta, seega esimene 
                cnt_index = 0
            # mitu samaliigilist ymbrikut on samas testipaketis kokku
            cnt_total = yliik.get_count(tpakett.id, ymbrik.kursus_kood)
            
            if not tr_tahis and not tr_algus:
                # kui pole ruumiga seotud ymbrik, siis leiame paketi varaseima ruumi algusaja
                q1 = (model.Session.query(sa.func.min(model.Testiruum.algus))
                      .join(model.Testiruum.sooritused)
                      .join(model.Sooritus.testiprotokoll)
                      .filter(model.Testiprotokoll.testipakett_id==tpakett.id))
                tr_algus = q1.scalar()

            liik_t = [l for l in valjastusymbrik_t if l['liik_id'] == ymbrik.valjastusymbrikuliik_id][0]
            avamisaeg = liik_t.get('avamisaeg')
            if tr_algus and avamisaeg:
                # muudame kellaaja selliseks, nagu kasutaja genereerimise vormil sisestas
                tr_algus = tr_algus.replace(hour=avamisaeg[0], minute=avamisaeg[1])
                
            template = liik_t['template']
            
            maht = yliik.maht
            jaanud_sooritusi = ymbrik.toodearv
            for y_cnt in range(ymbrik.ymbrikearv):
                ymbrikus_sooritusi = maht and min(maht, jaanud_sooritusi) or jaanud_sooritusi
                jaanud_sooritusi -= ymbrikus_sooritusi
                cnt = y_cnt + 1
                template.generate(story, self.toimumisaeg, rcd, ymbrikus_sooritusi,
                                  cnt, ymbrik.ymbrikearv,
                                  cnt_index + cnt, cnt_total, tr_algus)
                
        return story
