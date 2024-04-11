"Sisestamise valideerimisskeemid"

import formencode
from eis.forms.validators import *

class ValjastamineKontrollForm(Schema):
    testiliik = String()
    tunnistuseliik = String()
    sessioon_id = Int(not_empty=True)
    t_name = String()
    isikukood = Isikukood()
    ainultuued = Bool
    
class ValjastamineForm(Schema):
    pohjendus = String()
    ainultuued = Bool(if_missing=False)
    sessioon_id = Int()
    testimiskord_id = Int()
    t_name = String()
    isikukood = Isikukood()

class TyhistamisedForm(Schema):
    tunnistusenr = String(if_missing=None)
    isikukood = Isikukood(if_missing=None)
    
class TyhistamineForm(Schema):
    staatus = Int
    tyh_pohjendus = String(max=255)
    tyh_sooritused = Bool
    
class VaieUusOtsiForm(Schema):
    isikukood = Isikukood(not_empty=True)
    
class VaieKontaktForm(Schema):
    otsus_epostiga = Bool(if_missing=False)
    k_epost = Email(strip=True, max=255)
    k_telefon = String(max=20)
    k_postiindeks = String(max=5)
    a_kood = formencode.ForEach(String)
    a_normimata = String(max=200)
    otsus_epostiga = Bool(if_missing=False)
    
class VaieIsikuvalikForm(Schema):
    isikukood = Isikukood(if_missing=None)
    synnikpv = EstDateConverter(if_missing=None)
    eesnimi = String(if_missing=None, max=50)
    perenimi = String(if_missing=None, max=50)

class VaieUusForm(Schema):
    kasutaja_id = Int
    sooritaja_id = Int
    esitamisaeg = EstDateConverter(not_empty=True)
    otsus_epostiga = Bool(if_missing=False)
    k_epost = Email(strip=True, max=255)
    
    # aadress
    a_kood = formencode.ForEach(String)
    a_normimata = String(max=200)

    # põhjendus
    markus = String(not_empty=True)

class VaidedOtsingForm(Schema):
    sessioon_id = Int(if_missing=None)
    test_id = Int(if_missing=None)
    aine = String(if_missing=None)
    staatus = Int(if_missing=None)
    valjaotsitud = Bool(if_missing=None)
    isikukood = Isikukood(if_missing=None)
    eesnimi = String(if_missing=None)
    perenimi = String(if_missing=None)
    alates = EstDateConverter(if_missing=None)
    kuni = EstDateConverter(if_missing=None)

class VaieForm(Schema):
    otsus_kp = EstDateConverter(if_missing=None)
    otsus_pohjendus = String(if_missing=None)
    arakuulamine_kuni = EstDateConverter(if_missing=None)
    eelnou_pohjendus = String(if_missing=None)
    
class LopetamisedForm(Schema):
    aasta = Int()

class RegkontrollForm(Schema):
    pass

class EttepanekudForm(Schema):
    teema = String(if_missing=None)
    sisu = String(if_missing=None)
    saatja = String(if_missing=None)
    alates = EstDateConverter(if_missing=None)
    kuni = EstDateConverter(if_missing=None)

class EttepanekForm(Schema):
    f_on_vastatud = Bool(if_missing=False)
    f_vastus = String(if_missing=None)

class ToofailidForm(Schema):
    "Otsingu vorm"
    pass

class ToofailForm(Schema):
    "Otsingu vorm"
    f_kirjeldus = String(max=256)
    filename = String(max=256, if_missing=None)
    test_id = Int
    f_oppetase_kood = String
    avalik_kuupaev = EstDateConverter
    avalik_kell = EstTimeConverter

class SkannidTaotlemineForm(Schema):
    kord_id = formencode.ForEach(Int)
    tutv_taotlus_alates = EstDateConverter()
    tutv_taotlus_kuni = EstDateConverter()
    tutv_hindamisjuhend_url = formencode.compound.All(URL, String(max=512))
    alatine = Bool
    chained_validators = [Range('tutv_taotlus_alates',
                                'tutv_taotlus_kuni',
                                'Vahemiku algus ei saa olla peale lõppu')]

class SkannidTellimisedForm(Schema):
    alates = EstDateConverter(if_missing=None)
    kuni = EstDateConverter(if_missing=None)
    isikukood = Isikukood(if_missing=None)
    chained_validators = [Range('alates',
                                'kuni',
                                'Vahemiku algus ei saa olla peale lõppu')]

    
class SkannidTellimineUusForm(Schema):
    sooritus_id = Int(not_empty=True)
    #soovib_p = Bool
    soovib_skanni = Bool
    k_epost = Email(strip=True, max=255, not_empty=True)
    chained_validators = [AnyNotEmpty('soovib_skanni')]
    
class SkannidTellimineUusOtsiForm(Schema):
    isikukood = Isikukood(not_empty=True)

