import os.path
import urllib.request, urllib.parse, urllib.error

from eis.lib.baseresource import *
_ = i18n._
from eis.lib.block import BlockController

log = logging.getLogger(__name__)

class SkannidController(BaseController):
    """Skannitud vastuse pildi kuvamine
    """
    _authorize = False

    def skskann(self):
        "Ühe sisestuskogumi PDFi kuvamine"
        s_id = self.request.matchdict.get('id')
        solek = model.Sisestusolek.get(s_id)
        assert solek.sooritus == self.c.sooritus, _("Vale sooritus")
        return utils.download(solek.skann, 
                              'vastus%s.pdf' % (solek.sisestuskogum_id), 
                              const.CONTENT_TYPE_PDF)        

    def yvskann(self):
        "Ühe ülesande vastuse väljalõike jpg kuvamine"
        yv_id = self.request.matchdict.get('id')
        yv = model.Ylesandevastus.get(yv_id)
        assert yv.sooritus == self.c.sooritus, _("Vale sooritus")
        return utils.download(yv.skann, 'vastus.jpg', const.MIMETYPE_IMAGE_JPEG)        

    def kvskann(self):
        "Ühe küsimuse ühe vastuse väljalõike jpg kuvamine"
        kvk_id = self.request.matchdict.get('id')
        kvk = model.Kvskann.get(kvk_id)
        assert kvk.kysimusevastus.ylesandevastus.sooritus == self.c.sooritus, _("Vale sooritus")
        return utils.download(kvk.skann, 'vastus.jpg', const.MIMETYPE_IMAGE_JPEG)        

    def __before__(self):
        self.c.sooritus_id = self.request.matchdict.get('sooritus_id')
        self.c.sooritus = model.Sooritus.get(self.c.sooritus_id)

    def _has_permission(self):
        action = self.c.action
        if not self.c.sooritus:
            return False

        sooritaja = self.c.sooritus.sooritaja
        if sooritaja.kasutaja_id == self.c.user.id:
            if self.c.sooritus.staatus == const.S_STAATUS_POOLELI:
                # lahendaja parajasti vastab
                return True

        # kas olen sooritaja või volitatud vastuste vaataja
        kasutaja = self.c.user.get_kasutaja()
        if kasutaja.on_volitatud(sooritaja.kasutaja_id):
            return True

        # kas olen hindaja
        rcd = model.Hindamine.query.\
            filter(model.Hindamine.hindaja_kasutaja_id==self.c.user.id).\
            join(model.Hindamine.hindamisolek).\
            filter(model.Hindamisolek.sooritus_id==self.c.sooritus.id).\
            first()
        if rcd:
            # olen selle töö hindaja
            return True

        return False
