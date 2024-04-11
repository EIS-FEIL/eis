# -*- coding: utf-8 -*- 

from eis.lib.baseresource import *
import eis.handlers.ekk.ylesanded.taustobjekt as taustobjekt
_ = i18n._

log = logging.getLogger(__name__)

class TaustobjektController(taustobjekt.TaustobjektController):
    """Uue faili salvestamine"""

    _permission = 'avylesanded'
