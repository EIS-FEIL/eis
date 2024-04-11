"Administreerimisliidese valideerimisskeemid"

import formencode
from .validators import *
from eis.model import const

class ParoolidForm(Schema):
    "Otsingu vorm"
    isikukood = String(if_missing=None)

class KlassiparoolidForm(Schema):
    "Otsingu vorm"
    klass = String(not_empty=True)
    paralleel = String()

class AmetnikudForm(Schema):
    "Otsingu vorm"
    roll_id = Int(if_missing=None)
    oigus_id = Int(if_missing=None)
    isikukood = String(if_missing=None)
    rollisikukood = String(if_missing=None)
    jira_nr = Int(if_missing=None)
    
class EksaminandidForm(Schema):
    "Otsingu vorm"

class KasutajadForm(Schema):
    "Otsingu vorm"
    isikukood = String(if_missing=None)
    testsessioon_id = Int(if_missing=None)
    test_id = Int(if_missing=None)
    nousolek = Bool(if_missing=None)
    maaratud = Bool(if_missing=None)
    roll_id = Int(if_missing=None)
    kroll_id = Int(if_missing=None)

class KohakasutajadForm(Schema):
    grupp_id = Int(if_missing=None)
    kehtiv = Bool(if_missing=None)
    
class KoolitusedForm(Schema):
    "Koolituste laadimise vorm"
    aine_kood = String(not_empty=True)
    koolitusaeg = EstDateConverter(not_empty=True)
    lang = formencode.ForEach(String)
    kasutajagrupp_id = Int(not_empty=True)
    keeletase = formencode.ForEach(String)

class LabiviijalaadimineForm(Schema):
    "Läbiviijate laadimise vorm"
    kasutajagrupp_id = Int(not_empty=True)

class AmetnikulaadimineForm(Schema):
    "Kasutajate laadimise vorm"
    kasutajagrupp_id = Int(not_empty=True)
    piirkond_id = Int(if_missing=None)
    aine_kood = String(if_missing=None, max=10)
    testiliik_kood = String(if_missing=None)

class KaskkirjadForm(Schema):
    "Käskkirja laadimise vorm"
    aine_kood = String(not_empty=True)
    kaskkirikpv = EstDateConverter(not_empty=True)
    kasutajagrupp_id = Int(not_empty=True)
    keeletase = formencode.ForEach(String)

class EhisoppuridForm(Schema):
    kool_id = Int(if_missing=None)
    #klass = String(not_empty=True)
    klass = String
    testiliik = String
    sessioon_id = Int(if_missing=None)
    test_id = Int(if_missing=None)
    #testimiskord_id = Int(if_missing=None)
    
class EhisopetajadForm(Schema):
    kool_id = Int
    aine = String
    aste = String
       
class AmetnikurollForm(Schema):
    r_kasutajagrupp_id = Int(if_missing=const.MISSING)
    r_piirkond_id = Int(if_missing=None)
    r_ained = formencode.ForEach(String)
    r_aine_kood = String(if_missing=None, max=10)
    r_oskus_kood = String(if_missing=None, max=10)
    r_kehtib_kuni = EstDateConverter()
    r_allkiri_jrk = Int(if_missing=None)
    r_allkiri_tiitel1 = String(if_missing=None, max=60)
    r_allkiri_tiitel2 = String(if_missing=None, max=60)
    koht_id = Int(if_missing=None)
    jira_nr = Int(min=100)
    selgitus = String(strip=True)
    chained_validators = [AnyNotEmpty('jira_nr', 'selgitus'),
                          ]

class KasutajarollForm(Schema):
    koht_id = Int(not_empty=True)
    kehtib_kuni = EstDateConverter()
    kasutajagrupp_id = Int()
    
# soorituskoha administraatori kehtivusaja muutmiseks
class KehtibkuniForm(Schema):
    kehtib_kuni = EstDateConverter()

class KasutajakohtForm(Schema):
    koht_id = Int(not_empty=True)
    kehtib_kuni = EstDateConverter
    
class KoharollForm(Schema):
    kasutajagrupp_id = Int()
    kehtib_kuni = EstDateConverter

class KasutajaForm(Schema):
    k_eesnimi = String(max=50, not_empty=True)
    k_perenimi = String(max=50, not_empty=True)
    isikukood = String(max=48)
    k_synnikpv = EstDateConverter(not_empty=True)
    k_sugu = String(not_empty=True)
    parool = String(if_missing=None)
    k_markus = String()
    k_on_labiviija = Bool(if_missing=False)
    k_postiindeks = String(max=5)
    k_telefon = String(max=20)
    k_epost = Email(strip=True, max=255)

    p_arveldusarve = String(max=20)
    p_on_psammas = Bool(if_missing=False)
    p_psammas_protsent = Int(if_missing=None)
    p_on_pensionar = Bool(if_missing=False)
    p_on_ravikindlustus = Bool(if_missing=False)
    
    # aadress
    a_kood = formencode.ForEach(String)
    a_normimata = String(max=200)

class AineprofiilForm(Schema):

    aine_kood = String()
    kasutajagrupp_id = Int()
    keeletase_kood = String(if_missing=None)
    rangus = Number(if_missing=None)
    halve = Number(if_missing=None)
    koolitusaeg = EstDateConverter(if_missing=None)
    kaskkirikpv = EstDateConverter(if_missing=None)

class ProfiilForm(Schema):
    k_epost = Email(strip=True, max=255, if_missing=None) # avalikus vaates kasutusel
    
    f_on_vaatleja = Bool(if_missing=False)
    f_on_testiadmin = Bool(if_missing=False)
    f_v_koolitusaeg = EstDateConverter(if_missing=None)
    f_v_kaskkirikpv = EstDateConverter(if_missing=None)
    
    skeel = formencode.ForEach(String)
    v_skeel = formencode.ForEach(String)
    k_skeel = formencode.ForEach(String)
    s_skeel = formencode.ForEach(String)    

    f_markus = String(if_missing=None)

    pre_validators = [formencode.NestedVariables()]
    a = formencode.ForEach(AineprofiilForm())    

class KasutajaajaluguForm(Schema):
    testsessioon_id = Int()
    alates = EstDateConverter()
    kuni = EstDateConverter()

class AmetnikForm(Schema):
    k_eesnimi = String(max=50, not_empty=True, strip=True)
    k_perenimi = String(max=50, not_empty=True, strip=True)
    isikukood = String(max=48, strip=True)
    k_synnikpv = EstDateConverter(not_empty=True)    
    k_sugu = String
    parool = String(if_missing=None, strip=True)
    k_epost = Email(strip=True, max=255)

class EksaminandForm(Schema):

    k_eesnimi = String(max=50, not_empty=True, strip=True)
    k_perenimi = String(max=50, not_empty=True, strip=True)
    isikukood = String(max=48, if_missing=None, strip=True)
    k_synnikpv = EstDateConverter(not_empty=True)
    k_sugu = String
    
    # aadress
    a_kood = formencode.ForEach(String)
    a_normimata = String(max=200)

    k_postiindeks = String(max=5)
    k_telefon = String(max=20)
    k_epost = Email(strip=True, max=255)
    teavita = formencode.ForEach(String)

    kodakond_kood = String(max=3, if_missing=None)
    k_lisatingimused = String()
    on_lisatingimused = Bool(if_missing=False)
   
    # ainult siis, kui EHISes andmeid polnud
    ko_kool_koht_id = Int(if_missing=None)
    ko_kool_nimi = String(max=100, if_missing=None)
    ko_oppekeel = String(if_missing=None)
    ko_lopetamisaasta = Int(min=1950,max=2030, if_missing=None)
    ko_tunnistus_nr = String(if_missing=None)
    ko_tunnistus_kp = EstDateConverter(if_missing=None)
    ko_lopetanud_kasitsi = Bool()
    ko_lopetanud_pohjus = String(max=100)
    k_markus = String()

    chained_validators = [NotEmptyIffNotEmpty('on_lisatingimused',
                                              'k_lisatingimused'),
                          ]   

class KasutajagruppOigusForm(Schema):
    oigus_id = Int()
    b_index = Int(if_missing=0)
    b_show = Int(if_missing=0)
    b_create = Int(if_missing=0)
    b_update = Int(if_missing=0)

class KasutajagruppForm(Schema):
    f_nimi = String(max=50, not_empty=True)
    f_tyyp = Int()
    pre_validators = [formencode.NestedVariables()]
    o = formencode.ForEach(KasutajagruppOigusForm())

class LogiForm(Schema):
    id = Int(if_missing=None)
    idr = IDRange(if_missing=None)
    isikukood = String(if_missing=None)
    alates = EstDateConverter(today_or_before=True, if_missing=None)
    kuni = EstDateConverter(today_or_before=True, if_missing=None)
    ylesanne_id = Int(if_missing=None)
    chained_validators = [DateRange('alates',
                                    'kuni')
                          ]

class LogiadapterForm(Schema):
    id = Int(if_missing=None)
    alates = EstDateConverter(today_or_before=True, if_missing=None)
    kuni = EstDateConverter(today_or_before=True, if_missing=None)
    chained_validators = [DateRange('alates',
                                    'kuni')
                          ]

class AbivahendForm(Schema):
    f_kood = String(max=10, if_missing=None)
    f_nimi = String(not_empty=True, max=100)
    f_kehtib = Bool()
    f_jrk = Int()
    f_kirjeldus = String()
    f_laius = Int
    f_korgus = Int
    f_pais = String
    f_ikoon_url = String(max=100)

class TranAbivahendForm(Schema):
    f_nimi = String(not_empty=True, max=100)
    f_kirjeldus = String()
    f_pais = String
    
class KlridaForm(Schema):
    id = Int()
    kood = String(max=10, if_missing=None)
    kood2 = String(max=2, if_missing=None)
    nimi = String(not_empty=True, max=100)
    kehtib = Bool()
    jrk = Int()
    level = Int(if_missing=None)
    bit = formencode.ForEach(Int)
    kinnituseta = Bool
    
# class KlridaKirjeldusForm(Schema):
#     f_kirjeldus = String()
#     f_laius = Int(if_missing=None)
#     f_korgus = Int(if_missing=None)    
#     f_pais = String(if_missing=None)
#     f_ikoon_url = String(if_missing=None, max=100)
    
class KlassifikaatorForm(Schema):
    f_nimi = String(not_empty=True, max=100)
    f_kehtib = Bool()
    ylem_kood = String(if_missing=None)

    pre_validators = [formencode.NestedVariables()]
    k = formencode.ForEach(KlridaForm())    

class TKlridaForm(Schema):
    id = Int()
    nimi = String(max=100)

class TKlridaKirjeldusForm(Schema):
    f_kirjeldus = String()
    f_pais = String(if_missing=None)

class TKlassifikaatorForm(Schema):
    f_nimi = String(max=100)
    ylem_kood = String(if_missing=None)
    pre_validators = [formencode.NestedVariables()]
    k = formencode.ForEach(TKlridaForm())    

class KlridaEHISForm(Schema):
    id = Int()
    kood = String(max=25, if_missing=None)
    nimi = String(not_empty=True, max=100)
    kehtib = Bool()
    jrk = Int()

class KlassifikaatorEHISForm(Schema):
    f_nimi = String(not_empty=True, max=100)
    f_kehtib = Bool()
    ylem_kood = String(if_missing=None)

    pre_validators = [formencode.NestedVariables()]
    k = formencode.ForEach(KlridaEHISForm())    

class KlvastavusForm(Schema):
    id = Int
    vaste_id = formencode.ForEach(Int)
    
class KlvastavusedForm(Schema):
    pre_validators = [formencode.NestedVariables()]
    klv = formencode.ForEach(KlvastavusForm())    

class PiirkonnadForm(Schema):
    "Otsingu vorm"

class PiirkondForm(Schema):
    "Otsingu vorm"

class KohadForm(Schema):
    "Otsingu vorm"
    kool_id = Int(if_missing=None)
    nimi = String(if_missing=None)
    maakond_kood = String(if_missing=None)
    piirkond = Int(if_missing=None)

class KohadMailForm(Schema):
    subject = String(not_empty=True)
    body = String(not_empty=True)
    to = formencode.ForEach(String())

class KohalogiForm(Schema):
    koht_id = Int(if_missing=None)
    koht_nimi = String(if_missing=None)
    muutja_nimi = String(if_missing=None)
    allikas = Int(if_missing=None)
    alates = EstDateConverter(today_or_before=True, if_missing=None)
    kuni = EstDateConverter(today_or_before=True, if_missing=None)
    chained_validators = [DateRange('alates',
                                    'kuni')
                          ]

class KohtForm(Schema):
    "Koha andmete vorm"
    f_nimi = String(not_empty=True, max=100)
    on_soorituskoht = Bool()
    f_piirkond_id = Int(if_missing=None)
    f_postiindeks = String(max=5)
    f_telefon = String(max=20)
    f_epost = Email(strip=True, max=255)
    f_varustus = String(max=512)
    f_klassi_kompl_arv = Int(if_missing=None)
    f_opilased_arv = Int(if_missing=None)
    f_alamliik_kood = String(if_missing=None)
    
    # aadress
    a_kood = formencode.ForEach(String)
    a_normimata = String(max=200)

class OppekavaForm(Schema):
    oppetase_kood = String(not_empty=True)
    kavatase_kood = String(not_empty=True)

class RuumForm(Schema):
    tahis = String(not_empty=True, max=20)
    ptestikohti = Int()
    etestikohti = Int()
    staatus = Int(if_missing=0)
    varustus = String(max=512)

class RuumidForm(Schema):
    f_ruumidearv = Int()
    f_ptestikohti = Int()
    f_etestikohti = Int()
    pre_validators = [formencode.NestedVariables()]
    r = formencode.ForEach(RuumForm())    

class KoharollForm(Schema):
    kasutajagrupp_id = Int(if_missing=const.MISSING)
    kehtib_kuni = EstDateConverter()

class TestsessioonForm(Schema):
    f_nimi = String(max=100, not_empty=True)
    f_vaide_tahtaeg = EstDateConverter()
    f_testiliik_kood = String()
    f_seq = Int()
    f_oppeaasta = Int(min=1990, max=2099, not_empty=True)
    f_vaikimisi = Bool

class KiirvalikForm(Schema):
    f_testiliik_kood = String(not_empty=True)
    f_nimi = String(not_empty=True, max=100)
    f_staatus = Int(if_missing=0)
    f_selgitus = String(max=1024)

class NousolekForm(Schema):
    toimumisaeg_id = Int()
    on_vaatleja = Bool(if_missing=False)
    on_hindaja = Bool(if_missing=False)
    on_intervjueerija = Bool(if_missing=False)

class NousolekudForm(Schema):
    pre_validators = [formencode.NestedVariables()]
    ta = formencode.ForEach(NousolekForm())    

class KasutajagrupidForm(Schema):
    pre_validators = [formencode.NestedVariables()]
    o = formencode.ForEach(KasutajagruppForm())    

class AsukohamaarusRowForm(Schema):
    id = Int()
    nimetav = String(max=30, not_empty=True)
    kohamaarus = String(max=30, not_empty=True)    

class AsukohamaarusForm(Schema):
    pre_validators = [formencode.NestedVariables()]
    r = formencode.ForEach(AsukohamaarusRowForm())    

class OlulineinfoForm(Schema):
    sisu2 = String(strip=True, if_missing=None)

class AvaleheteadeForm(Schema):
    f_pealkiri = String(max=100, not_empty=True)
    f_sisu = String(not_empty=True)
    f_lisasisu = String()
    f_tyyp = Int(not_empty=True)
    kellele = AtLeastOne(String)
    f_alates = EstDateConverter(not_empty=True)
    f_kuni = EstDateConverter()
    chained_validators = [Range('f_alates', 'f_kuni', 'Vahemiku algus ei saa olla peale lõppu')]    

class AvalehepiltForm(Schema):
    f_autor = String(max=200)
    f_allikas= String(max=200)
    f_alates = EstDateConverter(not_empty=True)
    f_kuni = EstDateConverter()
    kuni_vaja = String
    chained_validators = [Range('f_alates', 'f_kuni', 'Vahemiku algus ei saa olla peale lõppu'),
                          NotEmptyIffNotEmpty('kuni_vaja', 'f_kuni'),
                          ]
    
class RveksamitulemusForm(Schema):
    keeletase_kood = String()
    id = Int()
    tahis = String(max=30)
    alates = Number()
    kuni = Number()
    chained_validators = [Range('alates', 'kuni', 'Vahemiku algus ei saa olla peale lõppu')]
                          
class RvosatulemusForm(Schema):
    id = Int()
    tahis = String(max=30)
    alates = Number()
    kuni = Number()
    chained_validators = [Range('alates', 'kuni', 'Vahemiku algus ei saa olla peale lõppu')]
                          
class RvosaoskusForm(Schema):
    id = Int()
    nimi = String(max=256, not_empty=True)
    tulemus = formencode.ForEach(RvosatulemusForm())
    alates = Number()
    kuni = Number()
    chained_validators = [Range('alates', 'kuni', 'Vahemiku algus ei saa olla peale lõppu')]
    
class RveksamForm(Schema):
    f_nimi = String(max=256, not_empty=True)
    f_aine_kood = String(not_empty=True)
    f_tulemusviis = String(max=1, not_empty=True)
    tulemus = formencode.ForEach(RveksamitulemusForm())
    osa = formencode.ForEach(RvosaoskusForm())
    f_keeletase_kood = String()
    f_vastab_tasemele = StringBool()
    f_on_tase_tunnistusel = Bool()
    f_on_tulemus_tunnistusel = Bool()
    f_on_tulemus_sooritusteatel = Bool()
    f_on_osaoskused_tunnistusel = Bool()
    f_on_osaoskused_sooritusteatel = Bool()
    f_on_osaoskused_jahei = Bool()
    f_on_kehtivusaeg = Bool()
    f_on_tunnistusenr = Bool()
    f_alates = Number()
    f_kuni = Number()
    f_markus = String()
    f_kantav_tulem = Bool
    chained_validators = [Range('f_alates', 'f_kuni', 'Vahemiku algus ei saa olla peale lõppu')]

class LepingurollForm(Schema):
    id = Int
    kasutajagrupp_id = Int
    aine_kood = String
    testiliik_kood = String
    
class LepingForm(Schema):
    f_nimetus = String(not_empty=True)
    f_url = URL(max=512, not_empty=True)
    f_yldleping = Bool
    f_sessioonita = Bool
    f_aasta_alates = Int
    f_aasta_kuni = Int
    f_testsessioon_id = Int
    lr = formencode.ForEach(LepingurollForm())
    
class KlasterForm(Schema):
    f_int_host = String(max=50, not_empty=True)
    f_staatus = Int
