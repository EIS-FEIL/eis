# -*- coding: utf-8 -*- 
# $Id: lisad.py 406 2016-03-07 19:18:48Z ahti $

from eis.lib.base import *
_ = i18n._

log = logging.getLogger(__name__)

class LisadController(BaseController):
    _permission = 'lahendamine'
    def create(self):
        """POST /admin_ITEMS: Create a new item"""
        log.info("LAHENDAMINE LISAD")
