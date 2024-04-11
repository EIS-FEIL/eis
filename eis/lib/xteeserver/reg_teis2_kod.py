"""
Registreerimisavalduse esitamine riigiportaalis.
Kui andmebaasis pole kasutaja kirjet, siis antakse veateade.
Kontrollitakse, et kasutajal pole juba tasemeeksami registreeringut. Kui on, siis antakse veateade.
Kontrollitakse piirangu olemasolu (millisest ajast alates on tal lubatud uuesti tasemeeksamit sooritada).
Kui kasutaja soovib e-postiga teavitamist, kuid tema e-posti aadressi pole teada, siis antakse veateade.
Kontrollitakse, et oleks valitud täpselt üks keeleoskuse tase ja sellel tasemel üks testimiskord/piirkond.
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
import eis.lib.regpiirang as regpiirang
from eis.lib.xtee.xroad import *

import logging
log = logging.getLogger(__name__)

def serve(paring, header=None, attachments=[], context=None):
    error = teade = None
    handler = context
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
            filter(model.Test.testiliik_kood==const.TESTILIIK_TASE)

        if q.filter(model.Sooritaja.staatus <= const.S_STAATUS_POOLELI).count():
            error = 'Uut avaldust ei saa esitada, kuna olete juba avalduse mõnele eelolevale eksamile esitanud'
        if not error:
            # kontrollime, kas isikul on ajaline piirang järgmise eksami sooritamiseks
            piirang = None
            dt_min, piirang = regpiirang.reg_te_piirang(handler, k.id)

    if not error:
        teateviis = get_text(paring, 'teade')
        if teateviis == '1':
            if not k or not k.epost:
                error = 'Eksamiteate saamisviisiks on valitud e-post, kuid puudub e-posti aadress. Palun klikkige allolevale lingile ja sisestage e-posti aadress või valige eksamiteate saamisviisiks lihtkiri.'
                res.append(E.kontakt(''))

    if not error:
        # vaatame, kuhu soovib end regada
        tase = paring.find('tase')

        tkord_id = piirkond_id = None
        tkoht_s = None
        valitud = False
        for tag in ('a2', 'b1', 'b2', 'c1'):
            node = tase.find(tag)
            if node is not None and get_text(node, 'vali') in ('true', '1'):
                if valitud:
                    error = 'Te ei ole registreeritud, valitud võib olla ainult üks tase!'
                    break
                valitud = True
                tkoht_s = get_text(node,'koht')

        if not valitud:
            error = 'Te ei ole registreeritud, eksamitase on valimata'
        if tkoht_s:
            try:
                testipiirkond_id = tkoht_s.split(':')[0].strip()
                tkord_id, piirkond_id = testipiirkond_id.split('.')
            except:
                tkord_id = piirkond_id = None
        if not tkord_id:
            error = 'Te ei ole registreeritud, aeg/koht valik on tegemata'

    if not error:
        tkord = model.Testimiskord.get(tkord_id)
        if not tkord:
            error = 'Testimiskorda ei leitud'
        elif dt_min and tkord.alates < dt_min:
            error = 'Eksamit ei saa sooritada enne kuupäeva %s (%s)' % (h.str_from_date(dt_min), piirang)
        else:
            # ruumi = [tr.id for tr in tkoht.testiruumid if tr.kohti > tr.sooritajate_arv]
            # if len(ruumi) == 0:
            #     error = u'Valitud soorituskohas ei ole enam ruumi'

            dt_today = date.today()
            if not (tkord.test.testiliik_kood==const.TESTILIIK_TASE and \
                    tkord.reg_xtee and \
                    tkord.reg_xtee_alates<=dt_today and \
                    tkord.reg_xtee_kuni>=dt_today):
                error = 'Sellele testimiskorrale ei saa registreerida'

    if not error:
        ted_tvaldkond_kood = get_text(paring, 'tookoht')
        ted_tvaldkond_muu = get_text(paring, 'tookoht_muu')
        ted_amet_kood = get_text(paring, 'amet')
        ted_amet_muu = get_text(paring, 'amet_muu')
        ted_haridus_kood = get_text(paring, 'haridus')
        if not ted_tvaldkond_kood or ted_tvaldkond_kood == const.TVALDKOND_MUU and not ted_tvaldkond_muu:
            error = 'Te ei ole registreeritud, palun täpsustage töövaldkond'
        elif not ted_amet_kood or ted_amet_kood == const.AMET_MUU and not ted_amet_muu:
            error = 'Te ei ole registreeritud, palun täpsustage amet'
        elif ted_amet_kood and not ted_amet_muu:
            ted_amet_muu = model.Klrida.get_str('AMET', ted_amet_kood)
 
    if not error:
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
            log.debug('added=%s,sooritaja=%s' % (added, sooritaja and sooritaja.id))
            sooritaja.reg_markus = get_text(paring, 'markus')
            sooritaja.soovib_konsultatsiooni = get_text(paring, 'konsult') == '1'

            sooritaja.tvaldkond_kood = ted_tvaldkond_kood
            sooritaja.tvaldkond_muu = ted_tvaldkond_muu
            sooritaja.amet_kood = ted_amet_kood
            sooritaja.amet_muu = ted_amet_muu
            sooritaja.haridus_kood = ted_haridus_kood
            
            model.Session.commit()

            teade = 'Teie registreerimine õnnestus'
            res.append(E.teade(teade))
            res.append(E.edasi(''))

    if error:
        res.append(E.teade(error))

    return res, []

