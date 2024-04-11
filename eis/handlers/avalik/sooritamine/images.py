# -*- coding: utf-8 -*- 

import os.path

from eis.lib.base import *
_ = i18n._
from eis.lib.block import BlockController
from eis.handlers.avalik.lahendamine import images

log = logging.getLogger(__name__)

class ImagesController(images.ImagesController):
    """Piltide kuvamine testis
    """
    _permission = 'sooritamine'
    _authorize = True
    
    # def _check_esitlus(self, item, ylesanne_id):
    #     c = self.c
    #     if c.sooritus.staatus > const.S_STAATUS_ALUSTAMATA:
    #         q = (model.Session.query(model.sa.func.count(model.Valitudylesanne.id))
    #              .join(model.Valitudylesanne.testiylesanne)
    #              .filter(model.Testiylesanne.testiosa_id==c.sooritus.testiosa_id)
    #              .filter(model.Valitudylesanne.ylesanne_id==ylesanne_id))
    #         if q.scalar() > 0:
    #             return True
    #     return False

    def __before__(self):
        """Väärtustame testimiskorra id
        """
        c = self.c
        c.sooritus_id = self.convert_id(self.request.matchdict.get('sooritus_id'))
        super().__before__()
        # c.sooritus = model.Sooritus.get(sooritus_id)
        # c.testiosa = c.sooritus.testiosa
        # if c.testiosa and c.testiosa.vastvorm_kood == const.VASTVORM_I:
        #     if c.sooritus.toimumisaeg_id:
        #         # testimiskorraga suuline test, vastuseid sisestab intervjueerija
        #         testiruum_id = c.sooritus.testiruum_id
        #         q = (model.Labiviija.query
        #              .filter(model.Labiviija.testiruum_id==testiruum_id)
        #              .filter(model.Labiviija.kasutaja_id==c.user.id)
        #              )
        #         c.intervjueerija = q.first()
        #         if c.intervjueerija:
        #             c.olen_intervjueerija = True
        #     else:
        #         # testimiskorrata suuline test, vastuseid sisestab läbiviija
        #         testiruum = c.sooritus.testiruum
        #         c.olen_intervjueerija = testiruum.has_permission('testiadmin', const.BT_UPDATE, c.user)

    def _has_permission(self):
        c = self.c
        data = c.user.is_allowed_tos(c.sooritus_id)
        if data:
            return True

        # c.sooritaja = c.sooritus.sooritaja
        # if c.sooritus and c.sooritus.testiosa_id == c.testiosa.id:
        #     if c.testiosa.vastvorm_kood == const.VASTVORM_I:
        #         # sisestaja peab olema intervjueerija
        #         if not c.olen_intervjueerija:
        #             return False
        #     elif c.sooritus.tugiisik_kasutaja_id and c.sooritus.tugiisik_kasutaja_id != c.user.id:
        #         # kasutaja pole tugiisik
        #         return False
        #     elif not c.sooritus.tugiisik_kasutaja_id and c.sooritaja.kasutaja_id != c.user.id:
        #         # kasutaja pole sooritaja
        #         return False
        #     if c.user.testpw_id and c.user.testpw_id != c.sooritaja.id:
        #         # testiparooliga kasutajal on vale test
        #         return False
        #     return True
        return False
