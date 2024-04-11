# -*- coding: utf-8 -*- 

from eis.lib.baseresource import *
_ = i18n._

log = logging.getLogger(__name__)

class VersioonidController(BaseResourceController):
    """Versioonid
    """
    _permission = 'ylesanded'

    _MODEL = model.Ylesandeversioon
    _INDEX_TEMPLATE = 'ekk/ylesanded/versioonid.mako'
    _ITEM_FORM = None #forms.ekk.ylesanded.MuutjadForm 
    _DEFAULT_SORT = 'ylesandeversioon.seq' # vaikimisi sortimine
    _no_paginate = True
    
    def _query(self):
        return model.Session.query(model.Ylesandeversioon).\
               filter(model.Ylesandeversioon.ylesanne_id==self.c.ylesanne.id)

    def _search_default(self, q):
        return self._search(q)

    def _search(self, q):
        """Otsinguvormi päringu koostamine ning 
        otsitingimuste meelde jätmine c sees.
        """
        versioonid_id = sorted(map(int, self.request.params.getall('versioon_id')))
        self.c.versioonid = [v_id and model.Ylesandeversioon.get(v_id) or None\
                             for v_id in versioonid_id]
        return q

    def create(self):
        """Kanname ühe testimiskorra statistika ülesande üldandmetesse"""
        versioon = model.Ylesandeversioon.add(self.c.ylesanne)
        model.Session.commit()
        self.success(_("Jooksvad tekstid on salvestatud versioonina {s}").format(s=versioon.seq))
        return self._redirect('index')        

    def update(self):
        versioon_id = self.request.matchdict.get('id')
        versioon = model.Ylesandeversioon.get(versioon_id)
        if versioon:
            assert versioon.ylesanne_id == self.c.ylesanne.id, _("Vale ülesanne")
            sisuplokk_id = self.request.params.get('sisuplokk_id') or None
            versioon.revert(sisuplokk_id=sisuplokk_id)
            model.Session.commit()
            self.success(_("Andmed on taastatud"))
        return self._redirect('index')
        
    def __before__(self):
        ylesanne_id = self.request.matchdict.get('ylesanne_id')
        self.c.ylesanne = model.Ylesanne.get(ylesanne_id)

    def _perm_params(self):
        return {'obj':self.c.ylesanne}
