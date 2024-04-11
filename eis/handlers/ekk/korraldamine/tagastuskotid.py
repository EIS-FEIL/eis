# -*- coding: utf-8 -*- 
# $Id: tagastuskotid.py 406 2016-03-07 19:18:48Z ahti $

from eis.lib.baseresource import *
_ = i18n._
from eis.lib.basegrid import BaseGridController
from eis.lib.xtee import rahvastikuregister
log = logging.getLogger(__name__)

class TagastuskotidController(BaseResourceController):
    _permission = 'korraldamine'
    _MODEL = model.Turvakott
    #_SEARCH_FORM = forms.admin.KasutajadForm
    #_ITEM_FORM = forms.admin.KasutajaForm
    _INDEX_TEMPLATE = '/ekk/korraldamine/tagastus.kotid.mako' 
    #_EDIT_TEMPLATE = '/admin/kasutaja.nousolekud.mako' # muutmisvormi mall
    _LIST_TEMPLATE = '/ekk/korraldamine/tagastus.kotid_list.mako'
    _DEFAULT_SORT = '-turvakott.id'
    #_PARTIAL = True

    def _search(self, q):
        """Otsinguvormi päringu koostamine ning 
        otsitingimuste meelde jätmine c sees.
        """
        if self.c.testikoht_id:
            q = q.filter(model.Testikoht.id==int(self.c.testikoht_id))
        return q

    def _query(self):
        q = model.SessionR.query(model.Turvakott, model.Testipakett.lang, model.Koht.nimi).\
            filter(model.Turvakott.suund==const.SUUND_TAGASI).\
            join(model.Turvakott.testipakett).\
            join(model.Testipakett.testikoht).\
            join(model.Testikoht.koht).\
            filter(model.Turvakott.staatus != const.M_STAATUS_TAGASTATUD).\
            filter(model.Turvakott.staatus != const.M_STAATUS_HINNATUD).\
            filter(model.Testikoht.toimumisaeg_id==self.c.toimumisaeg.id)
        return q

    def __before__(self):
        self.c.toimumisaeg = model.Toimumisaeg.get(self.request.matchdict.get('toimumisaeg_id'))

    def _perm_params(self):
        return {'obj':self.c.toimumisaeg.testiosa.test}
    
