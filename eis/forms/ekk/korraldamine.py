# -*- coding: utf-8 -*-
"Korraldamise valideerimisskeemid"

import formencode
from eis.forms.validators import *

class ToimumisajadForm(Schema):
    test_id = Int(if_missing=None)
    ta_tahised = String(if_missing=None)
    testsessioon_id = Int(if_missing=None)
    testiliik = String(if_missing=None)
    periood = String(if_missing=None)
    aine = String(if_missing=None)
    alates = EstDateConverter(if_missing=None)
    kuni = EstDateConverter(if_missing=None)
    chained_validators = [Range('alates', 'kuni', 'Vahemiku algus ei saa olla peale lõppu'),
                          ]

class LabiviijadForm(Schema):
    kuupaev = EstDateConverter(if_missing=None)

class KohtProtokollForm(Schema):
    id = Int
    kell = EstTimeConverter
    
class KohtProtokollruumForm(Schema):
    tpr = formencode.ForEach(KohtProtokollForm)
    intervall = Int(if_missing=None)
    paus_algus = EstTimeConverter(if_missing=None)
    paus_lopp = EstTimeConverter(if_missing=None)
    chained_validators = [Range('paus_algus', 'paus_lopp', 'Pausi algus ei saa olla peale lõppu'),
                          ]
    
class ValjastusPDF(Schema):
    ttype = String(if_missing=None)
    tname = String(if_missing=None)
    liik_id = Int()
    avamisaeg = EstTimeConverter(if_missing=None)
    
class ValjastusPDFForm(Schema):
    piirkond_id = Int(if_missing=None)
    testikoht_id = Int(if_missing=None)
    pre_validators = [formencode.NestedVariables()]
    valjastusymbrik = formencode.ForEach(ValjastusPDF())    
    tagastusymbrik = formencode.ForEach(ValjastusPDF())    
    tyhjadeymbrik = formencode.ForEach(ValjastusPDF())    

class LabiviijaMailForm(Schema):
    subject = String(not_empty=True)
    body = String(not_empty=True)

class KohtYldandmedTestiruumForm(Schema):
    id = Int()
    toimumispaev_id = Int()
    kell = EstTimeConverter(if_missing=None)
    t_lopp = EstTimeConverter(if_missing=None)    

class KohtYldandmedRuumForm(Schema):
    id = Int()
    tr = formencode.ForEach(KohtYldandmedTestiruumForm())
    uus_ruum_id = Int(if_missing=None)

class KohtYldandmedForm(Schema):
    ruum = formencode.ForEach(KohtYldandmedRuumForm())    

class KohtSooritajadForm(Schema):
    ttabel = Bool
    intervall = Int(if_missing=20)

    
