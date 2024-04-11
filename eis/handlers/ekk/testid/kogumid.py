# -*- coding: utf-8 -*- 
# $Id: kogumid.py 406 2016-03-07 19:18:48Z ahti $

from eis.lib.baseresource import *
_ = i18n._

log = logging.getLogger(__name__)

class KogumidController(BaseResourceController):
    """Kogumid - hindamiskogumid ja sisestuskogumid
    """
    _permission = 'testimiskorrad'
    _MODEL = model.Hindamiskogum
    #_EDIT_TEMPLATE = 'ekk/testid/ylesanne.mako'
    _INDEX_TEMPLATE = 'ekk/testid/kogumid.mako'


    def index(self):
        self.c.testiosa_id = self.request.params.get('testiosa_id')
        if self.c.testiosa_id:
            self.c.testiosa = model.Testiosa.get(self.c.testiosa_id)
        return self.render_to_response(self._INDEX_TEMPLATE)

    def __before__(self):
        """Väärtustame self.c.test testiga
        """
        test_id = self.request.matchdict.get('test_id')
        self.c.test = model.Test.get(test_id)

        BaseResourceController.__before__(self)

    def _perm_params(self):
        return {'obj':self.c.test}

