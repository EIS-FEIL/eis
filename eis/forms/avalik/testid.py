"Avaliku vaate testide valideerimisskeemid"

import formencode
from eis.forms.validators import *

class OtsingForm(Schema):
    "Otsingu vorm"
    id = Int(if_missing=None, min=1)
    nimi = String(if_missing=None)
    aine = String(if_missing=None)
    staatus = String(if_missing=None)
    skeel = formencode.ForEach(String)    
    testiliik = String(if_missing=None)
    avaldamine = String(if_missing=None)
    pallid = formencode.ForEach(Int)
    piiraeg_alates = Piiraeg(if_missing=None)
    piiraeg_kuni = Piiraeg(if_missing=None)
    
class YldandmedForm(Schema):
    "Üldandmete vorm"
    f_nimi = String(not_empty=True, max=256)
    aine_kood = String(not_empty=True, max=50)
    piiraeg = Piiraeg()
    n_alates = EstDateConverter(if_missing=None)
    n_kuni = EstDateConverter(if_missing=None)
    f_oige_naitamine = Bool(if_missing=False)
    skeel = formencode.ForEach(String)    
    f_ymardamine = Bool(if_missing=False)
    f_arvutihinde_naitamine = Bool(if_missing=False)
    
class TestiylesanneForm(Schema):
    id = Int()
    max_pallid = Number()

class StruktuurForm(Schema):
    order = String()
    ty = formencode.ForEach(TestiylesanneForm())
    f_sooritajajuhend = String(max=1024)
    f_yhesuunaline = Bool
    f_yl_segamini = Bool
    pre_validators = [formencode.NestedVariables()]

class YlesandedForm(Schema):
    id = Int(min=1)
    arvutihinnatav = Bool(if_missing=False)
    st_avalik = Bool(if_missing=False)
    st_pedagoog = Bool(if_missing=False)
    ylkogu_id = Int(if_missing=None)

class OtsiylesandedForm(Schema):
    ylesanne_id = Int(if_missing=None)
    
class IsikForm(Schema):
    pass

class NimekirjadForm(Schema):
    "Otsingu vorm"
    test_id = Int(if_missing=None, min=1)
    nimi = String(if_missing=None, max=100)
    aine = String(if_missing=None, max=10)
    testiliik = String(if_missing=None, max=10)
    reg_aeg_alates = EstDateConverter(if_missing=None)
    reg_aeg_kuni = EstDateConverter(if_missing=None)

    reg_sooritaja = Bool(if_missing=False)
    reg_kool_eis = Bool(if_missing=False)

    staatus = String(if_missing=None)
        
class NimekiriForm(Schema):
    "Testimiskorrale registreerunute nimekirja vorm"
    f_nimi = String(not_empty=True, max=100)
    f_reg_aeg = EstDateConverter()
    reg_aeg_kell = EstTimeConverter()
    f_tahtaeg = EstDateConverter()
    tahtaeg_kell = EstTimeConverter()

class TestinimekiriNimiForm(Schema):
    "Oma testi nimekirja andmete muutmine"
    f_nimi = String(not_empty=True, max=100)
    f_alates = EstDateConverter()
    f_kuni = EstDateConverter(if_missing=False)
    r_kell = EstTimeConverter(if_missing=None)
    r_kell2 = EstTimeConverter(if_missing=None)
    r_lopp = EstTimeConverter(if_missing=None)
    t_lopp = EstTimeConverter(if_missing=None)
    r_on_arvuti_reg = Bool
    r_aja_jargi_alustatav = Bool
    r_algusaja_kontroll = Bool
    n_tulemus_nahtav = Bool
    n_alatestitulemus_nahtav = Bool
    n_vastus_nahtav = Bool
    chained_validators = [Range('f_alates',
                                'f_kuni',
                                'Vahemiku algus ei saa olla peale lõppu'),
                          ]
    
class TestinimekiriForm(Schema):
    "Oma testi nimekirja andmete muutmine"
    f_pedag_nahtav = Bool(if_missing=False)
    
class TestimarkusForm(Schema):
    sisu = String(not_empty=True)

class SooritajaFilterForm(Schema):
    pass

class TestilahendamineForm(Schema):
    pre_validators = [formencode.NestedVariables()]

class KanneForm(Schema):
    pass

class OmanimekirjadForm(Schema):
    "Testiülene nimekirjade otsingu vorm"
    test_id = Int(if_missing=None, min=1)

class PsyhtulemusedForm(Schema):
    "Otsingu vorm"
    isikukood = String(if_missing=None)
    alates = EstDateConverter(if_missing=None)
    kuni = EstDateConverter(if_missing=None)
    
class SaatmisnimekiriForm(Schema):
    "Tulemuste õpilastele saatmise nimekirja vorm"
    klassid_id = formencode.ForEach(String)

class KirjasisuForm(Schema):
    "Tulemuste õpilastele saatmise kirja sisu vorm"
    teema = String(max=256)
    sisu = String
    sooritajad_id = String

class TestinimekirjadForm(Schema):
    "EKK toe otsinguvorm"
    isikukood = String(if_missing=None)
    nimi = String(if_missing=None)
    test_id = Int(if_missing=None, min=1)
    aine = String(if_missing=None)
    
    
