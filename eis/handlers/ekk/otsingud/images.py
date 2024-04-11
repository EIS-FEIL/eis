import os.path
import logging

from eis.lib.base import *
_ = i18n._
from eis.handlers.avalik.lahendamine import images

log = logging.getLogger(__name__)

class ImagesController(images.ImagesController):
    _permission = 'aruanded-testisooritused'

    def _check_image_permission(self, sisuobjekt):
        return True
    
