# -*- coding: utf-8 -*- 

from eis.lib.baseresource import *
_ = i18n._

log = logging.getLogger(__name__)

class LisatestiController(BaseResourceController):
    """Ülesande lisamine testi"""

    _permission = 'ylesanded'
    _MODEL = model.Ylesanne
    _INDEX_TEMPLATE = 'ekk/ylesanded/lisatesti.valitest.mako'

    def _index(self):
        return self.response_dict

    def _index_valitest(self):
        "Kasutaja on sisestanud testi ID"
        err = None
        try:
            self.c.test_id = int(self.request.params.get('test_id'))
        except:
            err = _("Sisestatud testi ID on vale")
        else:
            self.c.test = model.Test.get(self.c.test_id)
            if not self.c.test:
                err = _("Testi ei leitud")
            elif not self.c.user.has_permission('ekk-testid', const.BT_UPDATE, obj=self.c.test):
                err = _("Puudub testi andmete muutmise õigus")
            else:
                mitu_testiosa = len(self.c.test.testiosad) > 1
                q = (model.Session.query(model.Komplekt.id,
                                         model.Komplekt.tahis,
                                         model.Testiosa.nimi)
                     .filter(model.Komplekt.staatus==const.K_STAATUS_KOOSTAMISEL)
                     .filter(model.Komplekt.lukus==None)
                     .join(model.Komplekt.komplektivalik)
                     .join(model.Komplektivalik.testiosa)
                     .filter(model.Testiosa.test_id==self.c.test.id)
                     .order_by(model.Testiosa.seq, model.Komplekt.tahis)
                     )
                li = []
                for k_id, k_tahis, osa_nimi in q.all():
                    if mitu_testiosa:
                        label = '%s (%s)' % (k_tahis, osa_nimi)
                    else:
                        label = k_tahis
                    li.append((k_id, label))
                if not li:
                    err = _("Testis ei ole ühtki koostamisel olevat ülesandekomplekti")
                elif len(li) > 1:
                    # kasutaja peab komplekti valima
                    self.c.opt_komplekt = li
                    return self.render_to_response('ekk/ylesanded/lisatesti.valikomplekt.mako')
                else:
                    # ainult 1 komplekt
                    komplekt_id = li[0][0]
                    self.c.komplekt = model.Komplekt.get(komplekt_id)
                    return self._show_komplekt(self.c.komplekt)

        self.error(err)
        return self.render_to_response('ekk/ylesanded/lisatesti.valitest.mako')

    def _index_valikomplekt(self):
        "Kasutaja on valinud komplekti"
        test_id = self.request.params.get('test_id')
        komplekt_id = self.request.params.get('komplekt_id')
        err = None
        self.c.test = model.Test.get(test_id)
        if not self.c.test:
            err = _("Testi ei leitud")
        elif not self.c.user.has_permission('ekk-testid', const.BT_UPDATE, obj=self.c.test):
            err = _("Puudub testi andmete muutmise õigus")
        else:
            self.c.komplekt = model.Komplekt.get(komplekt_id)
            if not self.c.komplekt:
                err = _("Komplekti ei leitud")
            else:
                return self._show_komplekt(self.c.komplekt)

        self.error(err)
        return self.render_to_response('ekk/ylesanded/lisatesti.valikomplekt.mako')

    def _show_komplekt(self, komplekt):
        kvalik = komplekt.komplektivalik
        testiosa = kvalik.testiosa
        assert testiosa.test_id == self.c.test.id, 'Vale test'
        # leiame komplekti ylesanded
        li = []
        alatestid = list(kvalik.alatestid)
        for alatest in alatestid:
            li.append((alatest.nimi, alatest.testiylesanded))
        if not alatestid and not len(testiosa.alatestid):
            li.append((None, testiosa.testiylesanded))
        self.c.items = li
        return self.render_to_response('ekk/ylesanded/lisatesti.valiylesanne.mako')

    def _create_valiylesanne(self):
        err = None
        params = self.request.params
        test_id = params.get('test_id')
        komplekt_id = params.get('komplekt_id')
        self.c.test = model.Test.get(test_id)
        self.c.komplekt = model.Komplekt.get(komplekt_id)
        if not self.c.test:
            err = _("Testi ei leitud")
        elif not self.c.user.has_permission('ekk-testid', const.BT_UPDATE, obj=self.c.test):
            err = _("Puudub testi andmete muutmise õigus")
        else:
            ty_id = params.get('ty_id')
            try:
                # valikylesande korral
                ty_id, seq = ty_id.split('#')
            except:
                seq = 1
            try:
                ty_id = int(ty_id)
                seq = int(seq)
            except:
                err = _("Palun vali koht testis, kuhu ülesanne lisada")

        if not err:
            if not self.c.komplekt:
                err = _("Komplekt puudub")
            elif self.c.komplekt.staatus != const.K_STAATUS_KOOSTAMISEL:
                err = _("Komplekti olek on {s}").format(s=self.c.komplekt.staatus_nimi)
            elif self.c.komplekt.lukus:
                err = _("Komplekt on lukus")
            else:
                # kas ylesanne juba on komplektis?
                vy2 = (model.Valitudylesanne.query
                       .filter_by(komplekt_id=self.c.komplekt.id)
                       .filter_by(ylesanne_id=self.c.item.id)
                       .first())
                if vy2 and not (vy2.testiylesanne_id == ty_id and vy2.seq == seq):
                    vy2.ylesanne_id = None
                ty = model.Testiylesanne.get(ty_id)
                testiosa = ty.testiosa
                assert testiosa.test_id == self.c.test.id, 'Vale test'
                vy = ty.give_valitudylesanne(self.c.komplekt, seq)
                if self.c.item.max_pallid is None:
                    self.c.item.max_pallid = self.c.item.get_max_pallid()
                vy.ylesanne_id = self.c.item.id
                if ty.max_pallid is None:
                    if not testiosa.lotv:
                        ty.max_pallid = self.c.item.max_pallid or 0
                    self.c.test.arvuta_pallid()
                vy.update_koefitsient(ty)
                model.Session.commit()
                self.c.lisatud_ty = ty
                self.notice(_("Ülesanne lisatud!"))
                return self.render_to_response('ekk/ylesanded/lisatesti.valiylesanne.mako')
        if err:
            self.error(err)
        return self._show_komplekt(self.c.komplekt)
            
    def __before__(self):
        self.c.item = model.Ylesanne.get(self.request.matchdict.get('ylesanne_id'))

    def _perm_params(self):
        return {'obj':self.c.item}


