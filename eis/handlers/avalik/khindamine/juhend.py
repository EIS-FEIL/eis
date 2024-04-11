"Testi ülesande hindamisjuhendi ja hindamisjuhi küsimuste näitamine kirjalikule hindajale"

from eis.lib.baseresource import *
_ = i18n._
from .hkhindamine import get_tab_urls 
log = logging.getLogger(__name__)

class JuhendController(BaseResourceController):
    _permission = 'khindamine'
    _actions = 'index,downloadfile'
    _INDEX_TEMPLATE = 'avalik/khindamine/hindamine_r.juhend.mako'     

    def _index_d(self):
        self._get_tab_urls()
        return self.response_dict

    def _get_tab_urls(self):
        get_tab_urls(self, self.c)

    def downloadfile(self):
        """Näita faili
        """
        ylesandefail_id = self.request.matchdict.get('file_id')
        format = self.request.matchdict.get('format')
        item = model.Hindamisobjekt.get(ylesandefail_id)
        if not item:
            raise NotFound('Kirjet ei leitud')
        assert item.ylesanne_id == self.c.vy.ylesanne_id, _("Vale ülesanne")
        return utils.download(item.filedata, item.filename, item.mimetype)

    def __before__(self):
        id = self.request.matchdict.get('vy_id')
        c = self.c
        c.vy = model.Valitudylesanne.get(id)
        c.ylesanne = c.vy.ylesanne
        toimumisaeg_id = self.request.matchdict.get('toimumisaeg_id')
        c.toimumisaeg = model.Toimumisaeg.get(toimumisaeg_id)
        if c.toimumisaeg.testiosa.lotv:
            c.hindamiskogum = c.vy.hindamiskogum
        else:
            c.hindamiskogum = c.vy.testiylesanne.hindamiskogum
        c.on_kriteeriumid = c.hindamiskogum.on_kriteeriumid
        c.lang = self.params_lang()
        c.indlg = self.request.params.get('indlg')
        
    def _has_permission(self):
        # suulise hindamise korral on antud c.testiruum
        # kirjaliku hindamise korral on antud c.toimumisaeg
        c = self.c
        hk_id = c.hindamiskogum.id
        c.hindaja = c.toimumisaeg.get_hindaja(c.user.id, hindamiskogum_id=hk_id)
        return self.c.hindaja is not None

