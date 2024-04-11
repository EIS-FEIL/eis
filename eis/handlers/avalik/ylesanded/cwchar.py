# -*- coding: utf-8 -*- 
"""Ristsõna etteantud tähe salvestamine
"""
from eis.lib.base import *
_ = i18n._
import eis.handlers.ekk.ylesanded.cwchar

log = logging.getLogger(__name__)

class CwcharController(eis.handlers.ekk.ylesanded.cwchar.CwcharController):
    _permission = 'avylesanded'
