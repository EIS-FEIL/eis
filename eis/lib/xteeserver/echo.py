# -*- coding: utf-8 -*- 
# $Id: echo.py 9 2015-06-30 06:34:46Z ahti $

from lxml import etree

from eis.lib.pyxadapterlib.xutils import *

def serve(paring, header=None, attachments=[], context=None):
    res = E.response(E.vuu('3'),
                 E.ahaa('seeh'),
                 E.ahaa('vohoo'))
    return res, []
