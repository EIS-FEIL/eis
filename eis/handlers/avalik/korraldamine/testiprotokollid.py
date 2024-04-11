# -*- coding: utf-8 -*- 

from eis.lib.baseresource import *
_ = i18n._
from eis.lib.basegrid import *

log = logging.getLogger(__name__)

class TestiprotokollidController(BaseResourceController):
    _permission = 'avalikadmin'
    _MODEL = model.Testiprotokoll
    #_INDEX_TEMPLATE = 'avalik/korraldamine/sooritajad.mako' 
    #_DEFAULT_SORT = 'kasutaja.nimi'
    #_ITEM_FORM = forms.avalik.admin.KSooritajadForm

    def create(self):
        tmp_tahised = 'tmp%s_%s' % (self.c.user.id, self.c.user.gen_pwd(20))
        tpr = model.Testiprotokoll(testipakett=self.c.testipakett,
                                   testiruum=self.c.testiruum,
                                   tahis='',
                                   tahised=tmp_tahised
                                   )
        tpr.gen_tahis()
        model.Session.commit()
        return HTTPFound(location=self.url('korraldamine_sooritajad', 
                                           toimumisaeg_id=self.c.toimumisaeg.id,
                                           testikoht_id=self.c.testikoht.id))

    def delete(self):
        try:
            tpr_id = self.request.matchdict.get('id')
            tpr = model.Testiprotokoll.get(tpr_id)
            tpr.delete()
            model.Session.commit()
        except Exception as e:
            self.error(_("Kustutamine ebaõnnestus") + ' (%s)' % repr(e))
        else:
            self.success(_("Protokollirühm on kustutatud"))
            
        return HTTPFound(location=self.url('korraldamine_sooritajad', 
                                           toimumisaeg_id=self.c.toimumisaeg.id,
                                           testikoht_id=self.c.testikoht.id))        
                    
    def __before__(self):
        self.c.testikoht = model.Testikoht.get(self.request.matchdict.get('testikoht_id'))
        self.c.testipakett = model.Testipakett.get(self.request.matchdict.get('testipakett_id'))
        self.c.testiruum = model.Testiruum.get(self.request.matchdict.get('testiruum_id'))        
        assert self.c.testiruum.testikoht == self.c.testikoht, _("Vale koht")
        assert self.c.testikoht == self.c.testipakett.testikoht, _("Vale koht")
        self.c.toimumisaeg = self.c.testikoht.toimumisaeg

