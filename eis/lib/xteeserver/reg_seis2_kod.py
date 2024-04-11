"""
Registreerimisavalduse esitamine riigiportaalis.
Kui andmebaasis pole kasutaja kirjet, siis antakse veateade.
Kontrollitakse, et kasutajal pole juba tasemeeksami registreeringut. Kui on, siis antakse veateade.
Kui kasutaja soovib e-postiga teavitamist, kuid tema e-posti aadressi pole teada, siis antakse veateade.
Kontrollitakse, et valitud testimiskorrale registreerimine on avatud.
Kui kasutajal on piirang, siis kontrollitakse, et piirang ei takista valitud testimiskorral osalemist.
Salvestatakse registreering.
"""
from datetime import date
from lxml import etree

from eis.lib.pyxadapterlib.xutils import *
from eis import model
import eiscore.const as const
import eis.lib.helpers as h
import eis.lib.utils as utils
from eis.lib.xtee.xroad import *

import logging
log = logging.getLogger(__name__)

def serve(paring, header=None, attachments=[], context=None):
    error = teade = None
    ik = header.userId[2:]
    model.Paring_logi.log(header, paritav=ik)
    dt_min = None
    res = E.response()                
    k = model.Kasutaja.get_by_ik(ik)
    if not k:
        error = 'Isikuandmeid ei leitud'        
    else:
        # isik on EISi andmebaasis
        q = model.Sooritaja.query.\
            filter(model.Sooritaja.kasutaja_id==k.id).\
            filter(model.Sooritaja.staatus > const.S_STAATUS_TYHISTATUD).\
            join(model.Sooritaja.test).\
            filter(model.Test.testiliik_kood==const.TESTILIIK_SEADUS)

        if q.filter(model.Sooritaja.staatus <= const.S_STAATUS_POOLELI).count():
            error = 'Uut avaldust ei saa esitada, kuna olete juba avalduse mõnele eelolevale eksamile esitanud'

    if not error:
        teateviis = get_text(paring, 'teade')
        if teateviis == '1':
            if not k or not k.epost:
                error = 'Eksamiteate saamisviisiks on valitud e-post, kuid puudub e-posti aadress. Palun klikkige allolevale lingile ja sisestage e-posti aadress või valige eksamiteate saamisviisiks lihtkiri.'
                res.append(E.kontakt(''))

    if not error:
        tkord = None
        testipiirkond_id = get_text(paring, 'kuu')
        if testipiirkond_id:
            try:
                tkord_id, piirkond_id = testipiirkond_id.split('.')
                tkord = model.Testimiskord.get(tkord_id)
            except:
                tkord = None
        if not tkord:
            error = 'Testimiskorda ei leitud'
        else:
            # ruumi = [tr.id for tr in tkoht.testiruumid if tr.kohti > tr.sooritajate_arv]
            # if len(ruumi) == 0:
            #     error = u'Valitud soorituskohas ei ole enam ruumi'
            dt_today = date.today()
            if not (tkord.test.testiliik_kood==const.TESTILIIK_SEADUS and \
                    tkord.reg_xtee and \
                    tkord.reg_xtee_alates<=dt_today and \
                    tkord.reg_xtee_kuni>=dt_today):
                error = 'Sellele testimiskorrale ei saa registreerida'

    if not error:
        #k.tvaldkond_kood = paring.find('tookoht').text
        #k.amet_kood = paring.find('amet').text
        #k.haridus_kood = paring.find('haridus').text
        added, sooritaja = model.Sooritaja.registreeri(k,
                                                       tkord.test_id,
                                                       tkord,
                                                       const.LANG_ET,
                                                       piirkond_id,
                                                       const.REGVIIS_XTEE,
                                                       k.id,
                                                       None,
                                                       kinnitatud=True)
        if not sooritaja:
            error = 'Teid ei saa sellele testile enam registreerida'
        else:
            sooritaja.reg_markus = get_text(paring, 'markus')
            model.Session.commit()
            res.append(E.teade('Registreerimisavaldus on esitatud'))
            res.append(E.edasi(''))

    if error:
        res.append(E.teade(error))

    return res, []

