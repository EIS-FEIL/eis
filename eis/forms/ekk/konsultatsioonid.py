"Konsultatsioonide valideerimisskeemid"

import formencode
from eis.forms.validators import *

class OtsingForm(Schema):
    "Otsingu vorm"
    id = Int(if_missing=None, min=1)
    
class YldandmedForm(Schema):
    "Üldandmete vorm"
    f_nimi = String(not_empty=True, max=256)
    f_aine_kood = String(not_empty=True, max=10)
    keeletase_kood = String()
    f_testiliik_kood = String()
    f_markus = String()
    
class ToimumispaevForm(Schema):
    kuupaev = EstDateConverter(not_empty=True)
    kell = EstTimeConverter(not_empty=True)
    id = Int()

class KordForm(Schema):
    f_on_mall = Bool
    f_tahis = Alphanum(max=20, not_empty=True)
    f_testsessioon_id = Int()
    tpv = formencode.ForEach(ToimumispaevForm())
    f_nimi = String(max=256)
    # toimumisaja parameetrid
    ta_konsultant_koolituskp = EstDateConverter()
    ta_reg_labiviijaks = Bool()
    ta_ruumide_jaotus = Bool()
    ta_labiviijate_jaotus = Bool()
    ta_konsultant_tasu = Number()
    pre_validators = [formencode.NestedVariables()]
