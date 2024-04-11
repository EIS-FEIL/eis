# -*- coding: utf-8 -*-
"Hindamise valideerimisskeemid"

import formencode
from eis.forms.validators import *

class OtsingForm(Schema):
    "Otsingu vorm"
    test_id = Int(if_missing=None, min=1)
    alates = EstDateConverter(if_missing=None)
    kuni = EstDateConverter(if_missing=None)

class SvastamineOtsingForm(Schema):
    "Otsingu vorm"
    test_id = Int(if_missing=None, min=1)
    alates = EstDateConverter(if_missing=None)
    kuni = EstDateConverter(if_missing=None)

class AspektiHinneForm(Schema):
    # vt forms.ekk.sisestamine
    toorpunktid = Toorpunkt(if_missing=None) # kui on disabled, siis ei tule
    markus = String(if_missing=None)
    nullipohj_kood = String(if_missing=None)    
    a_kood = String()

class KysimuseHinneForm(Schema):
    k_id = Int()
    toorpunktid = Toorpunkt(if_missing=None) 
    markus = String(if_missing=None)
    nullipohj_kood = String(if_missing=None)        

class TestiylesanneForm(Schema):
    # aluseks forms.ekk.sisestamine
    ty_id = Int()
    vy_id = Int()
    vy_seq = Int(if_missing=0)
    toorpunktid = Toorpunkt(if_missing=None) # kasutusel ainult siis, kui antakse terve ylesande punktid korraga
    markus = String(if_missing=None)
    nullipohj_kood = String(if_missing=None)    

    ha = formencode.ForEach(AspektiHinneForm()) # kui ylesandel on aspektid   
    k = formencode.ForEach(KysimuseHinneForm()) # kui ylesandel pole aspekte
    pre_validators = [formencode.NestedVariables()]

class SHindamineForm(Schema):
    pre_validators = [formencode.NestedVariables()]
    ty = formencode.ForEach(TestiylesanneForm())    
    sooritus_id = Int()

class SHindamisedForm(Schema):
    komplekt_id = Int()
    hindamiskogum_id = Int()
    intervjuu_labiviija_id = Int(if_missing=None)
    pre_validators = [formencode.NestedVariables()]
    hmine = formencode.ForEach(SHindamineForm())    
    
class KHindamineForm(Schema):
    pre_validators = [formencode.NestedVariables()]
    ty = formencode.ForEach(TestiylesanneForm())    
    kr = formencode.ForEach(AspektiHinneForm())
    kokku_pallid = Number(if_missing=None)
    ksm_naeb_hindaja = Bool
    ksm_naeb_sooritaja = Bool
    
# Mitme soorituse ühe ülesande hindamine (omaylesanne)
class YTestiylesanneForm(Schema):
    sooritus_id = Int()
    ty = formencode.ForEach(TestiylesanneForm())
    
class YHindamineForm(Schema):
    pre_validators = [formencode.NestedVariables()]
    tos = formencode.ForEach(YTestiylesanneForm())    

# eksamikeskuse vaates eksperthindamise ettepaneku vormid
class HindamiskogumForm(Schema):
    pre_validators = [formencode.NestedVariables()]
    hindamiskogum_id = Int()
    ty = formencode.ForEach(TestiylesanneForm())    

class SooritusForm(Schema):
    pre_validators = [formencode.NestedVariables()]
    sooritus_id = Int()
    hk = formencode.ForEach(HindamiskogumForm())

class EttepanekForm(Schema):
    pre_validators = [formencode.NestedVariables()]
    tos = formencode.ForEach(SooritusForm())
    f_ettepanek_pohjendus = String(if_missing=None)
