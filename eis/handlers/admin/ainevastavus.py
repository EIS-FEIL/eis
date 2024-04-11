# -*- coding: utf-8 -*- 

from eis.lib.baseresource import *
_ = i18n._
from eis.lib.basegrid import BaseGridController
import eis.lib.raw_export as raw_export

log = logging.getLogger(__name__)

class AinevastavusController(BaseResourceController):
    "EISi ja oppekava.edu.ee klassifikaatorite vastavus"
    
    _permission = 'klassifikaatorid'
    _ITEM = 'klassifikaator'
    _ITEMS = 'klassifikaatorid'
    _MODEL = model.Klassifikaator
    _ITEM_FORM = forms.admin.KlvastavusedForm
    _EDIT_TEMPLATE = 'admin/ainevastavus.mako'
    _DEFAULT_SORT = 'nimi'
    _no_paginate = True
    
    _APP = const.APP_EIS

    def _edit(self, item):
        c = self.c
        c.items = [r for r in c.item.read]

    def _update(self, item):
        c = self.c
        c.item = item
        if c.kl2 not in ('OPIAINE','EHIS_AINE'):
            self.error(_("Vigane URL"))
            return
        
        for klv in self.form.data['klv']:
            klrida_id = klv['id']
            # EISi klassifikaatori rida
            rcd = model.Klrida.get(klrida_id)
            # teise klassifikaatori vasted
            vasted_id = klv.get('vaste_id')
            vastavused = [r for r in rcd.eis_klvastavused if r.ehis_kl==c.kl2]
            for r in vastavused:
                if r.ehis_klrida_id in vasted_id:
                    vasted_id.remove(r.ehis_klrida_id)
                else:
                    r.delete()
            for vaste_id in vasted_id:
                v = model.Klvastavus(eis_klrida_id=rcd.id,
                                     ehis_klrida_id=vaste_id,
                                     ehis_kl=c.kl2)

        model.Session.commit()
        
        # kustutame selle klassifikaatori väärtused mälupuhvrist,
        # kuna need on muutunud ja tuleks uuesti andmebaasist pärida
        model.Klrida.clean_cache(item.kood)

    def __before__(self):
        self.c.kl2 = self.request.matchdict.get('kl2')
        super().__before__()
