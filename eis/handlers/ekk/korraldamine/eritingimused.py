# Sooritajad, kellel on varem olnud eritingimusi (ES-1151)

from eis.lib.baseresource import *
_ = i18n._
log = logging.getLogger(__name__)

class EritingimusedController(BaseResourceController):
    _permission = 'korraldamine'
    _MODEL = model.Testikoht
    _INDEX_TEMPLATE = '/ekk/korraldamine/eritingimused.mako' 
    _LIST_TEMPLATE = '/ekk/korraldamine/eritingimused_list.mako'
    _DEFAULT_SORT = 'piirkond.nimi,koht.nimi,sooritaja.perenimi,sooritaja.eesnimi'
    _ignore_default_params = ['pdf']
    _no_paginate = True
    _UNIQUE_SORT = 'sooritaja.id'
    
    def _query(self):
        q = model.SessionR.query(model.Sooritaja.id,
                                model.Kasutaja.isikukood,
                                model.Kasutaja.synnikpv,
                                model.Sooritaja.eesnimi,
                                model.Sooritaja.perenimi,
                                model.Sooritus.tahised,
                                model.Koht.nimi,
                                model.Ruum.tahis,
                                model.Piirkond.nimi)
        q = (q.join(model.Kasutaja.sooritajad)
             .filter(model.Sooritaja.testimiskord_id==self.c.toimumisaeg.testimiskord_id)
             .filter(model.Sooritaja.staatus>const.S_STAATUS_REGAMATA)
             .join(model.Sooritaja.sooritused)
             .filter(model.Sooritus.toimumisaeg_id==self.c.toimumisaeg.id)
             .outerjoin(model.Sooritus.testikoht)
             .outerjoin(model.Testikoht.koht)
             .outerjoin(model.Sooritus.testiruum)
             .outerjoin(model.Testiruum.ruum)
             .outerjoin((model.Piirkond,
                         sa.or_(model.Piirkond.id==model.Koht.piirkond_id,
                                sa.and_(model.Piirkond.id==model.Sooritaja.piirkond_id,
                                        model.Sooritus.testikoht_id==None))
                         ))
             )

        # kasutajal on lisatingimused või on mõnel testil olnud eritingimusi
        Sooritaja2 = sa.orm.aliased(model.Sooritaja)
        Sooritus2 = sa.orm.aliased(model.Sooritus)
        q = q.filter(sa.or_(sa.and_(model.Kasutaja.lisatingimused!='',
                                    model.Kasutaja.lisatingimused!=None),
                            sa.exists().where(sa.and_(
                                model.Kasutaja.id==Sooritaja2.kasutaja_id,
                                Sooritaja2.id==Sooritus2.sooritaja_id,
                                Sooritus2.on_erivajadused==True))
                            ))

        # leiame kasutajale lubatud piirkondade loetelu
        piirkonnad_id = self.c.user.get_kasutaja().get_piirkonnad_id('erivajadused', const.BT_SHOW)
        # kas pole õigust kõigi piirkondade korraldamiseks?
        if None not in piirkonnad_id:
            # piirkondlik korraldaja ei või kõiki piirkondi vaadata, 
            q = q.filter(model.Piirkond.id.in_(piirkonnad_id))

        return q

    def _search_default(self, q):
        return self._search(q)

    def _search(self, q):
        c = self.c
        c.header = self._prepare_header()
        c.prepare_item = self._prepare_item
        return q

    def _prepare_header(self):
        # tabeli päis
        header = [('kasutaja.isikukood,kasutaja.synnikpv', _("Isikukood või sünniaeg")),
                  ('kasutaja.eesnimi', _("Eesnimi")),
                  ('kasutaja.perenimi', _("Perekonnanimi")),
                  ('sooritus.tahised', _("Soorituse tähis")),
                  ('koht.nimi', _("Soorituskoht")),
                  ('ruum.tahis', _("Ruum")),
                  ('piirkond.nimi', _("Piirkond")),
                  ]
        return header

    def _prepare_item(self, rcd, n=None):
        "Tabeli ühe rea väljade kokkupanek"
        c = self.c
        h = self.h
        j_id, isikukood, skpv, eesnimi, perenimi, tahised, k_nimi, r_tahis, prk_nimi = rcd
        row = [isikukood or h.str_from_date(skpv),
               eesnimi,
               perenimi,
               tahised,
               k_nimi,
               r_tahis,
               prk_nimi,
               ]
        return row
    
    def __before__(self):
        self.c.toimumisaeg = model.Toimumisaeg.get(self.request.matchdict.get('toimumisaeg_id'))
        self.c.testiosa = self.c.toimumisaeg.testiosa
        self.c.test = self.c.testiosa.test
