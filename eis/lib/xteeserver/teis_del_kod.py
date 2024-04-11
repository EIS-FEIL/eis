"""
Leitakse sisendis antud registreering. Kontrollitakse, et see on sama kasutaja tasemeeksami registreering ning seda on võimalik tühistada. Kui on võimalik tühistada, siis tühistatakse.
"""
from lxml import etree

from eis.lib.pyxadapterlib.xutils import *
from datetime import date

from eis import model
import eiscore.const as const
import eis.lib.helpers as h

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
        error, teade = tyhista(ik, sooritaja_id, const.TESTILIIK_TASE)
    else:
        error = 'Vigane parameeter'

    if error:
        res = E.response(E.teade(error))
    else:
        res = E.response(E.teade(teade))       
    return res, []

def tyhista(ik, sooritaja_id, testiliik):
    error = teade = None
                
    k = model.Kasutaja.get_by_ik(ik)
    if not k:
        error = 'Pole andmeid isiku kohta'
    else:
        sooritaja = model.Sooritaja.get(sooritaja_id)

        if not sooritaja:
            error = 'Registreeringut ei leitud'
        elif sooritaja.kasutaja_id != k.id:
            error = 'Võõras registreering'
        elif sooritaja.test.testiliik_kood != testiliik:
            error = 'Valet testiliik'
        elif sooritaja.staatus == const.S_STAATUS_TYHISTATUD:
            error = 'Registreering on juba tühistatud'
        elif sooritaja.staatus not in (const.S_STAATUS_REGATUD, const.S_STAATUS_TASUMATA, const.S_STAATUS_REGAMATA):
            error = 'Registreeringut ei saa enam tühistada'
        else:
            dt_today = date.today()
            tkord = sooritaja.testimiskord
            if not (tkord.reg_xtee and tkord.reg_xtee_alates<=dt_today and tkord.reg_xtee_kuni>=dt_today):
                error = 'Registreeringut ei saa enam tühistada'            
            else:
                sooritaja.logi_pohjus = 'tühistas ise riigiportaalis'
                sooritaja.tyhista()
                # logi = model.Sooritajalogi(sooritaja=sooritaja,
                #                            staatus=const.S_STAATUS_TYHISTATUD,
                #                            pohjus=u'tühistas ise riigiportaalis')
                model.Session.commit()
                teade = 'Tühistatud'

    return error, teade
