# -*- coding: utf-8 -*- 
from eis.lib.baseresource import *
from eis.lib.basegrid import *
_ = i18n._

log = logging.getLogger(__name__)

class OtsisooritajadController(BaseResourceController):
    """Testimiskorrale regatud sooritajate otsimine dialoogiaknas
    """
    _permission = 'korraldamine'
    _MODEL = model.Sooritaja
    _INDEX_TEMPLATE = 'ekk/korraldamine/koht.otsisooritajad.mako'
    _DEFAULT_SORT = 'kasutaja.isikukood' # vaikimisi sortimine
    _no_paginate = True

    def _search(self, q):
        """Otsinguvormi päringu koostamine ning 
        otsitingimuste meelde jätmine c sees.
        """
        if self.c.isikukood:
            usp = validators.IsikukoodP(self.c.isikukood)
            q = q.filter(usp.filter(model.Kasutaja))                                                
        if self.c.piirkond_id:
            f = []
            prk = model.Piirkond.get(self.c.piirkond_id)
            for prk_id in prk.get_alamad_id():
                f.append(model.Koht.piirkond_id==prk_id)
            q = q.filter(sa.or_(*f))
        return q

    def _search_default(self, q):
        return None

    def _query(self):
        return (model.SessionR.query(model.Sooritus, model.Sooritaja, model.Kasutaja)
                .join(model.Sooritus.sooritaja)
                .filter(model.Sooritus.toimumisaeg_id==self.c.toimumisaeg.id)
                .filter(model.Sooritus.testikoht_id==None)
                .join(model.Sooritaja.kasutaja)
                )

    def __before__(self):
        self.c.toimumisaeg = model.Toimumisaeg.get(self.request.matchdict.get('toimumisaeg_id'))
        self.c.testikoht = model.Testikoht.get(self.request.matchdict.get('testikoht_id'))

    def _perm_params(self):
        return {'obj':self.c.testikoht}
