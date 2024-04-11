# -*- coding: utf-8 -*- 
# $Id: images.py 9 2015-06-30 06:34:46Z ahti $

import os.path
import logging

from eis.lib.base import model
from eis.handlers.avalik.lahendamine import images

log = logging.getLogger(__name__)

class ImagesController(images.ImagesController):
    _permission = 'khindamine'
    def _check_image_permission(self, sisuobjekt):
        #ylesanne_id = int(self.request.matchdict.get('ylesanne_id'))
        #return sisuobjekt.sisuplokk.ylesanne_id == ylesanne_id
        return True


    def _has_permission(self):
        rc = False
        testiruum_id = self.request.matchdict.get('testiruum_id')
        if testiruum_id:
            # oma testi hindamine
            testiruum = model.Testiruum.get(testiruum_id)
            nimekiri = testiruum.nimekiri
            if nimekiri:
                if self.c.user.on_pedagoog:
                    rc = nimekiri.esitaja_koht_id==self.c.user.koht_id
                else:
                    rc = nimekiri.esitaja_kasutaja_id==self.c.user.id
        else:
            # testimiskorraga testi hindamine?
            toimumisaeg_id = self.request.matchdict.get('toimumisaeg_id')
            if toimumisaeg_id:
                hindaja = model.Labiviija.get_hindaja_by_user(toimumisaeg_id,
                                                            None,
                                                            self.c.user)

                rc = hindaja is not None
        return rc
