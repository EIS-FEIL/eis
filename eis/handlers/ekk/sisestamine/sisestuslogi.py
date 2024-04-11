# -*- coding: utf-8 -*- 
# $Id: sisestuslogi.py 361 2016-02-18 14:47:11Z ahti $

from eis.lib.base import *
log = logging.getLogger(__name__)

class SisestuslogiController(BaseController):
    """Sisestuslogi (sisestuses tehtud muudatused)
    """
    _permission = 'sisestamine'
    _INDEX_TEMPLATE = 'ekk/sisestamine/sisestuslogi.mako'

    def index(self):
        return self.render_to_response(self._INDEX_TEMPLATE)

    def __before__(self):
        self.c.hindamine = model.Hindamine.get(self.request.matchdict.get('hindamine_id'))
