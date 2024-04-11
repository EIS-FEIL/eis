# -*- coding: utf-8 -*- 

from eis.lib.baseresource import *
_ = i18n._
import eis.handlers.ekk.ylesanded.mathsettings as mathsettings

log = logging.getLogger(__name__)

class MathsettingsController(mathsettings.MathsettingsController):
    """Lahendaja matemaatikaredaktori seadistamine"""
    _permission = 'avylesanded'
