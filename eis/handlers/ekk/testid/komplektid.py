from eis.lib.baseresource import *
_ = i18n._
from eis.lib.testsaga import TestSaga
log = logging.getLogger(__name__)

class KomplektidController(BaseResourceController):
    """Ülesandekomplektid
    """
    _permission = 'ekk-testid'
    _MODEL = model.Komplekt
    _EDIT_TEMPLATE = 'ekk/testid/komplekt.mako'
    _INDEX_TEMPLATE = 'ekk/testid/valitudylesanded.mako'
    _ITEM_FORM = forms.ekk.testid.KomplektForm 

    def _create(self, **kw):
        komplektivalik_id = self.form.data.get('komplektivalik_id')
        if not komplektivalik_id:
            # kui pole valitud komplektivalik, siis peab olema valitud selline alatest,
            # millel veel komplektivalikut ei ole
            if self.c.testiosa.on_alatestid:
                kvalik = model.Komplektivalik(testiosa=self.c.testiosa)
                alatestid_id = self.form.data.get('alatest_id')

                for alatest in self.c.testiosa.alatestid:
                    if alatest.id in alatestid_id:
                        if alatest.komplektivalik_id == None:
                            if len(kvalik.alatestid) == 0:
                                # valiku esimene alatest määrab valiku kursuse
                                kvalik.kursus_kood = alatest.kursus_kood
                                kvalik.alatestid.append(alatest)
                            elif kvalik.kursus_kood == alatest.kursus_kood:
                                # valiku muud alatestid peavad olema samas kursuses
                                kvalik.alatestid.append(alatest)

                # kontrollime, et komplektivalik ei jaguneks rohkem kui yhte sisestuskogumisse
                sisestuskogumid_id = set()
                for alatest in kvalik.alatestid:
                    for ty in alatest.testiylesanded:
                        sisestuskogumid_id.add(ty.hindamiskogum.sisestuskogum_id)
                        if len(sisestuskogumid_id) > 1:
                            raise ValidationError(self, {}, _("Kõik ülesanded peavad kuuluma samasse sisestuskogumisse"))

                if len(kvalik.alatestid) == 0:
                    raise ValidationError(self, {}, _("Vähemalt üks alatest peab olema valitud"))            
            else:
                # ei ole alateste
                kvalik = self.c.testiosa.give_komplektivalik()
        else:
            # kui komplektivalikus on mitu alatesti, siis tuleb vormilt jada,
            # milles kordub yks ja sama id
            kvalik = model.Komplektivalik.get(komplektivalik_id[0])            

        item = model.Komplekt(komplektivalik=kvalik)
        self._update(item)

        # et ei tekiks mitu alatestideta komplektivalikut
        alatestideta = len(kvalik.alatestid) == 0 and True or None
        kvalik.alatestideta = alatestideta
        if alatestideta:
            # kui pole alateste, siis saab olla ainult yks komplektivalik
            for kv in list(self.c.testiosa.komplektivalikud):
                if kv.id != kvalik.id:
                    for hk in kv.hindamiskogumid:
                        if not hk.staatus:
                            hk.delete()
                    kv.delete()
        # lisame igale testiylesandele valitudylesande kirje, kus veel pole
        kvalik.give_valitudylesanded()
        return item

    def _update(self, item):
        if not self.form.data.get('skeel'):
            raise ValidationError(self, {'skeel': _("Palun valida keel")})            
        item.skeeled = ' '.join(self.form.data.get('skeel'))
        try:
            BaseResourceController._update(self, item)
            item.flush()
        except sa.exc.IntegrityError as e:
            raise ValidationError(self, {'f_tahis': _("Palun sisestada unikaalne tähis")})
        self._check_keeled(item)
        TestSaga(self).komplekt_set_lukus(item)
        
    def _new(self, item):
        if not self.c.testiosa:
            self.c.testiosa = self.c.test.testiosad[0]

        self.c.kursus = kursus = self.request.params.get('kursus')
        item.komplektivalik_id = self.request.params.get('komplektivalik_id')
        if item.komplektivalik_id:
            item.komplektivalik_id = int(item.komplektivalik_id)
        else:
            valikud = self.c.testiosa.komplektivalikud
            if kursus:
                valikud = [r for r in valikud if r.kursus_kood == kursus]
            if valikud:
                item.komplektivalik = valikud[0]
        item.gen_tahis()
        item.copy_lang(self.c.test)
    
    def _check_keeled(self, item):
        li = []
        for vy in item.valitudylesanded:
            if vy.ylesanne_id:
                if not set(item.keeled).issubset(set(vy.ylesanne.keeled)):
                    li.append(str(vy.ylesanne_id))
        if len(li):
            self.error(_("Hoiatus: ülesanded {s} pole komplekti keeles").format(s=', '.join(li)))
        
    def _after_commit(self, item):
        if not item.tahis:
            item.tahis = item.id

    def _after_update(self, id):
        self.success()
        return HTTPFound(location=self.url('test_valitudylesanded', 
                                           test_id=self.request.matchdict.get('test_id'),
                                           testiosa_id=self.c.testiosa.id,
                                           komplektivalik_id=self.request.params.get('komplektivalik_id'),
                                           komplekt_id=id))


    def delete(self):
        args = {'test_id': self.c.test.id, 'testiosa_id': self.c.testiosa.id}
        id = self.request.matchdict.get('id')
        item = model.Komplekt.get(id)
        if item:
            komplektivalik = item.komplektivalik
            #delete_kvalik = len(komplektivalik.komplektid) == 1 and len(komplektivalik.hindamiskogumid) <= 1            
            try:
                item.delete()
                #if delete_kvalik:
                #    komplektivalik.delete()
                model.Session.commit()
                self.success(_("Andmed on kustutatud"))
            except sa.exc.IntegrityError as e:
                msg = _("Ei saa enam kustutada, sest on seotud andmeid ")
                self.error(msg)
                msg = '%s [%s] %s' % (msg, self.request.url, str(e))
                log.info(msg)
                model.Session.rollback()

            #if not delete_kvalik:
            args['komplektivalik_id'] = komplektivalik.id
        
        return HTTPFound(location=self.url('test_valitudylesanded', **args))
    
    def __before__(self):
        """Väärtustame self.c.test testiga
        """
        test_id = self.request.matchdict.get('test_id')
        self.c.test = model.Test.get(test_id)
        testiosa_id = self.request.matchdict.get('testiosa_id')
        self.c.testiosa = model.Testiosa.get(testiosa_id)
        BaseResourceController.__before__(self)

    def _perm_params(self):
        return {'obj':self.c.test}
