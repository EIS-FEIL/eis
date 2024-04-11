from eis.lib.baseresource import *
_ = i18n._

log = logging.getLogger(__name__)

class AlatestidController(BaseResourceController):
    """Testiülesanded
    """
    _permission = 'ekk-testid'
    _MODEL = model.Alatest
    _EDIT_TEMPLATE = 'ekk/testid/alatest.mako'

    @property
    def _ITEM_FORM(self):
        if self.request.params.get('is_tr'):
            return forms.ekk.testid.AlatestTForm
        else:
            return forms.ekk.testid.AlatestForm

    def _new(self, item):
        item.on_yhekordne = self.c.testiosa.yhesuunaline

    def _create(self, **kw):
        # kui leidub komplektivalik, millel pole veel komplekte, siis paneme uue alatesti sellesse
        testiosa = self.c.testiosa
        oli_alatestideta = not testiosa.on_alatestid
        kursus = self.form.data.get('f_kursus_kood') or None
        item_kv = None
        if self.c.test.diagnoosiv:
            item_kv = testiosa.give_komplektivalik()
        else:
            for kv in testiosa.komplektivalikud:
                if oli_alatestideta or len(kv.komplektid) == 0:
                    kv.kursus_kood = kursus
                    item_kv = kv
                    break
            # kui ei leidunud, siis teeme uue komplektivaliku
            if not item_kv:
                item_kv = model.Komplektivalik(testiosa=testiosa, kursus_kood=kursus)
        testiosa.on_alatestid = True
        kw['komplektivalik'] = item_kv
        kw['vastvorm_kood'] = testiosa.vastvorm_kood
        item = BaseResourceController._create(self, **kw)
        item.max_pallid = 0
        item.ylesannete_arv = 0

        # kui vahetult testiosa all oli varem ylesandeid, siis tõstame need nüüd alatesti alla
        for y in list(testiosa.testiylesanded):
            if y.alatest_id is None:
                y.alatest = item
                y.alatest_seq = item.seq
            item.ylesannete_arv += 1
            item.max_pallid += y.max_pallid or 0
            
        return item

    def _update(self, item, lang=None):
        self._bind_parent(item)
        item.from_form(self.form.data, self._PREFIX, lang=self.c.lang)

        if self.request.params.get('is_tr'):
            # tõlkimine
            return

        if item.yhesuunaline or self.c.testiosa.yhesuunaline:
            item.on_yhekordne = True
            
        if not self.request.params.get('is_tr'):
            oli_piiraeg = item.piiraeg
            item.piiraeg = self.form.data.get('piiraeg')
            if item.piiraeg:
                if self.c.testiosa.piiraeg and item.piiraeg > self.c.testiosa.piiraeg:
                    self.c.dialog_alatest = True
                    errors = {'piiraeg': _("Alatesti piiraeg ei tohi ületada testiosa piiraega")}
                    raise ValidationError(self, errors)

                for ty in item.testiylesanded:
                    if ty.piiraeg and ty.piiraeg > item.piiraeg:
                        self.c.dialog_testiosa = True
                        errors = {'piiraeg': _("Alatestis on ülesanne, mille piiraeg on suurem")}
                        raise ValidationError(self, errors)
                item.hoiatusaeg = (self.form.data.get('hoiatusaeg') or 0) * 60
                if item.hoiatusaeg and item.hoiatusaeg >= item.piiraeg:
                    self.c.dialog_testiosa = True
                    errors = {'hoiatusaeg': _("Hoiatusaeg ei saa olla alatesti piirajast suurem")}
                    raise ValidationError(self, errors)
            else:
                item.hoiatusaeg = None
            if oli_piiraeg and item.piiraeg and oli_piiraeg != item.piiraeg:
                # kui piiraega muudeti, siis teeme pooleli sooritustele märke,
                # et brauseris on vaja taimereid muuta
                model.Sooritus.set_piiraeg_muutus(self.c.testiosa.id)

            # arvutame alatestide jrk nr-id uuesti, juhuks, kui kursust muudeti
            d_seq = dict()
            for alatest in self.c.testiosa.alatestid:
                kursus = alatest.kursus_kood
                alatest.seq = d_seq[kursus] = (d_seq.get(kursus) or 0) + 1

            if item.skoorivalem:
                # testime valemit
                e_locals = {'OIGED': 1}
                value, err0, err, buf1 = model.eval_formula(item.skoorivalem, e_locals, divzero=0)
                if err:
                    raise ValidationError(self, {'f_skoorivalem': err})
                elif not isinstance(value, (int, float)):
                    raise ValidationError(self, {'f_skoorivalem': _("Valemiga arvutamine peab tulemuseks andma arvu")})

            max_pallid = self.form.data.get('max_pallid')
            if item.skoorivalem:
                # alatesti pallid arvutatakse valemiga, ei ole ylesannete pallide summa
                item.max_pallid = max_pallid               
            else:
                # alatesti pallid jagatakse ylesannete vahel
                if max_pallid and item.max_pallid:
                    self._update_pallid(item, max_pallid)
            model.Session.flush()
            # uuendame vajadusel ty tähised
            self.c.testiosa.arvuta_pallid(arvuta_ty=True)
        self.c.test.sum_tahemargid_lang(self.c.lang)
        
    def _update_pallid(self, item, max_pallid):
        # muudame testiülesannete pallid nii, et summa oleks max_pallid
        testiplokid = set()
        hkogumid = set()
        kaalukoefitsient = max_pallid/item.max_pallid
        for ty in item.testiylesanded:
            if ty.max_pallid is None:
                continue
            # kaalume testiylesande pallid
            ty.max_pallid *= kaalukoefitsient
            # muudame valitudylesannete koefitsiendid
            ty.update_koefitsient()

            if ty.testiplokk and ty.testiplokk not in testiplokid:
                testiplokid.add(ty.testiplokk)
            if ty.hindamiskogum not in hkogumid:
                hkogumid.add(ty.hindamiskogum)

        for testiplokk in testiplokid:
            testiplokk.max_pallid = sum([y.max_pallid or 0 for y in testiplokk.testiylesanded if y.max_pallid])

        item.max_pallid = sum([y.max_pallid or 0 for y in item.testiylesanded if y.max_pallid])
        testiosa = item.testiosa
        self.c.test.arvuta_pallid()

        for hkogum in hkogumid:
            hkogum.arvuta_pallid(testiosa.lotv)

    def _after_update(self, id):
        """Mida teha peale õnnestunud salvestamist
        """        
        self.success()
        return HTTPFound(location=self.url('test_struktuur1', 
                                           test_id=self.request.matchdict.get('test_id'),
                                           id=self.request.matchdict.get('testiosa_id'),
                                           lang=self.c.lang))

    def _delete(self, item):
        testiosa = item.testiosa
        item.delete()
        model.Session.flush()
        test = self.c.test
        test.arvuta_pallid()
        test.sum_tahemargid()        
        model.Session.commit()
        self.success(_("Andmed on kustutatud"))

    def _after_delete(self, parent_id=None):
        return HTTPFound(location=self.url('test_struktuur1', 
                                           test_id=self.request.matchdict.get('test_id'),
                                           id=self.request.matchdict.get('testiosa_id'),
                                           lang=self.c.lang))
    
    def __before__(self):
        """Väärtustame self.c.test testiga
        """
        testiosa_id = self.request.matchdict.get('testiosa_id')
        self.c.testiosa = model.Testiosa.get(testiosa_id)
        self.c.test = self.c.testiosa.test
        self.c.lang = self.params_lang()
        super(AlatestidController, self).__before__()

    def _perm_params(self):
        return {'obj':self.c.test}

