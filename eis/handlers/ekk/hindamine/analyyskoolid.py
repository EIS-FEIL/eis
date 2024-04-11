from eis.lib.baseresource import *
_ = i18n._
from eis.lib.block import BlockController
from eis.lib.resultstat import ResultStat

log = logging.getLogger(__name__)

class AnalyyskoolidController(BaseResourceController):
    _permission = 'hindamisanalyys'

    _MODEL = model.Valitudylesanne
    _INDEX_TEMPLATE = 'ekk/hindamine/analyys.koolid.mako'
    _EDIT_TEMPLATE = 'ekk/hindamine/analyys.koolid.mako' 
    _DEFAULT_SORT = 'testiylesanne.alatest_seq,testiylesanne.seq,valitudylesanne.komplekt_id,valitudylesanne.seq' # vaikimisi sortimine
    _SEARCH_FORM = forms.ekk.hindamine.AnalyyskoolidForm
    _no_paginate = True
    _get_is_readonly = False
    
    def _search_default(self, q):
        return self._search(q)

    def _search(self, q1):
        self.c.koolid_id = self._get_koolid_opt()
        self.c.testikoht_id = self.c.testikoht_id or None
        self.c.kool_koht_id = self.c.kool_koht_id or None
        if not self.c.testikoht_id and not self.c.kool_koht_id and not (self.c.otsi or self.c.csv):
            return
        if self.c.test.on_kursused and not self.c.kursus:
            return
        self._query_sooritused()
        q = self._query_ylesanded()
        if self.c.csv:
            return self._index_csv(q)
        self.c.header = self._prepare_header()
        self.c.prepare_item = self._prepare_item
        return q

    def _get_koolid_opt(self):
        q = (model.SessionR.query(model.Koht.id, model.Koht.nimi)
             .distinct()
             .join(model.Koht.sooritajad)
             .filter(model.Sooritaja.testimiskord_id==self.c.toimumisaeg.testimiskord_id)
             .order_by(model.Koht.nimi)
             )
        li = q.all()
        return li

    def _query_sooritused(self):
        # päritakse sooritajate nimekiri
        q = model.SessionR.query(model.Sooritus, 
                                model.Sooritaja.eesnimi,
                                model.Sooritaja.perenimi,
                                model.Koolinimi.nimi, # õppimiskoht
                                model.Koht.nimi # soorituskoht
                                )

        q = (q.join(model.Sooritus.sooritaja)
             .outerjoin(model.Sooritaja.koolinimi)
             .join(model.Sooritus.testikoht)
             .join(model.Testikoht.koht)
             )
        q = self._filter(q)
        q = q.order_by(model.Sooritus.testikoht_id,
                       model.Sooritaja.perenimi,
                       model.Sooritaja.eesnimi)

        self.c.sooritused = q.all()

        # päritakse tulemuste tabel
        q = model.SessionR.query(model.Sooritus.id,
                                model.Testiylesanne.alatest_seq,
                                model.Testiylesanne.seq,
                                model.Ylesandevastus.valitudylesanne_id,
                                model.Ylesandevastus.pallid)
        q = q.join(model.Sooritus.sooritaja)
        q = (q.join((model.Ylesandevastus,
                     model.Ylesandevastus.sooritus_id==model.Sooritus.id))
             .join((model.Testiylesanne,
                    model.Testiylesanne.id==model.Ylesandevastus.testiylesanne_id)))
        q = self._filter(q)
        
        res = {}
        for rcd in q.all():
            sooritus_id, alatest_seq, ty_seq, vy_id, y_pallid = rcd
            if sooritus_id not in res:
                res[sooritus_id] = {}
            seq = '%s.%s' % (alatest_seq or '', ty_seq)
            res[sooritus_id][seq] = y_pallid

        self.c.res = res

    def _query_ylesanded(self):
        # koostatakse ylesannete statistika
        c = self.c
        if c.testikoht_id or c.kool_koht_id:
            resultstat = ResultStat(self, None, True)
            resultstat.calc_testikoht_y(c.toimumisaeg_id, c.testikoht_id, c.kool_koht_id)
            model.Session.commit()
        model.Session.execute('SET TRANSACTION READ ONLY')
            
        # päritakse ylesannete statistika
        q = model.SessionR.query(model.Ylesanne, 
                                model.Valitudylesanne,
                                model.Testiylesanne,
                                model.Ylesandestatistika)
        q = (q.join(model.Testiylesanne.valitudylesanded)
             .join(model.Valitudylesanne.ylesanne)
             .join(model.Testiylesanne.testiosa)
             .filter(model.Testiosa.test_id==c.test.id)
             .filter(model.Testiylesanne.liik==const.TY_LIIK_Y))
        if c.toimumisaeg:
            komplektid_id = [k.id for k in c.toimumisaeg.komplektid]
            q = q.filter(model.Valitudylesanne.komplekt_id.in_(komplektid_id))

        if c.kursus:
            q = q.join(model.Testiylesanne.alatest).\
                filter(model.Alatest.kursus_kood==c.kursus)
            
        if c.testikoht_id:
            f = model.Ylesandestatistika.testikoht_id == c.testikoht_id
        elif c.kool_koht_id:
            f = model.Ylesandestatistika.kool_koht_id == c.kool_koht_id
        else:
            f = sa.and_(model.Ylesandestatistika.kool_koht_id == None,
                        model.Ylesandestatistika.testikoht_id == None)
            if c.toimumisaeg:
                f = sa.and_(f, model.Ylesandestatistika.toimumisaeg_id == c.toimumisaeg.id)
        q = q.outerjoin((model.Ylesandestatistika,
                         sa.and_(model.Ylesandestatistika.valitudylesanne_id==model.Valitudylesanne.id,
                                 f)))
        return q

    def _filter(self, q):
        q = q.filter(model.Sooritus.staatus==const.S_STAATUS_TEHTUD)
        if self.c.testikoht_id:
            q = q.filter(model.Sooritus.testikoht_id==self.c.testikoht_id)
        elif self.c.kool_koht_id:
            q = q.filter(model.Sooritus.toimumisaeg_id==self.c.toimumisaeg_id).\
                filter(model.Sooritaja.kool_koht_id==self.c.kool_koht_id)
        else:
            q = q.filter(model.Sooritus.toimumisaeg_id==self.c.toimumisaeg_id)            
        if self.c.kursus:
            q = q.filter(model.Sooritaja.kursus_kood==self.c.kursus)
        if self.c.pallitud:
            Testiylesanne2 = sa.orm.aliased(model.Testiylesanne)
            Ylesandevastus2 = sa.orm.aliased(model.Ylesandevastus)
            q = q.filter(sa.exists().where(sa.and_(
                Testiylesanne2.testiosa_id==self.c.testiosa.id,
                Testiylesanne2.liik==const.TY_LIIK_Y,
                ~ sa.exists(
                    sa.select([Ylesandevastus2.id])
                    .where(sa.and_(Ylesandevastus2.sooritus_id==model.Sooritus.id,
                                   Ylesandevastus2.testiylesanne_id==Testiylesanne2.id,
                                   Ylesandevastus2.pallid!=None))
                    .correlate(model.Sooritus)
                    .correlate(Testiylesanne2)
                    )
                )))
        #model.log_query(q)
                                           
        return q

    def _prepare_header(self):
        "Loetelu päis"
        c = self.c
        header = [(None, _("Sooritaja")),
                  ]
        if c.csv:
            header.extend([
                  (None, _("Soorituskoht")),
                  (None, _("Õppimiskoht")),
                  ])
        self.testiylesanded = [ty for ty in c.testiosa.testiylesanded \
                               if not c.kursus or c.kursus == ty.hindamiskogum.kursus_kood]
        for ty in self.testiylesanded:
            header.append((None, ty.tahis or ''))
        header.append((None, _("Kokku")))
        header.append((None, _("Ajakulu")))
        return header

    def _prepare_items(self, q):
        "Loetelu ridade andmete väljastamine (CSV jaoks)"
        c = self.c
        header = self._prepare_header()
        items = []
        for n, rcd in enumerate(c.sooritused):
            item = self._prepare_item(rcd, n)
            items.append(item)
        return header, items

    def _prepare_item(self, rcd, n=None):
        "Loetelu rida"
        c = self.c
        h = self.h
        tos, eesnimi, perenimi, oppekoht_nimi, testikoht_nimi = rcd
        res = c.res.get(tos.id)
        item = ['%s %s %s' % (tos.tahised or '', eesnimi, perenimi)]
        if c.csv:
            item.extend([
                testikoht_nimi,
                oppekoht_nimi,
                ])
        for ty in self.testiylesanded:
            value = res and h.fstr(res.get('%s.%s' % (ty.alatest_seq or '', ty.seq))) or ''
            item.append(value)
        item.append(tos.get_tulemus())
        item.append(h.str_from_time(tos.ajakulu))
        return item
    
    def __before__(self):
        self.c.toimumisaeg_id = self.request.matchdict.get('toimumisaeg_id')
        self.c.toimumisaeg = model.Toimumisaeg.get(self.c.toimumisaeg_id)
        self.c.testiosa = self.c.toimumisaeg.testiosa
        self.c.test = self.c.testiosa.test

    def _perm_params(self):
        return {'obj':self.c.test}
