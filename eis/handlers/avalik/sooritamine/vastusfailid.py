import os.path
import urllib.request, urllib.parse, urllib.error

from eis.lib.baseresource import *
_ = i18n._
from eis.lib.block import BlockController

log = logging.getLogger(__name__)

class VastusfailidController(BaseResourceController):

    _MODEL = model.Kvsisu
    _authorize = False
    _actions = 'show,download'

    def show(self):
        kvs_id = self.request.matchdict.get('id')
        kvs = model.Kvsisu.get(kvs_id)
        assert kvs.kysimusevastus.ylesandevastus.sooritus == self.c.sooritus, _("vale sooritus")
        return utils.download(kvs.filedata, kvs.filename, None)        

    def __before__(self):
        self.c.sooritus_id = self.request.matchdict.get('sooritus_id')
        self.c.sooritus = model.Sooritus.get(self.c.sooritus_id)

    def _has_permission(self):
        c = self.c
        action = c.action
        if not c.sooritus:
            return False

        sooritaja = c.sooritus.sooritaja
        testiosa = c.sooritus.testiosa
        if c.sooritus.staatus == const.S_STAATUS_POOLELI:
            # lahendaja parajasti vastab
            if testiosa.vastvorm_kood == const.VASTVORM_I:
                # vastuseid sisestab intervjueerija
                testiruum_id = c.sooritus.testiruum_id
                q = (model.Labiviija.query
                     .filter(model.Labiviija.testiruum_id==testiruum_id)
                     .filter(model.Labiviija.kasutaja_id==c.user.id)
                     )
                intervjueerija = q.first()
                if intervjueerija:
                    return True
            elif c.sooritus.tugiisik_kasutaja_id:
                # vastuseid sisestab tugiisik
                if c.sooritus.tugiisik_kasutaja_id == c.user.id:
                    return True
            else:
                # vastuseid sisestab sooritaja ise
                if sooritaja.kasutaja_id == c.user.id:
                    return True
            # sisestaja on vale
            return False
        
        if action == 'show':
            # kas olen sooritaja või volitatud vastuste vaataja
            kasutaja = c.user.get_kasutaja()
            if kasutaja.on_volitatud(sooritaja.kasutaja_id):
                return True

            # kas olen hindaja
            rcd = (model.Hindamine.query
                   .filter(model.Hindamine.hindaja_kasutaja_id==c.user.id)
                   .join(model.Hindamine.hindamisolek)
                   .filter(model.Hindamisolek.sooritus_id==c.sooritus.id)
                   .first())
            if rcd:
                # olen selle töö hindaja
                return True

        return False

    def _get_log_params(self):
        action = self.c.action
        if action == 'create':
            return [('VASTUSEFAIL','FAIL')]
        else:
            return BaseController._get_log_params(self)
        
