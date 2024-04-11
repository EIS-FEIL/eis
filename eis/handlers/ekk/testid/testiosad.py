from eis.lib.baseresource import *
_ = i18n._

log = logging.getLogger(__name__)

class TestiosadController(BaseResourceController):
    """Testiosad
    """
    _permission = 'ekk-testid'
    _MODEL = model.Testiosa
    _EDIT_TEMPLATE = 'ekk/testid/testiosa.mako'
    #_SHOW_TEMPLATE = 'ekk/testid/testiosa.show.mako'
    _INDEX_TEMPLATE = 'ekk/testid/struktuur.mako'
    _ITEM_FORM = forms.ekk.testid.TestiosaForm 
    _index_after_create = True
    _ignore_default_params = ['lang']
    
    def _new(self, item):
        liseq = [o.seq for o in self.c.test.testiosad]
        item.seq = not liseq and 1 or max(liseq) + 1
        item.naita_max_p = True
        item.yhesuunaline = self.c.test.testiliik_kood == const.TESTILIIK_KOOLIPSYH
        item.yl_lahendada_lopuni = self.c.test.testiliik_kood == const.TESTILIIK_KOOLIPSYH
        item.gen_tahis()

    def update(self):
        id = self.request.matchdict.get('id')
        if self.request.params.get('is_tr'):
            self._ITEM_FORM = forms.ekk.testid.TestiosaTForm
        else:
            self._ITEM_FORM = forms.ekk.testid.TestiosaForm

        return BaseResourceController.update(self)
        
    def _update(self, item):
        oli_lotv = item.lotv
        oli_yhesuunaline = item.yhesuunaline
        oli_skoorivalem = item.skoorivalem
        oli_vastvorm = item.vastvorm_kood
        oli_seq = item.seq
        vana_tahis = item.tahis

        BaseResourceController._update(self, item, lang=self.c.lang)
        
        self._update_lotv(item, oli_lotv)
        if item.id and oli_vastvorm != item.vastvorm_kood:
            # kui vastamise vorm muutus, siis muudame sisestusviisi
            if item.vastvorm_kood in (const.VASTVORM_SP, const.VASTVORM_SH):
                # suulisel testiosal saab olla ainult punktide sisestamine
                q = (model.Session.query(model.Testiylesanne)
                     .filter(model.Testiylesanne.testiosa_id==item.id)
                     .filter(model.Testiylesanne.sisestusviis!=const.SISESTUSVIIS_PALLID))
                for ty in q.all():
                    ty.sisestusviis = const.SISESTUSVIIS_PALLID
            else:
                # kirjalikul testiosal on vaikimisi vastuse sisestamine, sisestusolekus saab seda muuta
                q = (model.Session.query(model.Testiylesanne)
                     .filter(model.Testiylesanne.testiosa_id==item.id)
                     .filter(model.Testiylesanne.sisestusviis!=const.SISESTUSVIIS_VASTUS))
                for ty in q.all():
                    ty.sisestusviis = const.SISESTUSVIIS_VASTUS
                
        self.c.test.from_form(self.form.data, 't_', lang=self.c.lang)            
        if item.skoorivalem:
            item.max_pallid = const.MAX_SCORE

            # testime valemit
            e_locals = {'SKOOR': 10}
            value, err0, err, buf1 = model.eval_formula(item.skoorivalem, e_locals, divzero=0)
            if err:
                raise ValidationError(self, {'f_skoorivalem': err})
            elif not isinstance(value, (int, float)):
                raise ValidationError(self, {'f_skoorivalem': _("Valemiga arvutamine peab tulemuseks andma arvu")})

        if item.tahis:
            item.tahis = item.tahis.upper()
        if not self.request.params.get('is_tr'):
            #item.pos_yl_list = self.form.data.get('pos_yl_list')
            if self.form.data.get('peida_yl_list'):
                item.pos_yl_list = const.POS_NAV_HIDDEN
            else:
                item.pos_yl_list = const.POS_NAV_LEFT
            oli_piiraeg = item.piiraeg
            item.piiraeg = self.form.data.get('piiraeg')
            if item.piiraeg:
                for ty in item.testiylesanded:
                    if ty.piiraeg and ty.piiraeg > item.piiraeg:
                        self.c.dialog_testiosa = True
                        errors = {'piiraeg': _("Testiosas on ülesanne, mille piiraeg on suurem")}
                        raise ValidationError(self, errors)
                        
                for alatest in item.alatestid:
                    if alatest.vastvorm_kood != item.vastvorm_kood:
                        alatest.vastvorm_kood = item.vastvorm_kood
                    if alatest.piiraeg and alatest.piiraeg > item.piiraeg:
                        self.c.dialog_testiosa = True
                        errors = {'piiraeg': _("Testiosas on alatest, mille piiraeg on suurem")}
                        raise ValidationError(self, errors)
                hoiatusaeg = self.form.data.get('hoiatusaeg')
                if hoiatusaeg:
                    hoiatusaeg *= 60
                    if hoiatusaeg >= item.piiraeg:
                        self.c.dialog_testiosa = True
                        errors = {'hoiatusaeg': _("Hoiatusaeg ei saa olla testiosa piirajast suurem")}
                        raise ValidationError(self, errors)
                item.hoiatusaeg = hoiatusaeg
            else:
                item.hoiatusaeg = None
            if oli_piiraeg and item.piiraeg and oli_piiraeg != item.piiraeg:
                # kui piiraega muudeti, siis teeme pooleli sooritustele märke,
                # et brauseris on vaja taimereid muuta
                model.Sooritus.set_piiraeg_muutus(item.id)
                
            if item.yhesuunaline:
                # yhesuunalise testiosa kõik alatestid on yhekordsed (ei pruugi olla yhesuunalised)
                for alatest in item.alatestid:
                    if not alatest.on_yhekordne:
                        alatest.on_yhekordne = True

            seq = self.form.data['seq']
            if seq and item.seq != seq:
                # testiosa jrk muudeti
                model.Session.flush()
                osad = [o for o in self.c.test.testiosad if o != item]
                osad.insert(seq-1, item)
                for i, osa in enumerate(osad):
                    osa.seq = i + 1
                if seq == 1:
                    # tagasisidetunnused tuleb siduda esimese testiosaga
                    q = (model.Session.query(model.Normipunkt)
                         .join(model.Normipunkt.testiosa)
                         .filter(model.Testiosa.test_id==self.c.test.id)
                         )
                    for np in q.all():
                        if np.testiosa_id != item.id:
                            np.testiosa = item
                            
        if vana_tahis and item.tahis != vana_tahis:
            # testiosa tähist on muudetud
            model.Session.flush()
            for ta in item.toimumisajad:
                if not ta.kohad_kinnitatud:
                    ta.set_tahised()

        model.Session.flush()
        #if bool(oli_skoorivalem) != bool(item.skoorivalem):
        self.c.test.arvuta_pallid(True)

        lang = self.c.lang or None
        self.c.test.sum_tahemargid_lang(lang)

    def _update_lotv(self, item, oli_lotv):
        "Lõdva struktuuri kontrollid"
        if item.lotv:
            # lõdva struktuuri võimalus on mõeldud ainult kirjaliku e-testi jaoks
            if item.vastvorm_kood not in (const.VASTVORM_KE, const.VASTVORM_SE, const.VASTVORM_I):
                errors = {'f_lotv': _("Lõtva struktuuri saab kasutada ainult kirjalikes e-testides")}
                raise ValidationError(self, errors)

        if item.lotv and not oli_lotv:
            # lõdva struktuuri korral peavad hindamiskogumid koosnema valitudylesannetest
            for hk in item.hindamiskogumid:
                for ty in list(hk.testiylesanded):
                    # märgime ty-le vaikimisi hindamiskogumi
                    kv = item.give_komplektivalik(ty.alatest_id)
                    ty.hindamiskogum = kv.give_default_hindamiskogum()
                    for vy in ty.valitudylesanded:
                        # omistame vy-le hindamiskogumi
                        vy.hindamiskogum = hk
        elif oli_lotv and not item.lotv:
            # kui lõdva struktuuri märge ära võetakse, siis peavad hindamiskogumid koosnema testiülesannetest
            for ty in item.testiylesanded:
                kogumid = set()
                for vy in list(ty.valitudylesanded):
                    if ty.max_pallid is None:
                        ylesanne = vy.ylesanne
                        if ylesanne:
                            ty.max_pallid = ylesanne.max_pallid or 0
                    vy.update_koefitsient(ty)
                    if vy.hindamiskogum is not None:
                        kogumid.add(vy.hindamiskogum)
                        # eemaldame vy-lt hindamiskogumi
                        vy.hindamiskogum = None
                if len(kogumid) == 0:
                    # testiülesanne ei kuulu ühtegi hindamiskogumisse
                    kv = item.give_komplektivalik(ty.alatest_id)
                    ty.hindamiskogum = kv.give_default_hindamiskogum()
                    #ty.hindamiskogum = item.give_default_hindamiskogum()
                elif len(kogumid) == 1:
                    # kõik ty valitudylesanded on samast kogumist, omistame selle ty-le
                    ty.hindamiskogum = list(kogumid)[0]
                else:
                    # erinevad hindamiskogumid, ei saa lõtva struktuuri ära võtta
                    errors = {"f_lotv": _("Testiülesanne {s} on erinevates hindamiskogumites, mistõttu ei saa lõdva struktuuri märget eemaldada").format(s=ty.tahis)}
                    raise ValidationError(self, errors)
                        
        for hk in item.hindamiskogumid:
            hk.arvuta_pallid(item.lotv)
            
        #if item.lotv != oli_lotv:
        #    # kui lõtvust muudeti, siis arvutame testi max pallid uuesti
        #    self.c.test.arvuta_pallid(True)

    def _after_commit(self, item):
        if not item.tahis:
            item.tahis = item.id

    def _delete(self, item):
        rc = True
        for ta in item.toimumisajad:
            self.error(_("Testiosa ei saa kustutada, sest selle kohta on olemas toimumisaeg"))
            rc = False
            break
        else:
            q = model.Session.query(model.Sooritus.id).\
                filter_by(testiosa_id=item.id)
            if q.first():
                self.error(_("Testiosa ei saa kustutada, sest sellele on registreeritud sooritajaid"))
                rc = False
        if rc:
            try:
                item.delete()
                model.Session.flush()
                self.c.test.sum_tahemargid()            
                for ind, osa in enumerate(self.c.test.testiosad):
                    osa.seq = ind + 1
                self.c.test.arvuta_pallid(False)
            except Exception as e:
                self.error(_("Ei saa kustutada. ")+str(e, errors='replace'))
            else:
                self.success(_("Andmed on kustutatud"))
                model.Session.commit()

    def _after_update(self, id):
        """Mida teha peale õnnestunud salvestamist
        """        
        if not self.has_errors():
            self.success()
        return self._redirect('index', lang=self.c.lang)

    def _after_delete(self, parent_id=None):
        return HTTPFound(location=self.url('test_testiosad', test_id=parent_id,lang=self.c.lang))

    
    def __before__(self):
        """Väärtustame self.c.test testiga
        """
        test_id = self.request.matchdict.get('test_id')
        self.c.test = model.Test.get(test_id)

        self.c.lang = self.params_lang()
        if self.c.test:
            if self.c.lang and (self.c.lang == self.c.test.lang or self.c.lang not in self.c.test.keeled):
                self.c.lang = None
        else:
            self.c.lang = None
        super(TestiosadController, self).__before__()

    def _perm_params(self):
        return {'obj':self.c.test}

