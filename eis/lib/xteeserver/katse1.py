# -*- coding: utf-8 -*- 
# $Id: katse1.py 9 2015-06-30 06:34:46Z ahti $
"""
Katsetus
"""
from lxml import etree

from eis.lib.pyxadapterlib.xutils import *

import logging
log = logging.getLogger(__name__)

def serve(paring, header=None, attachments=[], context=None):

    ehak = '2000'
    ehak = '0183'
    res = E.response(E.teade('katse1'),
                 E.asula(ehak))
    return res, []

