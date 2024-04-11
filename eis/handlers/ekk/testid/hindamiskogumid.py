from eis.lib.baseresource import *
_ = i18n._

log = logging.getLogger(__name__)

class HindamiskogumidController(BaseResourceController):
    """Testi hindamiskogumid
    """
    _permission = 'testimiskorrad'

    _MODEL = model.Hindamiskogum
    _EDIT_TEMPLATE = 'ekk/testid/kogumid.mako'
    _ITEM_FORM = forms.ekk.testid.HindamiskogumForm 

    def _new_d(self):
        self.c.testiosa_id = self.request.params.get('testiosa_id')
        self.c.testiosa = model.Testiosa.get(self.c.testiosa_id)
        if not self.c.testiosa.komplektivalikud:
            self.error(_("Hindamiskogumit ei saa luua, sest testiosas puuduvad ülesanded"))
            return HTTPFound(location=self.url('test_kogumid', test_id=self.c.test.id))
    
        self.c.item = model.Hindamiskogum(testiosa=self.c.testiosa)
        model.Session.autoflush = False
        sisestuskogum_id = self.request.params.get('sisestuskogum_id')
        self.c.item.sisestuskogum_id = sisestuskogum_id and int(sisestuskogum_id) or None        
        self.c.item.post_create()
        self._edit(self.c.item)
        return self.response_dict

    def _create(self, **kw):
        self.c.testiosa_id = int(self.request.params.get('testiosa_id'))
        self.c.testiosa = model.Testiosa.get(self.c.testiosa_id)
        kw['testiosa_id'] = self.c.testiosa_id
        item = BaseResourceController._create(self, **kw)

        self.c.sisestuskogum_id = self.request.params.get('sisestuskogum_id') 
        if self.c.sisestuskogum_id:
            self.c.sisestuskogum_id = int(self.c.sisestuskogum_id)
        item.sisestuskogum_id = self.c.sisestuskogum_id or None
            
        return item
    
    def _edit(self, item):
        self.c.hindamiskogum = item
        self.c.testiosa = item.testiosa
        self.c.komplektivalik_id = self.request.params.get('komplektivalik_id')
        if self.c.komplektivalik_id:
            # kasutaja valis valikväljalt komplektivaliku
            self.c.komplektivalik = model.Komplektivalik.get(self.c.komplektivalik_id)
        else:
            # vaikimisi kuvame hindamiskogumiga seotud komplektivaliku
            self.c.komplektivalik = item.get_komplektivalik()
            if self.c.komplektivalik:
                self.c.komplektivalik_id = self.c.komplektivalik.id
                                                          
        if item.sisestuskogum_id:
            self.c.sisestuskogum = item.sisestuskogum or model.Sisestuskogum.get(item.sisestuskogum_id)

    def _update(self, item, lang=None):
        self._bind_parent(item)
        self.c.testiosa = item.testiosa or model.Testiosa.get(item.testiosa_id)
        item.from_form(self.form.data, self._PREFIX, lang=lang)
        
        if item.sisestuskogum and item.hindamine_kood != item.sisestuskogum.hindamine_kood:
            item.sisestuskogum = None
            self.notice(_("Kuna uus hindamise liik erineb sisestuskogumi hindamise liigist, siis on hindamiskogum senisest sisestuskogumist eemaldatud"))

        if not item.vaikimisi:
            # kui pole vaikimisi hindamiskogum, siis saab ylesandeid valida
            # (vaikimisi kogumis ei saa, sest seal on need, mida mujale pole valitud)
            if self.c.testiosa.lotv:
                # lõtv struktuur - komplekt koosneb komplektiylesannetest
                self._update_valitudylesanded(item)
            else:
                # kindel struktuur - komplekt koosneb testiylesannetest
                self._update_testiylesanded(item)

        model.Session.flush()
        # arvutame iga hindamiskogumi pallid ja arvutihinnatavuse üle
        for hkogum in self.c.testiosa.hindamiskogumid:
            hkogum.arvuta_pallid(self.c.testiosa.lotv)

        if item.sisestuskogum:
            # uuendame andmed selle kohta, kas sisestuskogum sisestatakse 
            # p-testi korral hindamisprotokolliga või vastustega
            on_hindamisprotokoll = item.on_hindamisprotokoll
            on_vastused = not item.on_hindamisprotokoll
            skogum = item.sisestuskogum
            for rcd in skogum.hindamiskogumid:
                if rcd.on_hindamisprotokoll:
                    on_hindamisprotokoll = True
                else:
                    on_vastused = True
            skogum.on_hindamisprotokoll = on_hindamisprotokoll
            skogum.on_vastused = on_vastused

    def _update_testiylesanded(self, item):
        id_list = list(map(int, self.request.params.getall('ty_id')))

        for vy in item.valitudylesanded:
            vy.hindamiskogum_id = None
            
        n = 0
        on_skannimine = item.sisestuskogum and item.sisestuskogum.on_skannimine
        testiosa = item.testiosa or model.Testiosa.get(item.testiosa_id)
        hk_komplektivalik = model.Komplektivalik.get(item.komplektivalik_id)
        err_kvalik = False

        on_kriteeriumid = item.on_kriteeriumid
        hk_alatest_id = None
        err_krit = False
        
        # teeme muudatused hindamiskogumi sisus 
        for ty in testiosa.testiylesanded:
            if ty.id in id_list:
                # meie hindamiskogumi ylesanne
                hkogum = item
                if on_skannimine:
                    # kui on skannimine, siis see määrab ära sisestusviisi
                    if item.on_digiteerimine:
                        ty.sisestusviis = const.SISESTUSVIIS_VASTUS
                    else:
                        ty.sisestusviis = const.SISESTUSVIIS_PALLID

                # kriteeriumitega hindamiskogumi kõik ylesanded peavad olema samast alatestist,
                # et oleks võimalik alatestisoorituse punkte eristada
                if on_kriteeriumid:
                    if ty.max_pallid:
                        ty.max_pallid = None
                        ty.update_koefitsient()
                    if not hk_alatest_id:
                        hk_alatest_id = ty.alatest_id
                    elif hk_alatest_id != ty.alatest_id:
                        err_krit = True

                # yhes hindamiskogumis peavad kõik ylesanded olema samas komplektivalikus
                ty_komplektivalik = ty.get_komplektivalik()
                if hk_komplektivalik != ty_komplektivalik:
                    # see ty ei saa olla meie hindamiskogumis
                    err_kvalik = True
                    if ty.hindamiskogum == hkogum:
                        hkogum = ty_komplektivalik.give_default_hindamiskogum()
                    else:
                        hkogum = None
                
            elif ty.hindamiskogum == item:
                # ei ole meie hindamiskogumi ylesanne, aga seni oli
                ty_komplektivalik = ty.get_komplektivalik()
                hkogum = ty_komplektivalik.give_default_hindamiskogum()
            else:
                # ei ole meie hindamiskogumist ega tule ka
                hkogum = None

            if hkogum:
                if hkogum != ty.hindamiskogum:
                    ty.hindamiskogum = hkogum
                ty.update_koefitsient()
                if ty.alatest:
                    hkogum.kursus_kood = ty.alatest.kursus_kood

        if err_krit:
            self.error(_("Hindamiskriteeriumitega hindamiskogumi kõik ülesanded peavad kuuluma samasse alatesti"))
        elif err_kvalik:
            self.error(_("Hindamiskogumi kõik ülesanded peavad kuuluma samasse komplektivalikusse"))
            
    def _update_valitudylesanded(self, item):
        hk_komplektivalik = model.Komplektivalik.get(item.komplektivalik_id)
        
        id_list = list(map(int, self.request.params.getall('vy_id')))
        testiosa = item.testiosa or model.Testiosa.get(item.testiosa_id)

        # kui komplektis on testiylesandeid, siis eemaldame need
        # (lõdva struktuuri komplektis on valitudylesanded)
        for ty in item.testiylesanded:
            ty_komplektivalik = ty.get_komplektivalik()            
            ty.hindamiskogum = ty_komplektivalik.give_default_hindamiskogum()

        # eemaldame valitudylesanded, mis enam pole hindamiskogumis
        for vy in item.valitudylesanded:
            if vy.id not in id_list:
                vy.hindamiskogum_id = None
            else:
                id_list.remove(vy.id)

        on_kriteeriumid = item.on_kriteeriumid
        hk_alatest_id = None
        err_krit = False
        
        # lisame valitudylesanded, mis on hindamiskogumisse lisatud
        for vy_id in id_list:
            vy = model.Valitudylesanne.get(vy_id)
            ty = vy.testiylesanne
            ty_komplektivalik = ty.get_komplektivalik()
            if ty_komplektivalik == hk_komplektivalik:
                vy.hindamiskogum = item

            if on_kriteeriumid:
                if not hk_alatest_id:
                    hk_alatest_id = ty.alatest_id
                elif hk_alatest_id != ty.alatest_id:
                    err_krit = True
                
        if err_krit:
            self.error(_("Hindamiskriteeriumitega hindamiskogumi kõik ülesanded peavad kuuluma samasse alatesti"))

    def _delete_except(self, item):
        q = (model.Session.query(model.Hindamisolek.id)
             .filter_by(hindamiskogum_id=item.id)
             .limit(1))
        for r in q.all():
            msg = _("Hindamisolekut ei saa enam kustutada, sest sellega on juba testitööd seotud")
            self.error(msg)
            model.Session.rollback()
            return
        q = (model.Session.query(model.Labiviija.id)
            .filter_by(hindamiskogum_id=item.id)
            .limit(1))
        for r in q.all():
            msg = _("Hindamisolekut ei saa enam kustutada, sest sellega on juba läbiviijad seotud")
            self.error(msg)
            model.Session.rollback()
            return
        return super()._delete_except(item)
    
    def _after_delete(self, parent_id=None):
        return HTTPFound(location=self.url('test_kogumid', test_id=self.c.test.id))

    def __before__(self):
        """Väärtustame self.c.test testiga
        """
        test_id = self.request.matchdict.get('test_id')
        self.c.test = model.Test.get(test_id)

        BaseResourceController.__before__(self)

    def _perm_params(self):
        return {'obj':self.c.test}

