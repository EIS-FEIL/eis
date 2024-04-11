# -*- coding: utf-8 -*- 

from eis.lib.baseresource import *
_ = i18n._
from eis.lib.basegrid import BaseGridController
from eis.lib.xtee import rahvastikuregister
log = logging.getLogger(__name__)

class TagastustoimumisedController(BaseResourceController):
    _permission = 'korraldamine'
    _MODEL = model.Hindamisprotokoll
    #_SEARCH_FORM = forms.admin.KasutajadForm
    #_ITEM_FORM = forms.admin.KasutajaForm
    _INDEX_TEMPLATE = '/ekk/korraldamine/tagastus.toimumised.mako' 
    #_EDIT_TEMPLATE = '/admin/kasutaja.nousolekud.mako' # muutmisvormi mall
    _LIST_TEMPLATE = '/ekk/korraldamine/tagastus.toimumised_list.mako'
    _DEFAULT_SORT = '-toimumisprotokoll.id'
    #_PARTIAL = True

    def _search(self, q):
        """Otsinguvormi päringu koostamine ning 
        otsitingimuste meelde jätmine c sees.
        """
        if self.c.testikoht_id:
            q = q.filter(model.Testikoht.id==int(self.c.testikoht_id))
        return q

    def _query(self):
        # leiame kinnitamata toimumise protokollid,
        # mis on kas seotud antud toimumisajaga
        # või kui on testimiskorra-põhised protokollid, siis seotud antud testimiskorraga
        q = (model.SessionR.query(model.Toimumisprotokoll, model.Koht.nimi)
             .join(model.Toimumisprotokoll.koht)
             .filter(model.Toimumisprotokoll.staatus != const.B_STAATUS_KINNITATUD)
             .filter(model.Toimumisprotokoll.staatus != const.B_STAATUS_EKK_KINNITATUD)
             .filter(sa.or_(
                 model.Toimumisprotokoll.testikoht.has(
                     model.Testikoht.toimumisaeg_id==self.c.toimumisaeg.id),
                 sa.and_(model.Toimumisprotokoll.testikoht_id==None,
                         model.Toimumisprotokoll.testimiskord_id==self.c.toimumisaeg.testimiskord_id)
                 ))
             )
        return q

    def __before__(self):
        self.c.toimumisaeg = model.Toimumisaeg.get(self.request.matchdict.get('toimumisaeg_id'))

    def _perm_params(self):
        return {'obj':self.c.toimumisaeg.testiosa.test}
