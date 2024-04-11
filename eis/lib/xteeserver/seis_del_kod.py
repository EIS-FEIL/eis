"""
Seaduse tundmise eksami registreerimise tühistamine.
Leitakse sisendis antud registreering. Kontrollitakse, et see on sama kasutaja seaduse tundmise eksami registreering ning seda on võimalik tühistada. Kui on võimalik tühistada, siis tühistatakse. 
"""
from lxml import etree

from eis.lib.pyxadapterlib.xutils import *
from eis import model
import eiscore.const as const
import eis.lib.helpers as h
from .teis_del_kod import tyhista

import logging
log = logging.getLogger(__name__)

def serve(paring, header=None, attachments=[], context=None):
    ik = header.userId[2:]
    model.Paring_logi.log(header, paritav=ik)
    try:
        sooritaja_id = int(paring.find('id').text)
    except:
        sooritaja_id = None

    if sooritaja_id:
        error, teade = tyhista(ik, sooritaja_id, const.TESTILIIK_SEADUS)
    else:
        error = 'Vigane parameeter'
        
    if error:
        res = E.response(E.teade(error))
    else:
        res = E.response(E.teade(teade))       
    return res, []
