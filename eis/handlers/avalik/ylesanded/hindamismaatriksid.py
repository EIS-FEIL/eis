# -*- coding: utf-8 -*- 
"Küsimuse hindamismaatriksi kuvamine"
from eis.lib.baseresource import *
_ = i18n._
import eis.handlers.ekk.ylesanded.hindamismaatriksid as hindamismaatriksid
log = logging.getLogger(__name__)

class HindamismaatriksidController(hindamismaatriksid.HindamismaatriksidController):
    _permission = 'avylesanded'
