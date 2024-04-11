# -*- coding: utf-8 -*- 

from eis.lib.baseresource import *
_ = i18n._

log = logging.getLogger(__name__)

class KomplektivalikudController(BaseResourceController):
    """Ülesandekomplektide valikus olevate alatestide valiku muutmine
    """
    _permission = 'ekk-testid'
    _MODEL = model.Komplektivalik
    _EDIT_TEMPLATE = 'ekk/testid/komplektivalik.mako'
    _INDEX_TEMPLATE = 'ekk/testid/valitudylesanded.mako'
    _ITEM_FORM = forms.ekk.testid.KomplektivalikForm 

    def _update(self, item):
        if item.lukus:
            self.error(_("Valik sisaldab lukustatud komplekte"))
            return
        
        alatestid_id = self.form.data.get('alatest_id')
        olds_alatest = set()
        # eemaldame komplektivalikust eemaldatud alatestid
        for alatest in list(item.alatestid):
            if alatest.id not in alatestid_id:
                olds_alatest.add(alatest)
            else:
                alatestid_id.remove(alatest.id)

        if olds_alatest:
            # eemaldatud alatestidele loome uue komplektivaliku
            new_kv = model.Komplektivalik(testiosa=self.c.testiosa)
            new_hk = new_kv.give_default_hindamiskogum()
            for alatest in olds_alatest:
                new_kv.alatestid.append(alatest)
                for ty in alatest.testiylesanded:
                    ty.hindamiskogum = new_hk
                    if self.c.testiosa.lotv:
                        for vy in ty.valitudylesanded:
                            vy.hindamiskogum = None
                            
        # lisame komplektivalikule lisatud alatestid
        olds_kv = set()
        for alatest_id in alatestid_id:
            alatest = model.Alatest.get(alatest_id)
            if alatest.testiosa_id == self.c.testiosa.id:
                old_kv = alatest.komplektivalik
                if old_kv is not None:
                    olds_kv.add(old_kv)
                alatest.komplektivalik = item
                item.alatestid.append(alatest)                

        if olds_kv:
            for old_kv in olds_kv:
                log.debug('eemaldame kv %s' % old_kv.id)
                for hk in list(old_kv.hindamiskogumid):
                    log.debug(' nihutame hk %s' % hk.id)
                    item.hindamiskogumid.append(hk)
                    hk.komplektivalik = item

            model.Session.flush()
            for old_kv in olds_kv:
                try:
                    old_kv.delete()
                except sa.exc.IntegrityError as e:
                    msg = _("Ei saa enam kustutada, sest on seotud andmeid ")
                    msg1 = '%s [%s] %s' % (msg, self.request.url, str(e))
                    log.info(msg1)
                    raise ValidationError(self, {}, msg)
            model.Session.flush()                
        
        # kontrollime, et komplektivalik ei jaguneks rohkem kui yhte sisestuskogumisse
        sisestuskogumid_id = set()
        for alatest in item.alatestid:
            for ty in alatest.testiylesanded:
                sisestuskogumid_id.add(ty.hindamiskogum.sisestuskogum_id)
        if len(sisestuskogumid_id) > 1:
            raise ValidationError(self, {}, _("Kõik ülesanded peavad kuuluma samasse sisestuskogumisse"))

        on_alatestid = len(self.c.testiosa.alatestid) > 0
        if on_alatestid and len(item.alatestid) == 0:
            model.Session.flush()                            
            if len(item.komplektid) == 0:
                # liigseks jäänud komplektivalik, eemaldame
                for hk in list(item.hindamiskogumid):
                    for ty in list(hk.testiylesanded):
                        kv = ty.alatest.komplektivalik
                        ty.hindamiskogum = kv.give_default_hindamiskogum()
                    hk.delete()
                item.delete()
                model.Session.commit()
                return self._after_delete()
            
            raise ValidationError(self, {}, _("Vähemalt üks alatest peab olema valitud"))            
        
        # lisame igale testiylesandele valitudylesande kirje, kus veel pole
        item.give_valitudylesanded()

        if on_alatestid:
            # eemaldame yle jäänud tyhjad komplektivalikud
            for kv in list(self.c.testiosa.komplektivalikud):
                if kv != item:
                    if len(kv.alatestid) == 0:
                        for hk in kv.hindamiskogumid:
                            for ty in hk.testiylesanded:
                                ty.hindamiskogum = ty.alatest.komplektivalik.give_default_hindamiskogum()
                            hk.delete()
                        kv.delete()

        # et ei tekiks mitu alatestideta komplektivalikut
        item.alatestideta = len(item.alatestid) == 0 and True or None

    def _after_update(self, id):
        self.success()
        return HTTPFound(location=self.url('test_valitudylesanded', 
                                           test_id=self.request.matchdict.get('test_id'),
                                           testiosa_id=self.c.testiosa.id,
                                           komplekt_id=self.c.komplekt_id,
                                           komplektivalik_id=id))

    def _after_delete(self, parent_id=None):
        return HTTPFound(location=self.url('test_valitudylesanded',
                                           test_id=self.c.test.id,
                                           testiosa_id=self.c.testiosa.id))
    
    def __before__(self):
        """Väärtustame self.c.test testiga
        """
        test_id = self.request.matchdict.get('test_id')
        self.c.test = model.Test.get(test_id)
        testiosa_id = self.request.matchdict.get('testiosa_id')
        self.c.testiosa = model.Testiosa.get(testiosa_id)
        self.c.komplekt_id = self.request.params.get('komplekt_id')
        BaseResourceController.__before__(self)

    def _perm_params(self):
        return {'obj':self.c.test}
