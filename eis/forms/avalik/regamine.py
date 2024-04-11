"Registreerimise valideerimisskeemid"

import formencode
from eis.forms.validators import *
import eiscore.const as const

class NimekirjadForm(Schema):
    "Otsingu vorm"
    test_id = Int(if_missing=None, min=1)

class OppekohtetForm(Schema):
    tmp_kood = String()
    oppekohtet_kood = String(if_missing=False)
    oppekoht_muu = String(if_missing=None, max=100)
    chained_validators = [NotEmptyIffSetTo('oppekohtet_kood',
                                           (const.OPPEKOHTET_KEELTEKOOL, const.OPPEKOHTET_MUU),
                                           'oppekoht_muu'),
                          ]   
    
class IsikuandmedForm(Schema):
    k_postiindeks = String(max=5)
    k_telefon = String(max=20)
    k_epost = Email(max=30)
    epost2 = Email(max=30)
    teavita = formencode.ForEach(String)
    
    # aadress
    a_adr_id = Int(if_missing=None)
    a_normimata = String(max=200)
    kk_tvaldkond_kood = String(if_missing=None)
    kk_tvaldkond_muu = String(if_missing=None, max=100)
    kk_amet_muu = String(if_missing=None, max=100)
    kk_haridus_kood = String(if_missing=None)
    oket = formencode.ForEach(OppekohtetForm)
    chained_validators = [MustBeCopy('k_epost', 'epost2')]
    
class OppimineForm(Schema):
    ko_kool_koht_id = Int()
    ko_kool_nimi = String(max=100)
    ko_oppekeel = String()
    ko_lopetamisaasta = Int()
    ko_tunnistus_nr = String(max=25)
    ko_tunnistus_kp = EstDateConverter()

class RahvusvahelisedForm(Schema):
    # rahvusvahelise eksami lisaväljad, vajadusel
    f_synnikoht_kodakond_kood = String(if_missing=None)
    f_synnikoht = String(if_missing=None, max=100)    
    f_eesnimi_ru = NameRus(if_missing=None, max=75)
    f_perenimi_ru = NameRus(if_missing=None, max=75)
    f_rahvus_kood = String(if_missing=None)
    f_rahvus_kood = String(if_missing=None)

class TestForm(Schema):
    id = Int()
    lang = String(if_missing=None)
    piirkond_id = Int(if_missing=None)

class TestidForm(Schema):
    pre_validators = [formencode.NestedVariables()]
    t = formencode.ForEach(TestForm())

class VolitusForm(Schema):
    isikukood = String(not_empty=True)

class ErivajadusForm(Schema):
    id = Int()
    taotlus = Bool(if_missing=False)
    taotlus_markus = String()
    chained_validators = [NotEmptyIfNotEmpty('taotlus', 'taotlus_markus'),]

class ErivajadusedForm(Schema):
    vaba_osa = Bool(if_missing=None)
    vaba_alatest_id = formencode.ForEach(Int())
    r_kontakt_nimi = String(max=100, not_empty=True)
    r_kontakt_epost = Email(strip=True, max=255, not_empty=True)
    pre_validators = [formencode.NestedVariables()]
    ev = formencode.ForEach(ErivajadusForm())

class ErivajadusedOtsingForm(Schema):
    sessioon_id = Int(if_missing=None)
    test_id = Int(if_missing=None)
    aine_kood = String(if_missing=None)
    kinnitatud = Bool(if_missing=False)
    kinnitamata = Bool(if_missing=False)
