"Testi ülesande sisu näitamine kirjalikule hindajale"

from eis.lib.baseresource import *
_ = i18n._
from eis.handlers.avalik.lahendamine import lahendamine
from .hkhindamine import get_tab_urls
log = logging.getLogger(__name__)

class LahendamineController(lahendamine.LahendamineController):
    _permission = 'khindamine'
    _EDIT_TEMPLATE = 'avalik/khindamine/hindamine_r.lahendamine.mako'     
    _actions = 'edit,update,show'

    def edit(self):
        self._get_tab_urls()
        if self.request.params.get('correct'):
            # õige vastuse sakk
            self.c.show_correct = True
            self.c.read_only = True
        else:
            # ei tee õige vastuse nuppu, kuna õige vastus on eraldi sakis
            self.c.prepare_correct = False
            self.c.btn_correct = False
        return super().edit()

    def _gentask(self, **kw):
        # kirjutame yle pcorrect ja bcorrect
        kw['pcorrect'] = self.c.read_only
        kw['bcorrect'] = False
        return super()._gentask(**kw)
    
    def _get_tab_urls(self):
        get_tab_urls(self, self.c)
              
    def __before__(self):
        c = self.c
        vy_id = self.request.matchdict.get('vy_id')
        c.vy = model.Valitudylesanne.get(vy_id)
        id = self.request.matchdict.get('id')
        c.ylesanne = model.Ylesanne.get(id)
        toimumisaeg_id = self.request.matchdict.get('toimumisaeg_id')
        c.toimumisaeg = model.Toimumisaeg.get(toimumisaeg_id)
        c.lang = self.params_lang()
        c.indlg = self.request.params.get('indlg')
        c.inint = self.request.params.get('inint')
        if c.toimumisaeg.testiosa.lotv:
            hk_id = c.vy.hindamiskogum_id
        else:
            hk_id = c.vy.testiylesanne.hindamiskogum_id
        c.hindamiskogum = model.Hindamiskogum.get(hk_id)

    def _has_permission(self):
        ## suulise hindamise korral on antud c.testiruum
        ## kirjaliku hindamise korral on antud c.toimumisaeg
        c = self.c
        if c.ylesanne.id != c.vy.ylesanne_id:
            return False
        hindaja = c.toimumisaeg.get_hindaja(c.user.id, hindamiskogum_id=c.hindamiskogum.id)
        return hindaja is not None

    def _check_status(self, item):
        # hindaja peab ylesandele ligi saama
        return True
