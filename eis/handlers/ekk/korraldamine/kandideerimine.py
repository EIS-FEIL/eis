# Sisseastumistesti sooritajad koolidega, millesse kandideerivad ES-3238

from eis.lib.baseresource import *
_ = i18n._
log = logging.getLogger(__name__)

class KandideerimineController(BaseResourceController):
    _permission = 'korraldamine'
    _MODEL = model.Testikoht
    _INDEX_TEMPLATE = '/ekk/korraldamine/kandideerimine.mako' 
    _LIST_TEMPLATE = '/ekk/korraldamine/kandideerimine_list.mako'
    _DEFAULT_SORT = 'sooritaja.perenimi,sooritaja.eesnimi'
    _ignore_default_params = ['pdf','csv']
    _no_paginate = True
    _UNIQUE_SORT = 'sooritaja.id'
    
    def _query(self):
        q = model.Session.query(model.Sooritaja,
                                model.Kasutaja.isikukood,
                                model.Kasutaja.synnikpv)
        q = (q.join(model.Kasutaja.sooritajad)
             .filter(model.Sooritaja.testimiskord_id==self.c.toimumisaeg.testimiskord_id)
             )
        return q

    def _search_default(self, q):
        return self._search(q)

    def _search(self, q):
        c = self.c
        if c.koht_id:
            q = q.filter(model.Sooritaja.kandideerimiskohad.any(
                model.Kandideerimiskoht.koht_id==c.koht_id))
        if self.c.csv:
            return self._index_csv(q)
        self.c.prepare_header = self._prepare_header
        self.c.prepare_item = self._prepare_item
        self.c.opt_vvkohad = self._get_vvkohad()
        return q

    def _get_vvkohad(self):
        q = (model.Session.query(model.Koht.id, model.Koht.nimi)
             .join(model.Testimiskord.regkohad)
             .filter(model.Testimiskord.id==self.c.toimumisaeg.testimiskord_id)
             .order_by(model.Koht.nimi))
        li = [(k_id, k_nimi) for (k_id, k_nimi) in q.all()]
        return li
    
    def _prepare_header(self):
        "Loetelu päis"
        return (('kasutaja.isikukood', _("Isikukood")),
                ('sooritaja.eesnimi', _("Eesnimi")),
                ('sooritaja.perenimi', _("Perekonnanimi")),
                ('koht.nimi', _("Tulemuste vaatamise õigusega kool")),
                ('sooritaja.staatus', _("Olek")),
                ('sooritaja.pallid', _("Tulemus")),
                )

    def _prepare_item(self, rcd, n=None):
        "Loetelu rida"
        sooritaja, k_ik, k_synnikpv = rcd

        # leiame tulemuste vaatamise õigusega koolid
        q = (model.Session.query(model.Koht.nimi,
                                 model.Kandideerimiskoht.automaatne)
             .join(model.Kandideerimiskoht.koht)
             .filter(model.Kandideerimiskoht.sooritaja_id==sooritaja.id)
             .order_by(model.Koht.nimi))
        li = []
        for k_nimi, automaatne in q.all():
            if automaatne:
                k_nimi += ' (%s)' % _("automaatselt")
            li.append(k_nimi)
        vvkohad = ', '.join(li)
        
        return [k_ik or self.h.str_from_date(k_synnikpv),
                sooritaja.eesnimi,
                sooritaja.perenimi,
                vvkohad,
                sooritaja.staatus_nimi,
                sooritaja.get_tulemus(),
                ]
    
    def __before__(self):
        self.c.toimumisaeg = model.Toimumisaeg.get(self.request.matchdict.get('toimumisaeg_id'))
        self.c.testiosa = self.c.toimumisaeg.testiosa
        self.c.test = self.c.testiosa.test
