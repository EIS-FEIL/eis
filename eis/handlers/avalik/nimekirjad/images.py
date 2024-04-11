# -*- coding: utf-8 -*- 
# $Id: images.py 406 2016-03-07 19:18:48Z ahti $

import os.path

from eis.lib.base import *
_ = i18n._
from eis.handlers.avalik.lahendamine import images

log = logging.getLogger(__name__)

class ImagesController(images.ImagesController):
    """Piltide kuvamine testis
    """
    _permission = 'nimekirjad'

    def _check_image_permission(self, sisuobjekt):
        #ylesanne_id = int(self.request.matchdict.get('ylesanne_id'))
        #return sisuobjekt.sisuplokk.ylesanne_id == ylesanne_id
        # SELECT count(*) FROM valitudylesanne vy, toimumisaeg_komplekt tk
        # WHERE vy.ylesanne_id=%d
        # AND vy.komplekt_id=tk.komplekt_id
        # AND tk.toimumisaeg_id=%d
        # % (sisuobjekt.sisuplokk.ylesanne_id, self.sooritus.toimumisaeg_id)

        return True

    def _has_permission(self):
        # Soorituse kirje peab olema olemas
        # sooritus_id = self.request.matchdict.get('sooritus_id')
        # self.sooritus = model.Sooritus.get(sooritus_id)
        # if self.sooritus and \
        #         self.sooritus.sooritaja.kasutaja_id == self.c.user.id and \
        #         self.sooritus.staatus == const.S_STAATUS_TEHTUD:
        #     return True
        # return False
        return True
