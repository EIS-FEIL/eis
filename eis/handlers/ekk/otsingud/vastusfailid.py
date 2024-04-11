import logging
from eis.handlers.avalik.sooritamine import vastusfailid

log = logging.getLogger(__name__)

class VastusfailidController(vastusfailid.VastusfailidController):
    _permission = 'aruanded-testisooritused'

    def show(self):
        return BaseResourceController.show(self)
