# -*- coding: utf-8 -*- 
# $Id: images_h.py 890 2016-09-29 13:46:02Z ahti $

import os.path
import logging

from eis.lib.base import model
from eis.handlers.avalik.lahendamine import images

log = logging.getLogger(__name__)

class ImagesController(images.ImagesController):
    _permission = 'khindamine'
    def _check_image_permission(self, sisuobjekt):
        return True

    def _has_permission(self):
        rc = False
        testiruum_id = self.request.matchdict.get('testiruum_id')
        testiruum = model.Testiruum.get(testiruum_id)
        nimekiri = testiruum.nimekiri
        if nimekiri:
            if self.c.user.on_pedagoog:
                rc = nimekiri.esitaja_koht_id==self.c.user.koht_id
            else:
                rc = nimekiri.esitaja_kasutaja_id==self.c.user.id
        return rc
