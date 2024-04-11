"""
Registreerimisvormi andmete alla laadimine riigiportaalis.
Kontrollitakse, et kasutaja ei ole juba seaduse tundmise eksamit edukalt sooritanud.
Kontrollitakse, et kasutajal juba pole seaduse tundmise eksami registreeringut.
Leitakse testimiskorrad, millele on võimalik registreeruda. Leitakse kõigi sobivate testimiskordade kõik piirkonnad ja väljastatakse need.
Kui isik on Eesti Vabariigi kodanik, siis antakse hoiatus, et eksam pole talle mõeldud.

"""
from datetime import date
from lxml import etree

from eis.lib.pyxadapterlib.xutils import *
from eis import model
import eiscore.const as const

import eis.lib.helpers as h
import eis.lib.utils as utils

import logging
log = logging.getLogger(__name__)

def serve(paring, header=None, attachments=[], context=None):
    error = teade = None
    ik = header.userId[2:]
    model.Paring_logi.log(header, paritav=ik)
    res = E.response()                
    k = model.Kasutaja.get_by_ik(ik)
    if k:
        # isik on EISi andmebaasis
        q = model.Sooritaja.query.\
            filter(model.Sooritaja.kasutaja_id==k.id).\
            filter(model.Sooritaja.staatus > const.S_STAATUS_TYHISTATUD).\
            join(model.Sooritaja.test).\
            filter(model.Test.testiliik_kood==const.TESTILIIK_SEADUS)

        if q.filter(model.Sooritaja.tulemus_piisav==True).count():
            error = 'Olete sooritanud positiivselt Eesti Vabariigi Põhiseaduse ja kodakondsuse seaduse tundmise eksami ning Teile on väljastatud vastav tunnistus. Eksami teistkordne sooritamine ei ole vajalik.'

        if not error:
            if q.filter(model.Sooritaja.staatus <= const.S_STAATUS_POOLELI).count():
                error = 'Uut avaldust ei saa esitada, kuna olete juba avalduse mõnele eelolevale eksamile esitanud'
        if not error:
            te_data = k.te_data
            res = E.response(E.nimi(k.nimi),
                             E.tookoht(te_data.tvaldkond_kood or ''),
                             E.amet(te_data.amet_kood or ''),
                             E.haridus2(te_data.haridus_kood or ''))

    if not error:
        #########################################################
        # otsime eesolevaid testimiskordi, kuhu sooritaja saab end regada

        dt_today = date.today()
        q = model.Session.query(model.Testimiskord, model.Piirkond).\
            join(model.Testimiskord.test).\
            filter(model.Test.testiliik_kood==const.TESTILIIK_SEADUS).\
            filter(model.Testimiskord.reg_xtee==True).\
            filter(model.Testimiskord.reg_xtee_alates<=dt_today).\
            filter(model.Testimiskord.reg_xtee_kuni>=dt_today).\
            join(model.Testimiskord.piirkonnad)

        q = q.order_by(model.Piirkond.nimi, model.Testimiskord.alates)
        plaanid = E.koht()
        for tkord, prk in q.all():
            test = tkord.test
            millal = tkord.millal
            testipiirkond_id = '%s.%s' % (tkord.id, prk.id)
            item = E.item('%s:%s / %s' % (testipiirkond_id, prk.nimi, millal),
                          label='%s / %s' % (prk.nimi, millal),
                          value=testipiirkond_id)
            plaanid.append(item)

        if not len(plaanid):
            error = 'Uut avaldust ei saa praegu esitada, eksamiplaane pole tehtud.'
        else:
            # võimalikud testimiskorrad, kuhu saab regada
            res.append(plaanid)

    if not error:
        if k and k.kodakond_kood == const.RIIK_EST:
            teade = "Rahvastikuregistri andmetel olete Eesti Vabariigi kodanik. Põhiseaduse ja kodakondsuse seaduse tundmise eksam on mõeldud neile, kes soovivad taotleda Eesti kodakondust. Kui soovite siiski jätkata, klikkige 'Edasi'."
            res.append(E.teade(teade))
            res.append(E.edasi_hoiata(''))
            
    if error:
        res = E.response(E.teade(error))
    else:
        res.append(E.edasi(''))

    return res, []

