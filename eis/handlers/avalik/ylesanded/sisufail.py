# -*- coding: utf-8 -*- 

from eis.lib.baseresource import *
_ = i18n._
import eis.handlers.ekk.ylesanded.sisufail as sisufail
log = logging.getLogger(__name__)

class SisufailController(sisufail.SisufailController):
    """Ülesande sisu"""
    _permission = 'avylesanded'
