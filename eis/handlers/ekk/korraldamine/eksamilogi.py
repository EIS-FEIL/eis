from eis.lib.baseresource import *
_ = i18n._
log = logging.getLogger(__name__)

class EksamilogiController(BaseResourceController):
    _permission = 'korraldamine'
    _MODEL = model.Piirkond
    _INDEX_TEMPLATE = '/ekk/korraldamine/eksamilogi.mako' 
    _no_paginate = True
    _actions = 'index,downloadfile'
    
    def _search_default(self, q):
        return self._search(q)
    
    def _search(self, q1):
        c = self.c
        c.get_sooritused = self._get_sooritused
        c.get_esimees = self._get_esimees
        q = (model.Session.query(model.Piirkond.nimi,
                                 model.Koht.nimi,
                                 model.Testikoht.id,
                                 model.Testiruum.id,
                                 model.Toimumisprotokoll.id,
                                 model.Toimumisprotokoll.lang,
                                 model.Toimumisprotokoll.markus)
             .outerjoin(model.Koht.piirkond)
             .join(model.Koht.testikohad)
             .filter(model.Testikoht.toimumisaeg_id==c.toimumisaeg.id)
             .join(model.Testikoht.toimumisprotokollid)
             .outerjoin(model.Toimumisprotokoll.testiruum)
             .outerjoin(model.Testiruum.ruum)
             .filter(model.Toimumisprotokoll.staatus.in_(
                 (const.B_STAATUS_KINNITATUD, const.B_STAATUS_EKK_KINNITATUD)))
             )
        if not c.kok:
            f = []
            if c.mrk:
                # märkustega soorituskohad
                f.append(sa.or_(sa.and_(model.Toimumisprotokoll.markus!=None,
                                        model.Toimumisprotokoll.markus!=''),
                                model.Testikoht.sooritused.any(
                                    sa.and_(model.Sooritus.markus!=None,
                                            model.Sooritus.markus!=''))))
            if c.ktk:
                # katkestanute või eemaldatutega soorituskohad
                staatused = (const.S_STAATUS_KATKESPROT, const.S_STAATUS_KATKESTATUD, const.S_STAATUS_EEMALDATUD)
                f.append(model.Testikoht.sooritused.any(
                    model.Sooritus.staatus.in_(staatused)))
            if f:
                q = q.filter(sa.or_(*f))

        if c.xls:
            return self._index_xls(q)            
        return q

    def _order(self, q, sort=None):
        return q.order_by(model.Piirkond.nimi,
                          model.Koht.nimi)

    def _prepare_header(self):
        "Loetelu päis"
        return [_("Piirkond"),
                _("Soorituskoht"),
                _("Soorituskoha märkus"),
                _("Eksaminand"),
                _("Isikukood"),
                _("Soorituse olek"),
                _("Põhjendus"),
                _("Soorituse märkus"),
                ]

    def _prepare_items(self, q):
        "Loetelu ridade andmete väljastamine (CSV jaoks)"
        header = self._prepare_header()
        items = []
        prev_prk = None
        for r1 in q.all():
            prk_nimi, k_nimi, testikoht_id, testiruum_id, tpr_id, lang, tpr_markus = r1
            items.append([prk_nimi, k_nimi, tpr_markus])

            for r2 in self._get_sooritused(testikoht_id, testiruum_id, lang):
                eesnimi, perenimi, isikukood, staatus, markus, stpohjus = r2
                item = ['','','',
                        f'{eesnimi} {perenimi}',
                        isikukood,
                        self.c.opt.S_STAATUS.get(staatus),
                        stpohjus,
                        markus]
                items.append(item)

        return header, items
    
    def _get_sooritused(self, testikoht_id, testiruum_id, lang):
        c = self.c
        staatused = (const.S_STAATUS_KATKESPROT, const.S_STAATUS_KATKESTATUD, const.S_STAATUS_EEMALDATUD)

        entities = [model.Sooritaja.eesnimi,
                    model.Sooritaja.perenimi,
                    model.Kasutaja.isikukood,
                    model.Sooritus.staatus,
                    model.Sooritus.markus,
                    model.Sooritus.stpohjus]
        q = (model.Session.query(*entities)
             .filter(model.Sooritus.toimumisaeg_id==c.toimumisaeg.id)
             .filter(sa.or_(model.Sooritus.staatus.in_(staatused),
                            model.Sooritus.markus!=None))
             .join(model.Sooritus.sooritaja)
             .join(model.Sooritaja.kasutaja)
             )
        q = q.filter(model.Sooritus.testikoht_id==testikoht_id)
        if testiruum_id:
            q = q.filter(model.Sooritus.testiruum_id==testiruum_id)
        if lang:
            q = q.filter(model.Sooritaja.lang==lang)
        q = q.order_by(model.Sooritaja.eesnimi,
                       model.Sooritaja.perenimi)
        return q.all()

    def _get_esimees(self, testikoht_id, testiruum_id):
        q = (model.Session.query(model.Kasutaja.nimi)
             .join(model.Labiviija.kasutaja)
             .filter(model.Labiviija.kasutajagrupp_id==const.GRUPP_KOMISJON_ESIMEES)
             .filter(model.Labiviija.testikoht_id==testikoht_id)
             )
        if testiruum_id:
            q = q.filter(model.Labiviija.testiruum_id==testiruum_id)
        nimed = [nimi for nimi, in q.order_by(model.Kasutaja.nimi).all()]
        return ', '.join(nimed)

    def _downloadfile(self, id, file_id, format):
        "Ruumifaili allalaadimine"
        rcd = model.Ruumifail.get(file_id)
        if rcd:
            ta_id = rcd.toimumisprotokoll.testikoht.toimumisaeg_id
            if ta_id == self.c.toimumisaeg.id:
                return utils.download(rcd.filedata, rcd.filename)
        self.error(_("Faili ei leitud"))
        return self._redirect('index')
    
    def __before__(self):
        self.c.toimumisaeg = model.Toimumisaeg.get(self.request.matchdict.get('toimumisaeg_id'))
        self.c.testiosa = self.c.toimumisaeg.testiosa
        self.c.test = self.c.testiosa.test
