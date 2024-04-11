# -*- coding: utf-8 -*- 
# $Id: otsilabikohad.py 406 2016-03-07 19:18:48Z ahti $

from eis.lib.baseresource import *
_ = i18n._
from eis.lib.basegrid import *
_ = i18n._
from .otsikohad import OtsikohadController

log = logging.getLogger(__name__)

class OtsilabikohadController(OtsikohadController):
    """Soorituskoha otsimine dialoogiaknas, et läbiviija sinna ümber suunata
    """
    _MODEL = model.Testiruum
    _INDEX_TEMPLATE = 'ekk/korraldamine/koht.otsilabikohad.mako'
    _DEFAULT_SORT = 'koht.nimi' # vaikimisi sortimine
    _no_paginate = True
