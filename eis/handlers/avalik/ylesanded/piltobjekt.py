# -*- coding: utf-8 -*- 

from eis.lib.baseresource import *
_ = i18n._
import eis.handlers.ekk.ylesanded.piltobjekt as piltobjekt
log = logging.getLogger(__name__)

class PiltobjektController(piltobjekt.PiltobjektController):
    "Faili salvestamine"
    _permission = 'avylesanded'
