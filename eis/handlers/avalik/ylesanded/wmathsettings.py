# -*- coding: utf-8 -*- 

from eis.lib.baseresource import *
_ = i18n._
import eis.handlers.ekk.ylesanded.wmathsettings as wmathsettings

log = logging.getLogger(__name__)

class WmathsettingsController(wmathsettings.WmathsettingsController):
    """Lahendaja MathType matemaatikaredaktori seadistamine"""
    _permission = 'avylesanded'
