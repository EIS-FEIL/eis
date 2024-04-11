# -*- coding: utf-8 -*- 
import os.path
import logging

from eis.lib.base import *
_ = i18n._
from eis.handlers.avalik.lahendamine import images

log = logging.getLogger(__name__)

class ImagesController(images.ImagesController):

    _permission = 'ekk-testid'

    def _check_esitlus(self, item, ylesanne_id):
        if item:
            rc = self.c.user.has_permission('ylesanded', const.BT_SHOW, ylesanne_id=ylesanne_id)
            if not rc:
                raise NotAuthorizedException('message', _("Puudub ligipääsuõigus"))
            return rc

    def _perm_params(self):
        test = model.Test.get(self.request.matchdict.get('test_id'))
        return {'obj': test}
