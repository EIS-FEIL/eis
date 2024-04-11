# -*- coding: utf-8 -*- 
# $Id: korraldus.py 406 2016-03-07 19:18:48Z ahti $

from eis.lib.baseresource import *
_ = i18n._

log = logging.getLogger(__name__)

class KorraldusController(BaseResourceController):

    _permission = 'ekk-testid'

    def _perm_params(self):
        return {'obj':model.Test.get(self.request.matchdict.get('test_id'))}
