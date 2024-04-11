"Avaliku vaate administreerimisliidese valideerimisskeemid"

import formencode
from eis.forms.validators import *

class VolitusForm(Schema):
    isikukood = String(not_empty=True)
    kehtib_kuni = formencode.All(DateValidator(today_or_after=True), 
                                 EstDateConverter(if_missing=None))

class TestitulemusedForm(Schema):
    test_id = Int(if_missing=None)
    alates = EstDateConverter(if_missing=None)
    kuni = EstDateConverter(if_missing=None)
    testsessioon_id = Int(if_missing=None)
    alla = Number(if_missing=None)
    yle = Number(if_missing=None)
    
class KorraldamineForm(Schema):
    alates = EstDateConverter(if_missing=None)
    kuni = EstDateConverter(if_missing=None)
    testsessioon_id = Int(if_missing=None)
    test_id = Int(if_missing=None)
    
class AineprofiilForm(Schema):
    aine_kood = String()
    kasutajagrupp_id = Int()
    
class ProfiilForm(Schema):
    
    f_on_vaatleja = Bool(if_missing=False)
    f_on_testiadmin = Bool(if_missing=False)

    v_skeel = formencode.ForEach(String)
    k_skeel = formencode.ForEach(String)
    s_skeel = formencode.ForEach(String)        
    
    pre_validators = [formencode.NestedVariables()]
    a = formencode.ForEach(AineprofiilForm())    
    
class NousolekForm(Schema):
    toimumisaeg_id = Int()
    on_vaatleja = StringBool(if_missing=None)
    on_hindaja = StringBool(if_missing=None)
    on_intervjueerija = StringBool(if_missing=None)

class NousolekudForm(Schema):
    k_epost = Email(strip=True, max=255)    
    pre_validators = [formencode.NestedVariables()]
    ta = formencode.ForEach(NousolekForm())    

class LepingForm(Schema):
    testsessioon_id = Int()
    leping_id = Int()
    nous = Bool(if_missing=None)
    on_hindaja3 = Bool(if_missing=False)
    
class NousolekudIsikuandmedForm(Schema):
    k_postiindeks = String(max=5)
    k_telefon = String()
    k_epost = Email(strip=True, max=255)        

    p_arveldusarve = String(max=20)
    p_on_psammas = Bool(if_missing=False)
    p_psammas_protsent = Int(if_missing=None)
    p_on_pensionar = Bool(if_missing=False)
    p_on_ravikindlustus = Bool(if_missing=False)    

    # aadress
    a_kood = formencode.ForEach(String)
    a_normimata = String(max=200)

    pre_validators = [formencode.NestedVariables()]
    lep = formencode.ForEach(LepingForm())
   
class MaaramisedForm(Schema):
    testsessioon_id = Int(if_missing=None)
    alates = EstDateConverter(if_missing=None)
    kuni = EstDateConverter(if_missing=None)

class TestiruumForm(Schema):
    id = Int()
    ruum_id = Int(if_missing=None)
    on_sooritajad = Int(if_missing=None)
    toimumispaev_id = Int()
    kell = EstTimeConverter()
    
class KohtYldandmedTestiruumForm(Schema):
    id = Int()
    toimumispaev_id = Int()
    kell = EstTimeConverter(if_missing=None)
    t_lopp = EstTimeConverter(if_missing=None)
    
class KohtYldandmedRuumForm(Schema):
    id = Int()
    tr = formencode.ForEach(KohtYldandmedTestiruumForm())
    uus_ruum_id = Int(if_missing=None)
    
class TestiruumidForm(Schema):
    ruum = formencode.ForEach(KohtYldandmedRuumForm())    

class KSooritajaForm(Schema):
    sooritus_id = Int()
    kuupaev = EstDateConverter(if_missing=None)
    kellaaeg = EstTimeConverter(if_missing=None)
    testiruum_id = Int(if_missing=None)
    
class KSooritajadForm(Schema):
    pre_validators = [formencode.NestedVariables()]
    s = formencode.ForEach(KSooritajaForm())    

class ProtokollAlatestisooritusForm(Schema):
    id = Int()
    staatus = Int(if_missing=None)

class ProtokollSooritusForm(Schema):
    id = Int()
    staatus = Int(if_missing=None)
    markus = String(max=1024, if_missing=None)
    isikudok_nr = String(max=25, if_missing=None)
    pre_validators = [formencode.NestedVariables()]
    ats = formencode.ForEach(ProtokollAlatestisooritusForm())    

class ProtokollLabiviijaForm(Schema):
    id = Int()
    staatus = Int()
    yleaja = Bool(if_missing=None)
    toolopp = EstTimeConverter(if_missing=None)

class ProtokollOsalejadForm(Schema):
    pre_validators = [formencode.NestedVariables()]
    s = formencode.ForEach(ProtokollSooritusForm())    
    lv = formencode.ForEach(ProtokollLabiviijaForm())    
    markus = String(if_missing=None)
    testiruum_id = Int(if_missing=None)
    
class ProtokollYlesandeTulemusegaForm(Schema):
    id = Int
    pallid = Toorpunkt(if_missing=None)
    vy_seq = Int(if_missing=None)
    pre_validators = [formencode.NestedVariables()]

class ProtokollOsalejadYlesandedForm(Schema):
    ty = formencode.ForEach(ProtokollYlesandeTulemusegaForm())    
    pre_validators = [formencode.NestedVariables()]

class ProtokollSooritusTulemusegaForm(Schema):
    id = Int()
    pallid = Toorpunkt()#not_empty=True)
    staatus = Int(if_missing=None)
    pre_validators = [formencode.NestedVariables()]

class ProtokollSooritajaTulemusegaForm(Schema):
    id = Int()
    hinne = Int(if_missing=None)
    markus = String(max=1024, if_missing=None)    
    tos = formencode.ForEach(ProtokollSooritusTulemusegaForm())
    pre_validators = [formencode.NestedVariables()]

class ProtokollOsalejadTulemusegaForm(Schema):
    pre_validators = [formencode.NestedVariables()]
    s = formencode.ForEach(ProtokollSooritajaTulemusegaForm())    
    markus = String(if_missing=None)
    testiruum_id = Int(if_missing=None)
    
class ProtokollOsalejadErivajadusForm(Schema):
    id = Int()
    kasutamata = Bool(if_missing=False)

class ProtokollOsalejadErivajadusedForm(Schema):
    pre_validators = [formencode.NestedVariables()]
    ev = formencode.ForEach(ProtokollOsalejadErivajadusForm())

class ProtokollTurvakottForm(Schema):
    turvakott_id = Int()

class ProtokollTurvakotidForm(Schema):
    pre_validators = [formencode.NestedVariables()]
    tk = formencode.ForEach(ProtokollTurvakottForm())    

class RvtunnistusedForm(Schema):
    rveksam_id = Int(if_missing=None)
    aine = String(if_missing=None)
    isikukood = Isikukood(if_missing=None)
    alates = EstDateConverter(if_missing=None)
    kuni = EstDateConverter(if_missing=None)

    klass = String(if_missing=None)
    paralleel = String(if_missing=None)

class ToofailidForm(Schema):
    "Otsingu vorm"
