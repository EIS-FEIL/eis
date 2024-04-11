"Korraldamise valideerimisskeemid"

import formencode
from eis.forms.validators import *

class OtsingForm(Schema):

    test_id = Int(if_missing=None)
    ta_tahised = String(if_missing=None)
    aine = String(if_missing=None)

    sessioon_id = Int(if_missing=None)
    testiliik = String(if_missing=None)
    periood = String(if_missing=None)

    alates = EstDateConverter(if_missing=None)
    kuni = EstDateConverter(if_missing=None)

class OtsihindajaForm(Schema):
    planeeritud_toode_arv = Int(if_missing=None)
    rangus_alates = Number(if_missing=None)
    rangus_kuni = Number(if_missing=None)
    isikukood = Isikukood(if_missing=None)
    
class EkspertForm(Schema):
    kasutaja_id = Int()
    lv_id = Int()

class EkspertryhmadForm(Schema):
    pre_validators = [formencode.NestedVariables()]
    k = formencode.ForEach(EkspertForm())    

class HindamispohjusForm(Schema):
    hindamispohjus = String(not_empty=True)

class RikkumisotsusForm(Schema):
    on_rikkumine = Bool
    rikkumiskirjeldus = String
    chained_validators = [NotEmptyIffNotEmpty('on_rikkumine',
                                              'rikkumiskirjeldus')]

class AnalyyskoolidForm(Schema):
    testikoht_id = Int()
    kool_koht_id = Int()

class AnalyyskysimusForm(Schema):
    pallid = Number(not_empty=True)

class MootmisveadForm(Schema):
    mootmisviga = Int(min=0)

class SarnasedvastusedForm(Schema):
    testikoht_id = Int()
    testiruum_id = Int()
    komplektivalik_id = Int(if_missing=None)
    komplekt_id = Int(if_missing=None)
    samuvigu = Int(min=0)
    
class KolmandaksForm(Schema):
    protsent = Int(not_empty=True)
    hindamiskogum_id = Int(if_missing=None)
    lang = String(if_missing=None)
    piirkond_id = Int(if_missing=None)

class HindajadForm(Schema):
    hindaja_id = Int(if_missing=None)
    hindamiskogum_id = Int(if_missing=None)
    lang = String(if_missing=None)
    piirkond_id = Int(if_missing=None)
    
class ToovaatajaOtsiForm(Schema):
    eesnimi = String
    perenimi = String
    isikukood = Isikukood

class ToovaatajaForm(Schema):
    kasutaja_id = Int(not_empty=True)
    kehtib_kuni = EstDateConverter(not_empty=True)
