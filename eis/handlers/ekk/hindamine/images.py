import os.path

from eis.lib.base import *
_ = i18n._
from eis.lib.block import BlockController
from eis.handlers.avalik.lahendamine import images

log = logging.getLogger(__name__)

class ImagesController(images.ImagesController):
    """Piltide kuvamine testis
    """
    _permission = 'hindamisanalyys' # eksperthindamine?

    def _check_image_permission(self, sisuobjekt):
        return True
