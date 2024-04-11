# -*- coding: utf-8 -*- 
# $Id: skannid.py 406 2016-03-07 19:18:48Z ahti $

import os.path
import urllib.request, urllib.parse, urllib.error

from eis.lib.baseresource import *
_ = i18n._
from eis.handlers.avalik.tulemused.skannid import SkannidController

log = logging.getLogger(__name__)

class SkannidController(SkannidController):
    """Skannitud vastuse pildi kuvamine
    """

    def _has_permission(self):
        if not self.c.sooritus:
            return False
        return True
