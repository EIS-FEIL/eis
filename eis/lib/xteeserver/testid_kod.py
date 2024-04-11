"""
Väljastatakse andmed päringu sooritaja osalemise kohta antud testsessiooni testidel. 
Arvestatakse ainult kodakondsusseksamite, tasemeeksamite, põhikooli lõpueksamite, riigieksamite ja rahvusvaheliste tulemusi.
Mõeldud kasutamiseks riigiportaalist ja haridusportaalist.
"""
from eis.lib.pyxadapterlib.xutils import *
from eis import model
import eiscore.const as const
from eis.lib.xtee.xroad import get_ee_user_id, fstr, test_me

def serve(paring, header=None, attachments=[], context=None):
    error = None
    ik = get_ee_user_id(header)
    model.Paring_logi.log(header, paritav=ik)
    k = model.Kasutaja.get_by_ik(ik)
    tunnistus_id = None
    li = []

    if not k:
        error = 'Pole andmeid isiku kohta'
    else:
        try:
            testsessioon_id = int(paring.find('testsessioon_id').text)
            testsessioon = model.Testsessioon.get(testsessioon_id)
            assert testsessioon
        except:
            error = 'Vigane testsessiooni id'
        else:
            li = _search(k.id, testsessioon)
            tunnistus_id = _get_tunnistus_id(k.id, testsessioon)
            if not len(li):
                error = 'Pole andmeid isiku osalemisest antud testsessioonil'

    if error:
        res = E.response(E.teade(error))
    else:
        buf = ''
        res = E.response(E.teade(buf))
        jada = E.testid_kod_jada()
        for item in li:
            jada.append(item)
        res.append(jada)
        if tunnistus_id:
            res.append(E.tunnistus_id(str(tunnistus_id)))

    return res, []

def _search(k_id, testsessioon):
    li = []
    testiliigid = (const.TESTILIIK_POHIKOOL,
                   const.TESTILIIK_RIIGIEKSAM,
                   const.TESTILIIK_RV,
                   const.TESTILIIK_TASE,
                   const.TESTILIIK_SEADUS)
    q = (model.Session.query(model.Sooritaja,
                             model.Test.protsendita,
                             model.Testimiskord.koondtulemus_avaldet,
                             model.Testimiskord.alatestitulemused_avaldet)
         .filter(model.Sooritaja.kasutaja_id==k_id)
         .join(model.Sooritaja.testimiskord)
         .filter(model.Testimiskord.testsessioon_id==testsessioon.id)
         .join(model.Sooritaja.test)
         .filter(model.Test.testiliik_kood.in_(testiliigid))
         .filter(model.Sooritaja.staatus>=const.S_STAATUS_TASUMATA)
         )
    for rcd, protsendita, k_avaldet, a_avaldet in q.all():
        tulemus = ''
        test = rcd.test
        if rcd.staatus == const.S_STAATUS_TEHTUD:
            if rcd.vaie_ettepandud:
                k_avaldet = a_avaldet = False
            if k_avaldet:
                staatus = 'Tulemus on teada'
                tulemus = rcd.get_tulemus(False) or ''
                if tulemus and not protsendita and rcd.max_pallid != rcd.max_osapallid:
                    tulemus += ' (lõpptulemus on antud %s-pallisüsteemis)' % (int(test.max_pallid))
                if rcd.keeletase_kood:
                    tulemus += ', tase %s' % rcd.keeletase_kood
            else:
                staatus = 'Tulemus ei ole teada'
        else:
            k_avaldet = False
            staatus = const.S_STAATUS.get(rcd.staatus)

        item = E.item(E.test_nimi(str(test.nimi)), 
                      E.staatus(staatus or ''),
                      E.tulemus(tulemus))
        li.append(item)

        for r in rcd.get_osasooritused():
            alasooritus, alaosa, tos = r
            if not tos:
                # alatestideta testiosa sooritus
                tos = alasooritus

            kpv = tos.algus or tos.kavaaeg
            kpv = kpv and kpv.strftime('%Y-%m-%d') or ''
            koht = tos.testikoht and tos.testikoht.koht
            if koht and tos.staatus <= const.S_STAATUS_REGATUD and not tos.toimumisaeg.kohad_avalikud:
                # on määratud soorituskohta, kuid see pole veel kindel
                koht = None
            aadress = koht and koht.aadress

            tulemus = ''
            if not alasooritus:
                staatus = tos.staatus_nimi
            elif alasooritus.staatus == const.S_STAATUS_TEHTUD and \
              rcd.staatus != const.S_STAATUS_EEMALDATUD and \
              tos.staatus != const.S_STAATUS_EEMALDATUD:
                # kui sooritaja on eemaldatud, siis ei kuvata ka osade tulemusi ES-3126
                if a_avaldet:
                    staatus = 'Tulemus on teada'
                    tulemus = alasooritus.get_tulemus() or ''
                else:
                    staatus = 'Tulemus ei ole teada'
            else:
                staatus = alasooritus.staatus_nimi

            item2 = E.item(E.osa_nimi(alaosa.nimi),
                           E.osa_kuupaev(kpv),
                           E.osa_koht(koht and koht.nimi or ''),
                           E.osa_aadress(koht and koht.tais_aadress or ''),
                           E.staatus(staatus or ''),
                           E.tulemus(tulemus))
            li.append(item2)

    return li

def _get_tunnistus_id(k_id, testsessioon):
    # kuvame samal sessioonil antud sama liiki tunnistusi
    # kui sessioonile pole testiliiki määratud, siis kuvame riigieksamitunnistusi
    testiliik_kood = testsessioon.testiliik_kood or const.TESTILIIK_RIIGIEKSAM
    q = (model.Tunnistus.query
         .filter(model.Tunnistus.kasutaja_id==k_id)
         .filter(model.Tunnistus.testsessioon_id==testsessioon.id)
         .filter(model.Tunnistus.testiliik_kood==testiliik_kood))
    for rcd in q.all():
        if rcd.staatus == const.N_STAATUS_AVALDATUD:
            return rcd.id
    
if __name__ == '__main__':
    from eis.scripts.scriptuser import *

    # kasuta kujul: python testid_kod.py -admin TEGIJAKOOD sessioon_ID]
    ts_id = noname_args[0]
    paring = E.request(E.testsessioon_id(ts_id))
    test_me(serve, 'testid_kod.v1', paring, named_args)
