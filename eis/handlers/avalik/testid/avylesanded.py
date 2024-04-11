# testimiskorrata läbi viidud testi tulemused
from simplejson import dumps
from eis.lib.baseresource import *
from eis.lib.blockview import BlockView
from eis.lib.resultstat import ResultStat

log = logging.getLogger(__name__)
_ = i18n._

class AvylesandedController(BaseResourceController):

    _permission = 'omanimekirjad'
    _INDEX_TEMPLATE = 'avalik/testid/avtulemused.ylesanded.mako'
    _EDIT_TEMPLATE = 'avalik/testid/avtulemused.ylesanded.mako' 
    _no_paginate = True
    _get_is_readonly = False
    _actions = 'index,show,edit' # võimalikud tegevused

    def _query(self):
        pass

    def _search_default(self, q):
        return self._search(q)

    def _search(self, q):
        c = self.c
        c.testiylesanded = [ty for ty in c.testiosa.testiylesanded if ty.liik == const.TY_LIIK_Y]
        c.cnt_testiylesanded = len(c.testiylesanded)
        if c.testiruum:
            q1 = self._query_sooritused()
            c.res = self._query_res()
            if c.csv:
                return self._index_csv(q1)
            c.sooritused = q1.all()

        c.header = self._prepare_header()
        c.prepare_item = self._prepare_item
            
    def _filter(self, q):
        q = q.filter(model.Sooritus.testiruum_id==self.c.testiruum.id)
        return q

  
    def _query_sooritused(self):
        # päritakse sooritajate nimekiri
        q = model.SessionR.query(model.Sooritus, 
                                model.Sooritaja.eesnimi,
                                model.Sooritaja.perenimi,
                                model.Kasutaja.isikukood)

        q = self._filter(q)
        q = (q.join(model.Sooritus.sooritaja)
             .join(model.Sooritaja.kasutaja)
             .order_by(model.sa.desc(model.Sooritus.staatus),
                       model.Sooritaja.eesnimi,
                       model.Sooritaja.perenimi)
             )
        return q

    def _query_res(self):
        # päritakse tulemuste tabel
        q = model.SessionR.query(model.Sooritus.id,
                                model.Testiylesanne.alatest_seq,
                                model.Testiylesanne.seq,
                                model.Ylesandevastus.valitudylesanne_id,
                                model.Ylesandevastus.pallid)
        q = self._filter(q)
        q = (q.filter(model.Sooritus.staatus==const.S_STAATUS_TEHTUD)
             .join((model.Ylesandevastus,
                    model.Ylesandevastus.sooritus_id==model.Sooritus.id))
             .filter(model.Ylesandevastus.kehtiv==True)
             .join((model.Testiylesanne,
                    model.Testiylesanne.id==model.Ylesandevastus.testiylesanne_id)))
        
        res = {}
        for rcd in q.all():
            sooritus_id, a_seq, ty_seq, vy_id, y_pallid = rcd
            if sooritus_id not in res:
                res[sooritus_id] = {}
            res[sooritus_id][a_seq, ty_seq] = y_pallid
        return res

    def _index_csv(self, q, fn='andmed.csv'):
        "Loetelu väljastamine CSV-na"
        header, items = self._prepare_items(q)
        data = self._csv_data(header, items)
        data = utils.encode_ansi(data)
        return utils.download(data, fn, const.CONTENT_TYPE_CSV)
    
    def _prepare_header(self):
        c = self.c
        if c.csv:
            header = [(None, _("Õpilane")),
                      (None, _("Isikukood")),
                      (None, _("Olek")),
                    ]
        else:
            header = [(None, _("Õpilane")),
                      (None, _("Olek")),
                    ]
        for ind, ty in enumerate(c.testiylesanded):
            txt = '%s' % (ty.tahis or '')
            if ty.max_pallid is not None:
                if c.res_prot and ty.id in c.res_prot:
                    txt += ' (max 100%)'
                else:
                    txt += ' (max %sp)' % (self.h.fstr(ty.max_pallid))
            header.append((ind+1, txt))
        header.append((None, _("Kokku")))
        return header
    
    def _prepare_item(self, row, n, is_html=False):
        c = self.c
        tos, eesnimi, perenimi, ik = row
        res = c.res.get(tos.id)
        nimi = '%s %s' % (eesnimi, perenimi)
        if c.test.on_jagatudtoo:
            tehtud = len(res or {})
            if tos.staatus >= const.S_STAATUS_POOLELI:
                olek = f'{tehtud} / {len(c.testiylesanded)}'
            else:
                olek = tos.staatus_nimi
        else:
            olek = tos.staatus_nimi

        if c.csv:
            item = [nimi, ik, olek]
        else:
            item = [nimi,  olek]
        html_extra = {}
        
        for ind_ty, ty in enumerate(c.testiylesanded):
            value = res and self.h.fstr(res.get((ty.alatest_seq, ty.seq)),1) or ''
            if c.res_prot and ty.id in c.res_prot and value:
                value = f'{value}%'
            if is_html:
                if value and c.res_ts and ty.id in c.res_ts:
                    lnk_ty_id = ty.id
                else:
                    lnk_ty_id = None
                ind_c = len(item)
                html_extra[ind_c] = (ind_ty+1, lnk_ty_id)
            item.append(value)

        # kogutulemus
        if c.test.on_jagatudtoo:
            ## tulemus kuvada ka siis, kui kogu töö on veel hindamata
            value = tos.get_tulemus_pro(with_pr=False)
        else:
            value = tos.get_tulemus(with_pr=False)
        item.append(value)

        if is_html:
            return item, html_extra
        else:
            return item
        
    def _edit(self, item):
        self._index_d()
        if item.ylesanne:
            self.c.testiosa = item.testiylesanne.testiosa
            self.c.item_html = BlockView(self, item.ylesanne, self.c.lang).assessment_analysis()

    def _get_testiruum(self, test_id, testiosa_id):
        c = self.c
        testiruum_id = int(self.request.matchdict.get('testiruum_id'))
        testiruum = nimekiri_id = None
        if testiruum_id:
            # testiruum on antud
            testiruum = model.Testiruum.get(testiruum_id)
            if testiruum:
                nimekiri_id = testiruum.nimekiri_id
                if testiosa_id:
                    # testiosa on ka antud - kui see ei vasta testiruumile, siis see ei sobi
                    testikoht = testiruum.testikoht
                    if testikoht.testiosa_id != testiosa_id:
                        testiruum = None
        if not testiruum:
            # leiame viimasena loodud nimekirja
            q = (model.Testiruum.query
                 .join(model.Testiruum.nimekiri)
                 .filter(model.Nimekiri.test_id==test_id)
                 .filter(model.Nimekiri.testimiskord_id==None)
                 .filter(model.Nimekiri.esitaja_kasutaja_id==c.user.id)
                 )
            if nimekiri_id:
                q = q.filter(model.Testiruum.nimekiri_id==nimekiri_id)
            if c.user.koht_id:
                q = q.filter(model.Nimekiri.esitaja_koht_id==c.user.koht_id)
            if testiosa_id:
                q = (q.join(model.Testiruum.testikoht)
                     .filter(model.Testikoht.testiosa_id==testiosa_id))
            q = q.order_by(model.sa.desc(model.Testiruum.id))
            testiruum = q.first()
        return testiruum

    def __before__(self):
        c = self.c
        c.test_id = self.request.matchdict.get('test_id')
        c.test = model.Test.get(c.test_id)

        c.testiosa_id = self.request.params.get('testiosa_id')
        if c.testiosa_id:
            c.testiosa = model.Testiosa.get(c.testiosa_id)
            if c.testiosa.test_id != c.test.id:
                c.testiosa = c.testiosa_id = None

        c.testiruum = self._get_testiruum(c.test_id, c.testiosa_id)
        if c.testiruum:
            c.testiruum_id = c.testiruum.id
            c.nimekiri = c.testiruum.nimekiri
            c.testiosa = c.testiruum.testikoht.testiosa
        else:
            c.testiruum_id = 0
            if not c.testiosa:
                c.testiosa = c.test.testiosad[0]
            
    def _perm_params(self):
        c = self.c
        return {'obj': c.nimekiri}
