import logging

from eis.lib.base import model
from eis.handlers.avalik.lahendamine import images

log = logging.getLogger(__name__)

class ImagesController(images.ImagesController):

    _permission = 'lahendamine'
