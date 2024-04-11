from eis.lib.baseresource import *

from .otsiylesanded import OtsiylesandedController
from .otsiylesandekogud import OtsiylesandekogudController
from .otsitookogumikud import OtsitookogumikudController
from .testiosavalik import Testiosavalik
_ = i18n._
log = logging.getLogger(__name__)

class YlesandedController(BaseResourceController, Testiosavalik):

    _permission = 'testid'
    _MODEL = model.Testiylesanne
    _INDEX_TEMPLATE = 'avalik/testid/ylesanded.mako'

    def index(self):
        c = self.c
        request = self.request
        request.matchdict['action'] = 'index'
        
        handler = OtsiylesandedController(request)
        c.body_yl = handler.index().body.decode('utf-8')

        if c.user.on_pedagoog:
            handler = OtsiylesandekogudController(request)
            c.body_yk = handler.index().body.decode('utf-8')

            handler = OtsitookogumikudController(request)
            c.body_tk = handler.index().body.decode('utf-8')
        return self._showlist()

    def create(self):
        """Ülesannete lisamine testile.
        id on seq
        """
        testiosa = self.c.test.give_testiosa()
        kv = testiosa.give_komplektivalik()
        komplekt = kv.give_komplekt()
        seq = len(testiosa.testiylesanded)
        hkogum = kv.give_default_hindamiskogum()

        for ylesanne_id in self.request.params.getall('ylesanne_id'):
            seq += 1
            ylesanne = model.Ylesanne.get(ylesanne_id)
            ty = model.Testiylesanne(testiosa=testiosa, 
                                     valikute_arv=1, 
                                     hindamiskogum=hkogum,
                                     seq=seq, 
                                     tahis=str(seq),
                                     arvutihinnatav=ylesanne.arvutihinnatav,
                                     max_pallid=ylesanne.max_pallid)
            testiosa.testiylesanded.append(ty)
            li_vy = ty.give_valitudylesanded(komplekt)
            li_vy[0].ylesanne_id = ylesanne.id
            li_vy[0].koefitsient = 1.

        model.Session.commit()
        hkogum.arvuta_pallid(testiosa.lotv)
        self.c.test.arvuta_pallid()
        self.c.test.update_lang_by_y()
        model.Session.commit()
        self.success()       
        return HTTPFound(location=self.url('testid_edit_struktuur',id=self.c.test_id, testiruum_id=self.c.testiruum_id))

    def _delete(self, item):
        q = (model.Ylesandevastus.query
             .join((model.Valitudylesanne,
                    model.Valitudylesanne.id==model.Ylesandevastus.valitudylesanne_id))
             .filter(model.Valitudylesanne.testiylesanne_id==item.id))
        if q.count():
            self.error(_('Ülesannet on testi käigus juba lahendatud ja seda ei saa eemaldada'))
            return
        else:
            ylesanded = [vy.ylesanne for vy in item.valitudylesanded]
            
            item.delete()
            self.c.test.update_lang_by_y()
            for testiosa in self.c.test.testiosad:
                for kv in testiosa.komplektivalikud:
                    for komplekt in kv.komplektid:
                        komplekt.copy_lang(self.c.test)            
            model.Session.flush()
            for y in ylesanded:
                if y and y.lukus and not y.get_lukustusvajadus():
                    y.lukus = None
            self.success(_('Andmed on kustutatud!'))
            model.Session.commit()       

    def _after_delete(self, parent_id=None):
        self.c.test.arvuta_pallid()
        model.Session.commit()
        return HTTPFound(location=self.url('testid_struktuur', id=self.c.test_id, testiruum_id=self.c.testiruum_id))

    def __before__(self):
        """Väärtustame self.c.test testiga
        """
        c = self.c
        Testiosavalik.set_test_testiosa(self)
        c.komplekt_id = self.request.matchdict.get('komplekt_id')
        c.seq = self.request.matchdict.get('id')
        BaseResourceController.__before__(self)

    def _perm_params(self):
        return {'obj': self.c.test}

