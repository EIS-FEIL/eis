# -*- coding: utf-8 -*- 
from eis.lib.baseresource import *
_ = i18n._
from eis.lib.basegrid import BaseGridController

log = logging.getLogger(__name__)

class KlreadController(BaseResourceController):
    """Klassifikaatori ridade AJAXiga uuendamine klassifikaatori haldamise lehel
    """
    _permission = 'klassifikaatorid'
    _MODEL = model.Klrida
    _INDEX_TEMPLATE = '/admin/klread.mako'
    _LIST_TEMPLATE = '/admin/klread.mako'    
    _DEFAULT_SORT = 'klrida.jrk,klrida.id'
    _no_paginate = True
    
    def index(self):
        # HTML tabeli joonistamine, partial
        self.c.is_edit = self.request.params.get('edit')
        return BaseResourceController.index(self)
        
    def _search(self, q):
        """Otsinguvormi päringu koostamine ning 
        otsitingimuste meelde jätmine c sees.
        """
        kood = self.request.params.get('klassifikaator_kood')
        ylem_id = self.request.params.get('ylem_id')
        q = q.filter_by(klassifikaator_kood=kood)
        if kood == 'KEELETASE':
            q = q.filter_by(ylem_id=None)
            if ylem_id:
                q1 = (model.Session.query(model.Klrida.kood)
                      .filter_by(klassifikaator_kood=kood)
                      .filter_by(ylem_id=ylem_id)
                      .filter_by(kehtib=True))
                self.c.seostatud = [r[0] for r in q1.all()]
        elif kood == 'OPITULEMUS':
            q = q.filter(model.Klrida.alam_klseosed.any(
                model.Klseos.ylem_klrida_id==ylem_id))
        elif ylem_id:
            q = q.filter_by(ylem_id=ylem_id)        
            self.c.ylem = model.Klrida.get(ylem_id)
        if kood == 'ERIVAJADUS':
            aste = self.request.params.get('aste') or None
            q = q.filter(model.Klrida.bitimask==aste)
        elif kood == 'HTUNNUS':
            testiklass = self.request.params.get('testiklass')
            q = q.filter(model.Klrida.testiklass_kood==testiklass)
        self.c.item = model.Klassifikaator.get(kood)

        return q
    
