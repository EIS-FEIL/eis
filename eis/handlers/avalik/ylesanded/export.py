# -*- coding: utf-8 -*- 

from eis.lib.base import *
_ = i18n._
import eis.handlers.ekk.ylesanded.export as export
log = logging.getLogger(__name__)

class ExportController(export.ExportController):
    """Ülesannete eksport.
    """
    _permission = 'avylesanded'
