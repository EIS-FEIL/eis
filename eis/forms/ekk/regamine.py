"Registreerimise valideerimisskeemid"

import formencode
from eis.forms.validators import *
import eiscore.const as const

class OtsingForm(Schema):
    isikukood = Isikukood(if_missing=None)
    eesnimi = String(if_missing=None)
    perenimi = String(if_missing=None)
    erivajadused = Bool(if_missing=None)
    lisatingimused = Bool(if_missing=None)
    sessioon_id = Int(if_missing=None)
    testiliik = String(if_missing=None)
    test_id = Int(if_missing=None)
    testimiskord_id = Int(if_missing=None)
    kool_id = Int(if_missing=None)
    reg_alates = EstDateConverter(if_missing=None)
    reg_kuni = EstDateConverter(if_missing=None)
    topelt = Bool
    tasumata = Bool
    tyhistatud = Bool
    regamata = Bool

class MeeldetuletusForm(Schema):
    subject = String(not_empty=True)
    body = String(not_empty=True)
    sooritajad_id = String
    setdef = Bool(if_missing=False)
    
class IsikuvalikForm(Schema):
    isikukood = String()
    synnikpv = EstDateConverter(if_missing=None)
    eesnimi = String(if_missing=None, max=50, strip=True)
    perenimi = String(if_missing=None, max=50, strip=True)

class IsikuandmedForm(Schema):
    k_postiindeks = String(max=5)
    k_telefon = String(max=20)
    k_epost = Email(strip=True, max=255)    
    teavita = formencode.ForEach(String)
    
    # ainult siis, kui EHISes andmeid polnud
    ko_kool_koht_id = Int(if_missing=None)
    ko_kool_nimi = String(max=100, if_missing=None)
    ko_oppekeel = String(if_missing=None)
    ko_lopetamisaasta = Int(min=1950,max=2030, if_missing=None)
    ko_tunnistus_nr = String(if_missing=None)
    ko_tunnistus_kp = EstDateConverter(if_missing=None)

    # aadress
    a_kood = formencode.ForEach(String)
    a_normimata = String(max=200)

class RegavaldusForm(Schema):
    k_postiindeks = String(max=5)
    k_telefon = String(max=20)
    k_epost = Email(strip=True, max=255)        
    teavita = formencode.ForEach(String)
    
    f_tvaldkond_kood = String()
    f_amet_muu = String(max=100)    
    f_haridus_kood = String()
    f_kodakond_kood = String(max=3, if_missing=None)
    k_lisatingimused = String(max=200)
    on_lisatingimused = Bool(if_missing=False)
    
    ko_kool_koht_id = Int(if_missing=None)
    ko_kool_nimi = String(if_missing=None)
    ko_oppekeel = String(if_missing=None)
    ko_lopetamisaasta = Int(min=1920, if_missing=None)
    ko_tunnistus_nr = String(if_missing=None)
    ko_tunnistus_kp = EstDateConverter(if_missing=None)

    ko_lopetanud_kasitsi = Bool()
    ko_lopetanud_pohjus = String(max=100)
    
    f_lang = String()
    f_piirkond_id = Int()
    f_markus = String()
    f_reg_markus = String()
    f_soovib_konsultatsiooni = Bool()

    f_synnikoht_kodakond_kood = String(if_missing=None)
    f_synnikoht = String(if_missing=None, max=100)
    f_eesnimi_ru = NameRus(if_missing=None, max=75)
    f_perenimi_ru = NameRus(if_missing=None, max=75)
    
    # aadress
    a_kood = formencode.ForEach(String)
    a_normimata = String(max=200)

    chained_validators = [NotEmptyIffNotEmpty('on_lisatingimused',
                                              'k_lisatingimused'),
                          ]   

class RegavaldusAvalikForm(Schema):
    k_postiindeks = String(max=5)
    k_telefon = String(max=20)
    k_epost = Email(strip=True, max=255)        
    #k_teatekanal = Int()
    teavita = formencode.ForEach(String)
    
    ko_kool_koht_id = Int(if_missing=None)
    ko_kool_nimi = String(if_missing=None)
    ko_oppekeel = String(if_missing=None)
    ko_lopetamisaasta = Int(min=1920, if_missing=None)
    ko_tunnistus_nr = String(if_missing=None)
    ko_tunnistus_kp = EstDateConverter(if_missing=None)

    ko_lopetanud_kasitsi = Bool()
    ko_lopetanud_pohjus = String(max=100)
    
    # aadress
    a_kood = formencode.ForEach(String)
    a_normimata = String(max=200)


class RahvusvahelisedForm(Schema):
    testiliik = String()
    f_synnikoht_kodakond_kood = String(if_missing=None)
    f_synnikoht = String(if_missing=None, max=100)    
    f_eesnimi_ru = NameRus(if_missing=None, max=75)
    f_perenimi_ru = NameRus(if_missing=None, max=75)
    f_rahvus_kood = String(if_missing=None)

class OppekohtetForm(Schema):
    tmp_kood = String()
    oppekohtet_kood = String(if_missing=False)
    oppekoht_muu = String(if_missing=None, max=100)
    chained_validators = [NotEmptyIffSetTo('oppekohtet_kood',
                                           (const.OPPEKOHTET_KEELTEKOOL, const.OPPEKOHTET_MUU),
                                           'oppekoht_muu'),
                          ]   

class TasemeeksamidForm(Schema):
    testiliik = String()
    oket = formencode.ForEach(OppekohtetForm)
    f_tvaldkond_kood = String()
    f_amet_muu = String(max=100)    
    f_haridus_kood = String()
    
class ErivajadusForm(Schema):
    id = Int()
    taotlus = Bool(if_missing=False)
    taotlus_markus = String(if_missing=None)
    kinnitus = Bool(if_missing=False)
    kinnitus_markus = String(if_missing=None)

class ErivajadusedForm(Schema):
    vaba_osa = Bool(if_missing=None)
    vaba_alatest_id = formencode.ForEach(Int())
    r_kontakt_nimi = String(max=100, not_empty=True)
    r_kontakt_epost = Email(strip=True, max=255, not_empty=True)
    on_erivajadused_vaadatud = Bool(if_missing=False)
    pre_validators = [formencode.NestedVariables()]
    ev = formencode.ForEach(ErivajadusForm())

class ErivajadusedOtsingForm(Schema):
    erivajadus = formencode.ForEach(String)

class NimistusooritajaForm(Schema):
    tk_id = Int()
    s_id = Int(if_missing=None)
    lang = String(if_missing=None)

class NimistukasutajaForm(Schema):
    id = Int()
    tk = formencode.ForEach(NimistusooritajaForm())
    pre_validators = [formencode.NestedVariables()]

class NimistulisavalikudForm(Schema):
    k = formencode.ForEach(NimistukasutajaForm())
    pre_validators = [formencode.NestedVariables()]

class NimistusooritajadTAForm(Schema):
    ta_id = Int
    toimumispaev_id = Int(if_missing=None)
    testikoht_id = Int(if_missing=None)
    kell = EstTimeConverter(if_missing=None)

class NimistusooritajadForm(Schema):
    # ik_fail
    testiliik = String
    cols = formencode.ForEach(String)
    tadata = formencode.ForEach(NimistusooritajadTAForm())

