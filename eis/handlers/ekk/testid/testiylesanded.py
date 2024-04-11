from eis.lib.baseresource import *
_ = i18n._

log = logging.getLogger(__name__)

class TestiylesandedController(BaseResourceController):
    """Testiülesanded
    """
    _permission = 'ekk-testid'
    _MODEL = model.Testiylesanne
    _EDIT_TEMPLATE = 'ekk/testid/testiylesanne.mako'
    _get_is_readonly = False
    
    @property
    def _ITEM_FORM(self):
        if self.c.test.diagnoosiv:
            return forms.ekk.testid.TestiylesanneDiag2Form
        elif self.request.params.get('is_tr'):
            return forms.ekk.testid.TestiylesanneTForm
        else:
            return forms.ekk.testid.TestiylesanneForm            

    def _new_d(self):
        """GET /admin_ITEMS/new: Form to create a new item"""
        testiosa_id = self.request.matchdict.get('testiosa_id')
        alatest_id = self.request.params.get('alatest_id') or None
        testiplokk_id = self.request.params.get('testiplokk_id') or None

        ty_tahis = self._get_next_tahis(testiosa_id, alatest_id)
        
        self.c.item = model.Testiylesanne(testiosa_id=testiosa_id, 
                                          alatest_id=alatest_id,
                                          testiplokk_id=testiplokk_id,
                                          liik='Y',
                                          kuvada_statistikas=True,
                                          naita_max_p=not self.c.test.diagnoosiv,
                                          tahis=ty_tahis,
                                          nimi=ty_tahis,
                                          valikute_arv=1)
        
        # lülitame autoflushi välja, et ID ei genereeritaks
        model.Session.autoflush = False
        self.c.item.post_create()
        self._edit(self.c.item)
        return self.response_dict

    def _edit(self, item):
        pass

    def _get_next_tahis(self, testiosa_id, alatest_id):
        "Leiame viimase jrknr järgi uue ülesande jrknr"
        if alatest_id:
            parent = model.Alatest.get(alatest_id)
        else:
            parent = model.Testiosa.get(testiosa_id)
        last_tahis = None
        for ty in parent.testiylesanded:
            if ty.tahis:
                last_tahis = ty.tahis
        if last_tahis:
            li = last_tahis.split('.')
            li[-1] = '%d' % (int(li[-1]) + 1)
            return '.'.join(li)

    def _create(self, **kw):
        c = self.c
        alatest_id = self.request.params.get('f_alatest_id') or None
        kv = c.testiosa.give_komplektivalik(alatest_id)
        hkogum = kv.give_default_hindamiskogum()
        item = model.Testiylesanne(testiosa=c.testiosa,
                                   hindamiskogum=hkogum)
        item.testiosa_id = c.testiosa.id # et seq õigesti arvutaks
        self._update(item)
        if c.testiosa.vastvorm_kood in (const.VASTVORM_SP, const.VASTVORM_SH):
            item.sisestusviis = const.SISESTUSVIIS_PALLID
        else:
            item.sisestusviis = const.SISESTUSVIIS_VASTUS

        mitu = self.form.data['mitu']
        if mitu:
            # korraga lisada mitu samasugust ylesannet
            model.Session.flush()
            model.Session.refresh(c.testiosa)
            # ilma len(testiylesanded) tegemata on seal item topelt
            log.debug('ty.seq=%s, len=%s' % (item.seq, len(c.testiosa.testiylesanded)))
            self._add_multiple(item, mitu)

        return item

    def _add_multiple(self, item, mitu):
        "Lisatud ylesandest koopiate tegemine, kui soovitakse korraga mitu sarnast ylesannet luua"
        testiosa = self.c.testiosa
        alatest = item.alatest or None
        testiplokk = item.testiplokk or None
        komplektivalik = alatest and alatest.komplektivalik or testiosa.give_komplektivalik()

        # ty nime genereerimise mall:
        # kui ylesande nimi on jrk nr või kui nimes viimasele punktile järgnev osa on jrk nr,
        # siis moodutatakse koopiate nimi samamoodi
        nimi_templ = None
        if item.nimi == str(item.seq):
            nimi_templ = '%d'
        else:
            r = item.nimi.rsplit('.', 1)
            if r[-1] == str(item.seq) and len(r) == 2:
                nimi_templ = r[0] + '.%d'

        for ind in range(1, mitu):
            cp_item = item.copy()
            cp_item.seq = item.seq + ind
            if nimi_templ:
                cp_item.nimi = nimi_templ % (item.seq + ind)
            testiosa.testiylesanded.append(cp_item)
            if alatest:
                alatest.testiylesanded.append(cp_item)
            if testiplokk:
                testiplokk.testiylesanded.append(cp_item)

            # kontrollime, et igal komplektil oleks sellest ülesandest valitudylesande kirje
            if komplektivalik:
                for komplekt in komplektivalik.komplektid:
                    cp_item.give_valitudylesanded(komplekt)          

        # arvutame uuesti testiploki ja testiosa pallid ja märgime ty tähised
        model.Session.flush()
        item.update_parent_stat()

    def update(self):
        id = self.request.matchdict.get('id')
        return BaseResourceController.update(self)
    
    def _update(self, item, lang=None):
        BaseResourceController._update(self, item, self.c.lang)

        pealkiri = '\n'.join(self.form.data.get('pealkiri') or [])
        if len(pealkiri) > 512:
            errors = {'pealkiri-0': _("Liiga pikk tekst (mahub max {n} tähte)").format(n=512)}
            raise ValidationError(self, errors)            
        if not self.request.params.get('is_tr'):
            item.pealkiri = pealkiri
        else:
            item.give_tran(self.c.lang).pealkiri = pealkiri
            
        # kontrollime, et on õige testi küljes
        assert int(item.testiosa_id) == int(self.request.matchdict.get('testiosa_id')), _("Vale testiosa")
        assert item.testiplokk_id is None or \
            int(item.testiplokk_id) == int(self.request.params.get('f_testiplokk_id')), _("Vale plokk")

        hk = item.hindamiskogum
        if hk and hk.on_kriteeriumid and item.max_pallid:
            # kriteeriumitega hinnatav ylesanne
            item.max_pallid = 0
        if item.max_pallid is not None:
            item.update_koefitsient()

        if not self.request.params.get('is_tr'):
            alatest = None
            if item.alatest_id:
                alatest = model.Alatest.get(item.alatest_id)
                item.alatest_seq = alatest.seq
                komplektivalik = alatest.komplektivalik
            else:
                testiosa = item.testiosa or model.Testiosa.get(item.testiosa_id)
                komplektivalik = testiosa.give_komplektivalik()

            item.piiraeg = self.form.data.get('piiraeg')
            if item.piiraeg:
                if alatest and alatest.piiraeg and item.piiraeg > alatest.piiraeg:
                    self.c.dialog_testiylesanne = True
                    errors = {'piiraeg': _("Ülesande piiraeg ei tohi ületada alatesti piiraega")}
                    raise ValidationError(self, errors)

                if self.c.testiosa.piiraeg and item.piiraeg > self.c.testiosa.piiraeg:
                    self.c.dialog_testiylesanne = True
                    errors = {'piiraeg': _("Ülesande piiraeg ei tohi ületada testiosa piiraega")}
                    raise ValidationError(self, errors)
                # hoiatusaeg sisestatakse minutites, salvestatakse sekundites
                hoiatusaeg_min = self.form.data.get('hoiatusaeg')
                if hoiatusaeg_min:
                    item.hoiatusaeg = hoiatusaeg_min * 60
                else:
                    item.hoiatusaeg = None
                if item.hoiatusaeg and item.hoiatusaeg >= item.piiraeg:
                    self.c.dialog_testiosa = True
                    errors = {'hoiatusaeg': _("Hoiatusaeg ei saa olla ülesande piirajast suurem")}
                    raise ValidationError(self, errors)
            else:
                item.hoiatusaeg = None

            item.min_aeg = self.form.data.get('min_aeg')
            if item.min_aeg and item.piiraeg and item.min_aeg >= item.piiraeg:
                errors = {'piiraeg': _("Maksimaalne piiraeg peab olema minimaalsest piirajast suurem")}
                raise ValidationError(self, errors)                
            
            # uuendame testiploki ja alatesti andmeid alluvate kohta
            model.Session.flush()
            item.update_parent_stat()

            # kontrollime, et igal komplektil oleks sellest ülesandest valitudylesande kirje
            if komplektivalik:
                for komplekt in komplektivalik.komplektid:
                    item.give_valitudylesanded(komplekt)          

        self.c.test.sum_tahemargid_lang(self.c.lang or None)
        
    def _after_update(self, id):
        self.success()
        return HTTPFound(location=self.url('test_struktuur1', 
                                           test_id=self.request.matchdict.get('test_id'),
                                           id=self.request.matchdict.get('testiosa_id'),
                                           lang=self.c.lang))

    def _delete(self, item):
        testiosa = item.testiosa
        hk = item.hindamiskogum
        item.delete()
        model.Session.commit()
        testiosa.test.arvuta_pallid()
        if hk:
            hk.arvuta_pallid(testiosa.lotv)
        self.c.test.sum_tahemargid()            
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
        super(TestiylesandedController, self).__before__()

    def _perm_params(self):
        return {'obj':self.c.test}

