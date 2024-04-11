from reportlab.lib.units import mm
import sqlalchemy as sa
import eis.model as model
from eis.model.usersession import _
from eis.model import const
from .pdfdoc import PdfDoc, SimpleDocTemplate

class TurvakotikleebisDoc(PdfDoc):
    pagenumbers = True
    
    def __init__(self, toimumisaeg, params, order_by):
        self.toimumisaeg = toimumisaeg
        self.order_by = ','.join(order_by)
        self.piirkond_id = params.get('piirkond_id')
        self.testikoht_id = params.get('testikoht_id')
        self.params = params

    def _doctemplate(self, output):
        "PDFi dokumendi loomine"
        return SimpleDocTemplate(output, 
                                 pagesize=(100*mm,50*mm),
                                 leftMargin=0*mm,
                                 rightMargin=0*mm,
                                 topMargin=1*mm,
                                 bottomMargin=0*mm)
        
    def gen_story(self):
        vkotikleebis_t = self._load_template('vkotikleebis')
        tkotikleebis_t = self._load_template('tkotikleebis')        
        if not self.is_loaded:
            self.error = _('Turvakoti liik on valimata')
        elif not self.toimumisaeg.on_paketid:
            self.error = _("E-testis ei kasutata turvakotte")
        if self.error:
            return
        
        story = []
        q = model.Session.query(model.Testipakett,
                                model.Testikoht)
        q = q.join(model.Testipakett.testikoht).\
            filter(model.Testikoht.toimumisaeg_id==self.toimumisaeg.id).\
            join(model.Testikoht.koht).\
            outerjoin(model.Koht.piirkond).\
            outerjoin(model.Testipakett.testiruum)

        if self.testikoht_id:
            # soovitakse ainult antud testikoha väljatrükki
            q = q.filter(model.Testikoht.id==int(self.testikoht_id))            
        elif self.piirkond_id:
            # soovitakse ainult antud testikoha väljatrükki
            q = q.filter(model.Koht.piirkond_id==int(self.piirkond_id))

        q = q.order_by(sa.text(self.order_by + ',testiruum.tahis'))
        for rcd in q.all():
            testipakett, testikoht = rcd

            if vkotikleebis_t:
                for n, turvakott in enumerate(testipakett.valjastuskotid):
                    vkotikleebis_t.generate(story, self.toimumisaeg, testikoht, testipakett, turvakott, n+1)                

            if tkotikleebis_t:
                for n, turvakott in enumerate(testipakett.tagastuskotid):
                    tkotikleebis_t.generate(story, self.toimumisaeg, testikoht, testipakett, turvakott, n+1)                

        return story
