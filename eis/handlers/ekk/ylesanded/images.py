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
    _permission = 'ylesanded'

    def _check_esitlus(self, item, ylesanne_id):
        if item:
            rc = self.c.user.has_permission('ylesanded', const.BT_SHOW, ylesanne_id=ylesanne_id)
            if not rc:
                raise NotAuthorizedException('message', _("Puudub ligipääsuõigus"))
            return rc

    def _perm_params(self):
        ylesanne = model.Ylesanne.get(self.request.matchdict.get('ylesanne_id'))
        return {'obj': ylesanne}

    def __before__(self):
        self._lang = self.request.matchdict.get('lang')
        images.ImagesController.__before__(self)
