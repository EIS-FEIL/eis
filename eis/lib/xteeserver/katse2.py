# -*- coding: utf-8 -*- 
# $Id: katse2.py 9 2015-06-30 06:34:46Z ahti $
"""
Katsetus
"""
from lxml import etree

from eis.lib.pyxadapterlib.xutils import *

import logging
log = logging.getLogger(__name__)

def serve(paring, header=None, attachments=[], context=None):

    ehak = paring.find('asula').text or ''
    res = E.response(E.teade('katse2'),
                 E.asula(ehak))
    return res, []

