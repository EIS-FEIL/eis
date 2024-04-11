# -*- coding: utf-8 -*- 
# $Id: isikud.py 406 2016-03-07 19:18:48Z ahti $

from eis.lib.baseresource import *
_ = i18n._
from eis.handlers.admin import isikud
log = logging.getLogger(__name__)

class IsikudController(isikud.IsikudController):
    _permission = 'avalikadmin'

