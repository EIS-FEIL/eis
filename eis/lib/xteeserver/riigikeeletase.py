# -*- coding: utf-8 -*- 
"""
Teenus maanteeametile riigikeele taseme olemasolu kontrollimiseks

Teenus kontrollib, kas sisendis oleva isikukoodiga isik on kunagi sooritanud tasemeeksami või riigieksami või põhikooli lõpueksami aines „riigikeel“ või „eesti keel teise keelena“, millel saanud sisendis oleva taseme või sellest kõrgema taseme. Kui sooritus leitakse, väljastatakse väljundis „true“ ning isikul on antud keeleoskuse tase olemas. Kui sooritust ei leita, siis ei ole taseme olemasolu teada (mitteametlikult loetakse B1 taseme vääriliseks ka eestikeelse kooli lõpetanud, kuid EIS ei väljasta infot selle kohta, mis keeles kooli on keegi lõpetanud). 
"""
from lxml import etree

from eis.lib.pyxadapterlib.xutils import *
from eis import model
from eis.model import const
from eis.lib.xtee.xroad import fstr, test_me

def serve(paring, header=None, attachments=[], context=None):
    error = None
    isikukood = paring.find('isikukood').text
    if not isikukood or len(isikukood) != 11:
        error = 'Sisendis on vigane isikukood'
    tase = paring.find('tase').text
    tasemed = (const.KEELETASE_A1,
               const.KEELETASE_A2,
               const.KEELETASE_B1,
               const.KEELETASE_B2,
               const.KEELETASE_C1,
               const.KEELETASE_C2)
    if tase not in tasemed:
        error = 'Sisendis on vigane keeleoskuse tase'

    sooritatud = None        
    if not error:
        model.Paring_logi.log(header, isikukood)
        sooritatud = _search(isikukood, tase)
        
    if error:
        res = E.response(E.veateade(error))
    else:
        res = E.response(E.sooritatud(sooritatud))

    return res, []

def _search(isikukood, tase):
    # otsime sooritusi, kus on  tasemeeksamid (aines "riigikeel")
    # ja riigieksamid ja põhikooli lõpueksamid aines "eesti keel teise keelena"
    piisav = _get_piisavad_tasemed(tase)
    q = (model.Session.query(model.Sooritaja.id)
         .join(model.Sooritaja.kasutaja)
         .filter(model.Kasutaja.isikukood==isikukood)
         .join(model.Sooritaja.test)
         .filter(model.Test.testiliik_kood.in_((const.TESTILIIK_TASE,
                                                const.TESTILIIK_RIIGIEKSAM,
                                                const.TESTILIIK_POHIKOOL)))
         .filter(model.Test.aine_kood.in_((const.AINE_ET2, const.AINE_RK)))
         .filter(model.Sooritaja.staatus==const.S_STAATUS_TEHTUD)
         .filter(model.Sooritaja.keeletase_kood.in_(piisav))
         )
    return q.count() > 0 and 'true' or 'false'

def _get_piisavad_tasemed(tase):
    tasemed = (const.KEELETASE_A1,
               const.KEELETASE_A2,
               const.KEELETASE_B1,
               const.KEELETASE_B2,
               const.KEELETASE_C1,
               const.KEELETASE_C2)
    piisav = [r for r in tasemed if r >= tase]
    
    # vanad tasemed:
    # algtase - vastab B1 tasemele
    # kesktase - vastab B2 tasemele
    # kõrgtase - vastab C1 tasemele
    
    if tase <= const.KEELETASE_C1:
        piisav.append(const.KEELETASE_KORG)
        if tase <= const.KEELETASE_B2:
            piisav.append(const.KEELETASE_KESK)
            if tase <= const.KEELETASE_B1:
                piisav.append(const.KEELETASE_ALG)

    return piisav

if __name__ == '__main__':
    from eis.scripts.scriptuser import *
    # kasuta kujul: python riigikeeletase.py -admin TEGIJAKOOD KYSITAVKOOD [-v4 true]
    ik = noname_args[0]
    paring = E.request(E.isikukood(ik), E.tase(const.KEELETASE_B1))
    test_me(serve, 'riigikeeletase.v1', paring, named_args)
