"""
Teenus väljastab sisendis antud isikukoodidega isikute põhikooli lõpueksamite tulemused.
Väljastatakse tehtud, puudunud, katkestanud ja eemaldatud testisooritused,
kui testimiskorra koondtulemused on avaldatud ja toimumise protokoll on kinnitatud.
Kui samas õppeaines on mitu testisooritust, siis väljastatakse neist üksainus
(parima tulemusega).
"""
from eis.lib.pyxadapterlib.xutils import *
from eis import model
from eis.model import const, sa
import eis.lib.helpers as h
from eis.lib.xtee.xroad import fstr, test_me

def serve(paring, header=None, attachments=[], context=None):
    elem = paring.find('isikukoodid')
    isikukoodid = [r.text for r in elem.findall('isikukood')]
    version = header.service.serviceVersion
    oppurid = _search(isikukoodid, version)

    for ik in isikukoodid:
        model.Paring_logi.log(header, ik)
        
    res = E.response(oppurid)

    return res, []
        
def _search(isikukoodid, version='v2'):
    
    oppurid = E.oppurid()
    if isikukoodid:
        q = (model.Session.query(model.Sooritaja.id,
                                 model.Sooritaja.hinne,
                                 model.Sooritaja.tulemus_protsent,
                                 model.Sooritaja.staatus,
                                 model.Test.aine_kood,
                                 model.Test.pallideta,
                                 model.Test.protsendita,
                                 model.Test.testiliik_kood,
                                 model.Kasutaja.isikukood,
                                 model.Testimiskord.tulemus_kinnitatud,
                                 model.Testimiskord.prot_vorm)
             .join(model.Sooritaja.kasutaja)
             .filter(model.Kasutaja.isikukood.in_(isikukoodid))
             .join(model.Sooritaja.test)
             .filter(model.Test.testiliik_kood==const.TESTILIIK_POHIKOOL)
             .filter(model.Test.eeltest_id==None)
             .join(model.Sooritaja.testimiskord)
             .filter(model.Testimiskord.koondtulemus_avaldet==True)
             .filter(model.Testimiskord.osalemise_naitamine==True)
             )
        if version == 'v1':
            # väljastati ainult tehtud ja hinnatud tööd
            q = (q.filter(model.Sooritaja.staatus==const.S_STAATUS_TEHTUD)
                 .filter(model.Sooritaja.hindamine_staatus==const.H_STAATUS_HINNATUD)
                 .filter(model.Sooritaja.tulemus_protsent != None)
                 )
        elif version == 'v2':
            # väljastatakse kõik tööd, kui protokoll on kinnitatud ES-3599
            staatused = (const.S_STAATUS_TEHTUD,
                         const.S_STAATUS_PUUDUS,
                         const.S_STAATUS_KATKESPROT,
                         const.S_STAATUS_EEMALDATUD)
            q = q.filter(model.Sooritaja.staatus.in_(staatused))
        else:
            raise SoapFault('Server.InvalidVersion', 'Teenuse versiooni viga')
        
        data = {}
        for rcd in q.all():
            j_id, hinne, tulemus_protsent, staatus, aine, pallideta, protsendita, testiliik, isikukood, kinnitatud, prot_vorm = rcd
            if version == 'v2' and not _prot_kinnitatud(j_id, testiliik, prot_vorm):
                # toimumise protokoll pole kinnitatud, ei väljasta andmeid
                continue
            if tulemus_protsent is not None:
                if staatus == const.S_STAATUS_PUUDUS:
                    tulemus_protsent = None
                elif staatus == const.S_STAATUS_EEMALDATUD:
                    tulemus_protsent = 0
                elif staatus != const.S_STAATUS_TEHTUD:
                    tulemus_protsent = 0
            if aine == const.AINE_ET2 and not kinnitatud:
                # eesti keel teise keelena väljastatakse ainult siis, kui tulemused on kinnitatud ES-3115
                continue
            data_ik = data.get(isikukood)
            if not data_ik:
                data_ik = data[isikukood] = {}
            kl_aine = ehis_aine(aine)
            r = data_ik.get(kl_aine)
            if r and (r[1] or 0) > (tulemus_protsent or 0):
                # ei arvesta sama aine nõrgemat tulemust
                continue
            data_ik[kl_aine] = (hinne, tulemus_protsent, staatus)

        for ik, data_ik in data.items():
            oppeained = E.oppeained()
            for kl_aine, r in data_ik.items():
                hinne, tulemus_protsent, staatus = r
                oppeaine = E.oppeaine()
                oppeaine.append(E.kl_aine(kl_aine))
                if hinne is not None:
                    oppeaine.append(E.kl_hinne(hinne))
                if not pallideta and not protsendita and tulemus_protsent is not None:
                    prot = int(round(tulemus_protsent))
                    oppeaine.append(E.osakaal(prot))
                if version == 'v2':
                    sooritamata = staatus != const.S_STAATUS_TEHTUD
                    oppeaine.append(E.sooritamata(sooritamata and 1 or 0))
                oppeained.append(oppeaine)
            oppur = E.oppur(E.isikukood(ik),
                            oppeained)
            oppurid.append(oppur)
    return oppurid

def _prot_kinnitatud(j_id, testiliik, prot_vorm):
    "Kontrollitakse, kas toimumise protokoll on kinnitatud"
    
    def on_tseis(testiliik):
        return testiliik in (const.TESTILIIK_TASE, const.TESTILIIK_SEADUS)
    def on_testikohakaupa(prot_vorm):
        # not testimiskord.prot_tulemusega
        return prot_vorm not in (const.PROT_VORM_TULEMUS, const.PROT_VORM_YLTULEMUS)   
    def on_ruumikaupa(testiliik, prot_vorm):
        # testimiskord.on_ruumiprotokoll
        return on_tseis(testiliik) and not prot_tulemusega(prot_vorm)

    q = (model.Session.query(model.Toimumisprotokoll.staatus)
         .join(model.Sooritaja.sooritused)
         .filter(model.Sooritaja.id==j_id))

    if on_ruumikaupa(testiliik, prot_vorm):
        # testiruumi ja keele kaupa
        q = q.outerjoin((model.Toimumisprotokoll,
                         sa.and_(model.Toimumisprotokoll.testiruum_id==model.Sooritus.testiruum_id,
                                 model.Toimumisprotokoll.testiruum_id!=None,
                                 model.Toimumisprotokoll.lang==model.Sooritaja.lang)
                         ))
             
    elif on_testikohakaupa(prot_vorm):
        # toimumisaja ja koha ja keele kaupa
        q = q.outerjoin((model.Toimumisprotokoll,
                         sa.and_(model.Toimumisprotokoll.testikoht_id==model.Sooritus.testikoht_id,
                                 model.Toimumisprotokoll.lang==model.Sooritaja.lang)
                         ))
    else:
        # testimiskorra ja koha kaupa (tulemusega protokoll)
        # leiame esimese testiosa soorituse
        q1 = (model.Session.query(model.Sooritus.id)
              .filter(model.Sooritus.sooritaja_id==j_id)
              .join(model.Sooritus.testiosa)
              .order_by(model.Testiosa.seq))
        try:
            tos_id = q1.first()[0]
        except IndexError:
            # sooritus puudub
            return False
        # kontrollime esimese testiosa toimumise protokolli
        q = q.filter(model.Sooritus.id==tos_id)
        q = q.outerjoin((model.Toimumisprotokoll,
                         model.Toimumisprotokoll.testikoht_id==model.Sooritus.testikoht_id))
    li = [st for st, in q.all()]
    if not li:
        # toimumisprotokoll puudub
        return False
    for st in li:
        if st not in (const.B_STAATUS_KINNITATUD,
                      const.B_STAATUS_EKK_KINNITATUD):
            # toimumisprotokoll kinnitamata
            return False
    # toimumisprotokollid on olemas ja kinnitatud
    return True

def ehis_aine(kood):
    """Aine klassifikaatori teisendamine
    EH-168 (ee ja vv)
    ES-3120
    EISi klassifikaator:
    A  Ajalugu
    B  Bioloogia
    E  Eesti keel
    R  Eesti keel teise keelena
    ee Emakeel (eesti keel) -> E
    ss Emakeel (saksa keel)
    vv Emakeel (vene keel) -> W
    F  Füüsika
    G  Geograafia
    I  Inglise keel (võõrkeel) -> 17210
    K  Keemia
    kod        Kodakondsus
    M  Matemaatika
    P  Prantsuse keel (võõrkeel) -> 17211
    S  Saksa keel (võõrkeel) -> 17212
    W  Vene keel
    V  Vene keel (võõrkeel) -> W
    C  Ühiskonnaõpetus
    """
    ained = {'ee': 'E',
             'vv': 'W',
             'I': '17210',
             'P': '17211',
             'S': '17212',
             'V': 'W',
             }
    return ained.get(kood) or kood


if __name__ == '__main__':
    from eis.scripts.scriptuser import *

    # kasuta kujul: python pohikooleksamid_ehis.py -admin TEGIJAKOOD IK1,IK2,...,IKN 
    ikd = noname_args[0]
    isikukoodid = E.isikukoodid()
    for ik in ikd.split(','):
        isikukoodid.append(E.isikukood(ik))
    paring = E.request(isikukoodid)
    test_me(serve, 'pohikooleksamid_ehis', paring, named_args, version='v2')    

