"""
Registreerimisvormi andmete alla laadimine riigiportaalis.
Kontrollitakse, et kasutajal juba pole tasemeeksami registreeringut.
Kui kasutajal on piirang, siis leitakse, millisest ajast alates on lubatud uuesti tasemeeksamit sooritada. (Kui isik on eksamilt puudunud või eemaldatud või on saanud alla 35% või pole tulemus veel avaldatud, siis ei saa sooritada enne 6 kuu möödumist, muidu ei saa sooritada enne 1 kuu möödumist viimasest sooritusest.)
Leitakse testimiskorrad, millele on võimalik registreeruda. Leitakse kõigi sobivate testimiskordade kõik piirkonnad ja väljastatakse need keeletasemete kaupa.
"""
from datetime import date
import sqlalchemy as sa
from lxml import etree

from eis.lib.pyxadapterlib.xutils import *
from eis import model
import eiscore.const as const
import eis.lib.helpers as h
import eis.lib.utils as utils
import eis.lib.regpiirang as regpiirang

import logging
log = logging.getLogger(__name__)

def serve(paring, header=None, attachments=[], context=None):
    error = teade = None
    handler = context
    ik = header.userId[2:]
    model.Paring_logi.log(header, paritav=ik)
    dt_min = piirang = None
    res = E.response()                
    k = model.Kasutaja.get_by_ik(ik)
    if k:
        # isik on EISi andmebaasis
        # kontrollime, ega ta juba pole registreeritud
        error = regpiirang.reg_te_piirang1(handler, k.id)
        if not error:
            te_data = k.te_data
            res = E.response(E.nimi(k.nimi),
                             E.tookoht(te_data.tvaldkond_kood or ''),
                             E.tookoht_muu(te_data.tvaldkond_muu or ''),
                             E.amet(te_data.amet_kood or ''),
                             E.amet_muu(te_data.amet_muu or ''),
                             E.haridus2(te_data.haridus_kood or ''))

            ##########################################################
            # kontrollime, kas isikul on ajaline piirang järgmise eksami sooritamiseks
            dt_min, piirang = regpiirang.reg_te_piirang(handler, k.id)
            if piirang:
                piirang = 'Isik ei tohiks eksamit sooritada enne kuupäeva %s (%s)' % (h.str_from_date(dt_min), piirang)
                res.append(E.piirang(piirang))

    if not error:
        #########################################################
        # otsime eesolevaid testimiskordi, kuhu sooritaja saab end regada
        # otsime iga testimiskorra juures kõige esimese toimumisaja testikohad
        dt_today = date.today()
        q = model.Session.query(model.Testimiskord, model.Piirkond).\
            join(model.Testimiskord.test).\
            filter(model.Test.testiliik_kood==const.TESTILIIK_TASE).\
            filter(model.Testimiskord.reg_xtee==True).\
            filter(model.Testimiskord.reg_xtee_alates<=dt_today).\
            filter(model.Testimiskord.reg_xtee_kuni>=dt_today).\
            join(model.Testimiskord.piirkonnad)

        if dt_min:
            # isikul on ajaline piirang
            q = q.filter(model.Testimiskord.alates>=dt_min)

        q = q.order_by(model.Piirkond.nimi, model.Testimiskord.alates)
        plaanid = {}

        for tkord, prk in q.all():
            test = tkord.test
            keeletase_kood = test.keeletase_kood
            millal = tkord.millal
            testipiirkond_id = '%s.%s' % (tkord.id, prk.id)
            item = E.item('%s:%s / %s' % (testipiirkond_id, prk.nimi, millal),
                          label='%s / %s' % (prk.nimi, millal),
                          value=testipiirkond_id)
            if keeletase_kood not in plaanid:
                plaanid[keeletase_kood] = []
            plaanid[keeletase_kood].append(item)

        if not plaanid:
            error = 'Uut avaldust ei saa praegu esitada, eksamiplaane pole tehtud.'
        else:
            # võimalikud testimiskorrad, kuhu saab regada
            for tase in (const.KEELETASE_A2, const.KEELETASE_B1, const.KEELETASE_B2, const.KEELETASE_C1):
                if not plaanid.get(tase):
                    item = E.item('0:eksamikoht puudub',
                                  label='eksamikoht puudub',
                                  value='0')
                    plaanid[tase] = [item]

            def _add_plaan(items, li):
                for r in li:
                    items.append(r)
                return items

            res.append(_add_plaan(E.plaan1(), plaanid.get(const.KEELETASE_A2)))
            res.append(_add_plaan(E.plaan2(), plaanid.get(const.KEELETASE_B1)))
            res.append(_add_plaan(E.plaan3(), plaanid.get(const.KEELETASE_B2)))
            res.append(_add_plaan(E.plaan4(), plaanid.get(const.KEELETASE_C1)))

            res.append(E.edasi(''))
            
    if error:
        res = E.response(E.teade(error))
        if piirang:
            res.append(E.piirang(piirang))

    return res, []

