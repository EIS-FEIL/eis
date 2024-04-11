"""
Teenus otsib sisendiks antud isikukoodiga sooritaja andmeid või kui isikukood pole antud, siis teenuse kasutaja andmeid. Väljastatakse isiku kõigi riigieksamite andmed.

Teenusel on versioonid 1, 2 ja 3.
Versioonis 3 on rahvusvaheliste eksamite tunnistuste juures väli rveksam_kood juhul, kui eksam on seotud rahvusvaheliste eksamite klassifikaatoriga. Versioonides 1 ja 2 seda välja ei esine.
Versioonides 2 ja 3 on kasutusel EISi õppeainete klassifikaator, aga versioonis 1 identifitseeritakse õppeained (õppeaine nimetus ja kood) sõltuvalt ainest kas koodi või nimetuse järgi, vastavalt järgmisele tabelile.

.. table:: Õppeainete klassifikaatorite vastavus
   
   ================= ========================== ========================= ============================================== 
   Aine kood EISis   Õppeaine nimetus           Õppeaine identifikaator   SAISi identifikaatori väärtus                 
   ================= ========================== ========================= ============================================== 
   ee                Emakeel (eesti)            kood                      1                                             
   ----------------- -------------------------- ------------------------- ---------------------------------------------- 
   ss                Emakeel (saksa)            kood                      1                                             
   ----------------- -------------------------- ------------------------- ---------------------------------------------- 
   vv                Emakeel (vane)             kood                      1                                             
   ----------------- -------------------------- ------------------------- ---------------------------------------------- 
   E                 Eesti keel                 kood                      16 – kui eksam on sooritatud 2012 või hiljem  
                                                                          15 - kui eksam on sooritatud 2011 või varem   
   ----------------- -------------------------- ------------------------- ---------------------------------------------- 
   W                 Vene keel                  kood                      17 – kui eksam on sooritatud 2012 või hiljem  
                                                                          13 – kui eksam on sooritatud 2011 või varem   
   ----------------- -------------------------- ------------------------- ---------------------------------------------- 
   R                 Eesti keel teise keelena   nimetus                   eesti keel teise                              
   ----------------- -------------------------- ------------------------- ---------------------------------------------- 
   A                 Ajalugu                    nimetus                   ajalugu                                       
   ----------------- -------------------------- ------------------------- ---------------------------------------------- 
   B                 Bioloogia                  nimetus                   bioloogia                                     
   ----------------- -------------------------- ------------------------- ---------------------------------------------- 
   F                 Füüsika                    nimetus                   füüsika                                       
   ----------------- -------------------------- ------------------------- ---------------------------------------------- 
   G                 Geograafia                 nimetus                   geograafia                                    
   ----------------- -------------------------- ------------------------- ---------------------------------------------- 
   I                 Inglise keel               nimetus                   inglise keel                                  
   ----------------- -------------------------- ------------------------- ---------------------------------------------- 
   K                 Keemia                     nimetus                   keemia                                        
   ----------------- -------------------------- ------------------------- ---------------------------------------------- 
   M                 Matemaatika                nimetus                   matemaatika                                   
   ----------------- -------------------------- ------------------------- ---------------------------------------------- 
   P                 Prantsuse keel             nimetus                   prantsuse keel                                
   ----------------- -------------------------- ------------------------- ---------------------------------------------- 
   S                 Saksa keel                 nimetus                   saksa keel                                    
   ----------------- -------------------------- ------------------------- ---------------------------------------------- 
   V                 Vene keel                  nimetus                   vene keel                                     
   ----------------- -------------------------- ------------------------- ---------------------------------------------- 
   C                 Ühiskonnaõpetus            nimetus                   ühiskonnaõpetus                               
   ================= ========================== ========================= ============================================== 

Kui õppeaine on tabelis ning identifikaatoriks on kood, siis antakse nimetuse väljale aine nimetus EISis. 
Kui õppeaine on tabelis ning identifikaatoriks on nimetus, siis antakse koodi väljal aine kood EISis. 
Kui õppeaine ei ole tabelis, siis kasutatakse väljundis EISi õppeainete klassifikaatori koode ja nimetusi.
"""

from eis.lib.pyxadapterlib.xutils import *
from eis import model
from eis.model import const
import eis.lib.helpers as h
from eis.lib.xtee.xroad import fstr, test_me

def serve(paring, header=None, attachments=[], context=None):
    error = None
    isikukood = paring.find('isikukood').text
    if not isikukood:
        isikukood = header.userId[2:]
    if len(isikukood) != 11:
        error = 'Vigane isikukood'

    # teenuse v1 väljastab ainete koodid ja nimetused iidses SAISi liidese klassifikaatoris
    # teenuse v2 kasutab EISi oma klassifikaatorit
    # teenuse v3 annab väljundis ka elemendi rveksam_kood
    version = header.service.serviceVersion
    use_sais_aine = version == 'v1'
    use_rveksam = version == 'v3'
    if not error:
        model.Paring_logi.log(header, isikukood)
        jada = _search(isikukood, use_sais_aine)
        rvtunnistused = _search_rv(isikukood, context, use_sais_aine, use_rveksam)
        if not len(jada) and not len(rvtunnistused):
            error = 'Andmeid ei leitud'
        # elif handler and handler.is_rpc:
        #     # lisame RPC atribuudid
        #     jada = rpc_array(jada)
        #     rvtunnistused = rpc_array(rvtunnistused)
        
    if error:
        res = E.response(E.teade(error))
    else:
        buf = 'Isikukood: %s' % (isikukood)
        res = E.response(E.teade(buf),
                         jada,
                         rvtunnistused)

    return res, []

def _search(isikukood, use_sais_aine):
    q = (model.Session.query(model.Sooritaja, model.Test)
         .join(model.Sooritaja.kasutaja)
         .filter(model.Kasutaja.isikukood==isikukood)
         .join(model.Sooritaja.test)
         .filter(model.Test.testiliik_kood==const.TESTILIIK_RIIGIEKSAM)
         .filter(model.Test.eeltest_id==None)
         .filter(model.Sooritaja.staatus==const.S_STAATUS_TEHTUD)
         .join(model.Sooritaja.testimiskord)
         .filter(model.Testimiskord.tulemus_kinnitatud==True)
         .filter(model.Testimiskord.koondtulemus_avaldet==True)
         .filter(model.Testimiskord.osalemise_naitamine==True)
         )
    
    # jätame välja need sooritused, mida sama sooritaja on samas aines teinud ja saanud vähem punkte
    sa = model.sa
    Sooritaja2 = sa.orm.aliased(model.Sooritaja)
    Test2 = sa.orm.aliased(model.Test)
    Testimiskord2 = sa.orm.aliased(model.Testimiskord)
    q = q.filter(~ sa.exists().where(sa.and_(Sooritaja2.kasutaja_id==model.Sooritaja.kasutaja_id,
                                             Sooritaja2.test_id==Test2.id,
                                             Test2.testiliik_kood==const.TESTILIIK_RIIGIEKSAM,
                                             Test2.eeltest_id==None,
                                             Test2.aine_kood==model.Test.aine_kood,
                                             Sooritaja2.lang==model.Sooritaja.lang,
                                             Testimiskord2.id==Sooritaja2.testimiskord_id,
                                             Testimiskord2.tulemus_kinnitatud==True,
                                             Testimiskord2.koondtulemus_avaldet==True,
                                             Testimiskord2.osalemise_naitamine==True,
                                             sa.or_(model.Sooritaja.kursus_kood==Sooritaja2.kursus_kood,
                                                    sa.and_(Sooritaja2.kursus_kood==None, model.Sooritaja.kursus_kood==None)),
                                             sa.or_(Sooritaja2.tulemus_protsent>model.Sooritaja.tulemus_protsent,
                                                    sa.and_(Sooritaja2.tulemus_protsent==model.Sooritaja.tulemus_protsent,
                                                            Sooritaja2.id>model.Sooritaja.id))
                                             # sa.or_(Sooritaja2.pallid>model.Sooritaja.pallid,
                                             #        sa.and_(Sooritaja2.pallid==model.Sooritaja.pallid,
                                             #                Sooritaja2.id>model.Sooritaja.id))
                                             )
                                     ))

    q = q.order_by(model.Sooritaja.id)
    li = E.sais_eksam_jada()
    for rcd in q.all():
        sooritaja, test = rcd
        tkord = sooritaja.testimiskord
        if len(sooritaja.sooritused):
            kpv = sooritaja.sooritused[0].algus
        else:
            kpv = None
        
        tunnistus = (model.Tunnistus.query
                     .join(model.Tunnistus.testitunnistused)
                     .filter(model.Testitunnistus.sooritaja_id==sooritaja.id)
                     .filter(model.Tunnistus.staatus==const.N_STAATUS_AVALDATUD)
                     .filter(model.Tunnistus.kasutaja_id==sooritaja.kasutaja_id)
                     .first())
        # if tunnistus and tunnistus.fileext in (const.BDOC, const.ASICE):
        #     ktr = tunnistus.tunnistusekontroll
        #     if not ktr or not ktr.korras:
        #         tunnistus = None
        #         continue

        if use_sais_aine:
            aine_kood, aine_nimi = sais_aine(test.aine_kood, kpv)
        else:
            aine_kood = test.aine_kood
            aine_nimi = test.aine_nimi

        keele_nimetus = sais_keel(sooritaja.lang)

        item = E.item()
        item.append(E.nimetus(aine_nimi))
        item.append(E.kood(aine_kood))

        if sooritaja.kursus_kood:
            item.append(E.kursus(sooritaja.kursus_kood))
        if sooritaja.keeletase_kood:
            item.append(E.keeletase(sooritaja.keeletase_kood))
            
        item.append(E.kuupaev(kpv and kpv.strftime('%d.%m.%Y') or ''))
        #item.append(E.tulemus(h.fstr(sooritaja.pallid) or ''))
        tulemus = sooritaja.tulemus_protsent
        if tulemus is not None:
            tulemus = '%s' % int(round(tulemus))
        item.append(E.tulemus(tulemus or ''))
        item.append(E.keele_kood(sooritaja.lang or ''))
        item.append(E.keele_nimetus(keele_nimetus or ''))
        item.append(E.tunnistuse_nr(tunnistus and tunnistus.tunnistusenr or ''))
        li.append(item)
    return li

def _search_rv(isikukood, handler, use_sais_aine, use_rveksam):
    q = model.Session.query(model.Rvsooritaja, model.Tunnistus, model.Rveksam).\
        join(model.Rvsooritaja.tunnistus).\
        join(model.Tunnistus.kasutaja).\
        filter(model.Kasutaja.isikukood==isikukood).\
        join(model.Rvsooritaja.rveksam)
    q = q.order_by(model.Rvsooritaja.id)

    li = E.rvtunnistused()
    for rcd in q.all():
        rvsooritaja, tunnistus, rveksam = rcd
        rveksamitulemus = rvsooritaja.rveksamitulemus
        rveksam_kood = None
        
        if use_sais_aine:
            aine_kood, aine_nimi = sais_aine(rveksam.aine_kood, None)
        else:
            aine_kood = rveksam.aine_kood
            aine_nimi = rveksam.aine_nimi
            
        item = E.item()
        item.append(E.nimetus(aine_nimi))
        item.append(E.kood(aine_kood))

        kl = rveksam.rveksam
        if use_rveksam and kl:
            item.append(E.tunnistusenimetus(kl.nimi))
            item.append(E.rveksam_kood(kl.kood))
        else:
            item.append(E.tunnistusenimetus(rveksam.nimi))
             
        keeletase = rvsooritaja.keeletase_kood
        if not keeletase and rveksamitulemus:
            keeletase = rveksamitulemus.keeletase_kood
        if keeletase:
            item.append(E.keeletase(keeletase))

        kpv = tunnistus.valjastamisaeg
        if kpv:
            item.append(E.kuupaev(kpv.strftime('%Y-%m-%d')))
        if rvsooritaja.tulemus is not None:
            item.append(E.tulemus(fstr(rvsooritaja.tulemus)))
        item.append(E.tulemusviis(rveksam.tulemusviis))
        if rveksam.kuni is not None:
            item.append(E.max_tulemus(fstr(rveksam.kuni)))
            
        if rveksamitulemus:
            if rveksamitulemus.tahis:
                item.append(E.aste_tahis(rveksamitulemus.tahis))
            if rveksamitulemus.alates is not None:
                item.append(E.aste_alates(fstr(rveksamitulemus.alates)))
            if rveksamitulemus.kuni is not None:
                item.append(E.aste_kuni(fstr(rveksamitulemus.kuni)))

        osatulemused = E.osatulemused()
        for rvs in rvsooritaja.rvsooritused:
            osaoskus = rvs.rvosaoskus
            osatulemus = rvs.rvosatulemus
            oitem = E.item(E.nimetus(osaoskus.nimi))
            if rvs.tulemus is not None:
                oitem.append(E.tulemus(fstr(rvs.tulemus)))
            if osaoskus.kuni is not None:
                oitem.append(E.max_tulemus(fstr(osaoskus.kuni)))
            if osatulemus:
                if osatulemus.tahis:
                    oitem.append(E.aste_tahis(osatulemus.tahis))
                if osatulemus.alates is not None:
                    oitem.append(E.aste_alates(fstr(osatulemus.alates)))
                if osatulemus.kuni is not None:
                    oitem.append(E.aste_kuni(fstr(osatulemus.kuni)))
            osatulemused.append(oitem)
            
        if len(osatulemused):
            # if handler and handler.is_rpc:
            #     # lisame RPC atribuudid
            #     osatulemused = rpc_array(osatulemused)
            item.append(osatulemused)
            
        if tunnistus.tunnistusenr:
            item.append(E.tunnistuse_nr(tunnistus.tunnistusenr))
        li.append(item)

    return li

def sais_aine(kood, kpv):
    """ EISi ja SAISi õppeaine klassifikaatori vastavus.
    Leitakse EISi koodile vastav SAISi kood ja nimetus.
    """
    aine_nimi = None
    if kood in ('ee', 'ss', 'vv'):
        # vana emakeel (eesti, saksa, vene)
        sais_kood = '1'
    elif kood in ('E', 'W'):
        # eesti keel või vene keel
        if kpv and kpv.year < 2012:
            # kirjand, mida sooritati kuni 2011
            sais_kood = kood == 'E' and '15' or '13'
        else:
            # alates 2012
            sais_kood = kood == 'E' and '16' or '17'
    else:
        # ylejäänud aineid tõlgendab SAIS aine nimetuse järgi, võime koodiks panna oma tähe
        sais_kood = kood
        sais_nimetused = {'R': 'eesti keel teise',
                          'A': 'ajalugu',
                          'B': 'bioloogia',
                          'F': 'füüsika',
                          'G': 'geograafia',
                          'I': 'inglise keel',
                          'K': 'keemia',
                          'M': 'matemaatika',
                          'P': 'prantsuse keel',
                          'S': 'saksa keel',
                          'V': 'vene keel',
                          'C': 'ühiskonnaõpetus',
                          }
        aine_nimi = sais_nimetused.get(kood)

    if not aine_nimi:
        aine_nimi = model.Klrida.get_str('AINE', kood).lower()
    return sais_kood, aine_nimi

def sais_keel(lang):
    """EISi keelekoodile vastava SAISi keelenimetuse leidmine
    """
    if lang == const.LANG_ET:
        return 'eesti'
    elif lang == const.LANG_RU:
        return 'vene'
    elif lang:
        nimetus = const.LANG_NIMI.get(lang)
        if nimetus:
            # Inglise keel -> inglise
            return nimetus.split(' ')[0].lower()

if __name__ == '__main__':
    from eis.scripts.scriptuser import *

    # kasuta kujul: python saisEksamid.py -admin TEGIJAKOOD KYSITAVKOOD [-v4 true]
    ik = noname_args[0]
    paring = E.request(E.isikukood(ik))
    #test_me(serve, 'saisEksamid.v1', paring, named_args)
    test_me(serve, 'saisEksamid.v3', paring, named_args)    

