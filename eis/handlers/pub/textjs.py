# -*- coding: utf-8 -*- 
# $Id: textjs.py 890 2016-09-29 13:46:02Z ahti $
"""Tõlkestringid
"""
from eis.lib.base import *
_ = i18n._
log = logging.getLogger(__name__)

class TextjsController(BaseController):
    _authorize = False

    @action(renderer='/common/eis_textjs.mako')
    def index(self):
        return self.response_dict
