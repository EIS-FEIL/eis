# -*- coding: utf-8 -*- 

from eis.lib.baseresource import *
_ = i18n._
from eis.lib.basegrid import BaseGridController
from eis.lib.xtee import rahvastikuregister
log = logging.getLogger(__name__)

class AjaluguController(BaseResourceController):
    _MODEL = model.Labiviija
    _SEARCH_FORM = forms.admin.KasutajaajaluguForm
    #_ITEM_FORM = forms.admin.KasutajaForm
    _INDEX_TEMPLATE = '/admin/kasutaja.ajalugu.mako' 
    _LIST_TEMPLATE = '/admin/kasutaja.ajalugu_list.mako'
    _DEFAULT_SORT = '-toimumisaeg.alates'

    _permission = 'kasutajad'

    def _search(self, q):
        """Otsinguvormi päringu koostamine ning 
        otsitingimuste meelde jätmine c sees.
        """
        if self.c.testsessioon_id:
            q = q.filter(model.Testimiskord.testsessioon_id==int(self.c.testsessioon_id))
        if self.c.alates:
            q = q.filter(model.Toimumisaeg.kuni >= self.c.alates)
        if self.c.kuni:
            q = q.filter(model.Toimumisaeg.alates <= self.c.kuni)

        liigid = self.c.user.get_testiliigid(self._permission)
        if None not in liigid:
            q = q.filter(model.Testimiskord.test.has(model.Test.testiliik_kood.in_(liigid)))
        return q

    def _query(self):
        q = model.Labiviija.query.\
            filter_by(kasutaja_id=self.c.kasutaja.id).\
            filter(model.Labiviija.testiruum_id != None).\
            filter(model.Labiviija.kasutajagrupp_id != const.GRUPP_HIND_INT).\
            join(model.Labiviija.toimumisaeg).\
            join(model.Toimumisaeg.testimiskord)
        return q
    
    def __before__(self):
        self.c.kasutaja = model.Kasutaja.get(self.request.matchdict.get('kasutaja_id'))
