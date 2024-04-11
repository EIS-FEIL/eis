# -*- coding: utf-8 -*-
"Sisestamise valideerimisskeemid"

import formencode
from eis.forms.validators import *

class LabiviijadForm(Schema):

    testiliik = formencode.ForEach(String)
    sessioon_id = formencode.ForEach(Int)
    testimiskord_id = Int(if_missing=None)
    keeletase = String(if_missing=None)
    test_id = Int(if_missing=None)
    toimumisaeg_id = Int(if_missing=None)
    aine = String(if_missing=None)
    isikukood = Isikukood(if_missing=None)
    eesnimi = String(if_missing=None)
    perenimi = String(if_missing=None)
    alates = EstDateConverter(if_missing=None)
    kuni = EstDateConverter(if_missing=None)
    grupp_id = formencode.ForEach(Int())
    ridu = Int(if_missing=None)
    koikread = Bool(if_missing=False)
    pre_validators = [formencode.NestedVariables()]
    chained_validators = [Range('alates',
                                'kuni',
                                'Vahemiku lõpp ei saa olla enne algust')]

class LabiviijakaskkirjadForm(Schema):

    testiliik = String(if_missing=None)
    sessioon_id = Int(if_missing=None)
    testimiskord_id = Int(if_missing=None)
    keeletase = String(if_missing=None)
    test_id = Int(if_missing=None)
    toimumisaeg_id = Int(if_missing=None)
    aine = String(if_missing=None)
    isikukood = Isikukood(if_missing=None)
    eesnimi = String(if_missing=None)
    perenimi = String(if_missing=None)
    alates = EstDateConverter(if_missing=None)
    kuni = EstDateConverter(if_missing=None)
    #grupp_id = formencode.ForEach(Int())

    labiviijad = Bool(if_missing=False)
    nousolek = Bool(if_missing=False)
    polenous = Bool(if_missing=False)    
    kaskkirjas = Bool(if_missing=False)
    kaskkirikpv = EstDateConverter(if_missing=None)
    leping = Bool(if_missing=False)
    lepingkpv = EstDateConverter(if_missing=None)
    
    pre_validators = [formencode.NestedVariables()]
    chained_validators = [Range('alates',
                                'kuni',
                                'Vahemiku lõpp ei saa olla enne algust')]

class Nousolekud3Form(Schema):
    testiliik = String(if_missing=None)
    sessioon_id = Int(if_missing=None)
    aine = String(if_missing=None)
    pre_validators = [formencode.NestedVariables()]

class VaatlejateatedForm(Schema):

    sessioon_id = Int()
    toimumisaeg_id = Int()
    piirkond_id = Int()
    isikukood = Isikukood()
    eesnimi = String()
    perenimi = String()
    koolitusaeg_alates = EstDateConverter()
    koolitusaeg_kuni = EstDateConverter()
    ltyyp = String()
    kordus = Bool(if_missing=False)

    chained_validators = [Range('koolitusaeg_alates',
                                'koolitusaeg_kuni',
                                'Vahemiku lõpp ei saa olla enne algust')]

class LabiviijateatedForm(Schema):
    testiliik = String(not_empty=True)
    sessioon_id = Int(if_missing=None)
    testimiskord_id = Int(if_missing=None)
    keeletase = String(if_missing=None)
    test_id = Int(if_missing=None)
    toimumisaeg_id = Int(if_missing=None)
    piirkond_id = Int(if_missing=None)
    koht_id = Int(if_missing=None)

    isikukood = Isikukood(if_missing=None)
    eesnimi = String(if_missing=None)
    perenimi = String(if_missing=None)
    grupp_id = Int(if_missing=None)

    ltyyp = String(if_missing=None)
    kordus = Bool(if_missing=False)
    #kaskkirjas = Bool(if_missing=False)
    #kaskkirikpv = EstDateConverter(if_missing=None)
    
class TulemusteteavitusedForm(Schema):
    testiliik = String(not_empty=True)
    sessioon_id = Int(if_missing=None)
    test_id = Int(if_missing=None)
    toimumisaeg_id = Int(if_missing=None)
    piirkond_id = Int(if_missing=None)
    koht_id = Int(if_missing=None)

    isikukood = Isikukood(if_missing=None)
    eesnimi = String(if_missing=None)
    perenimi = String(if_missing=None)

    styyp = String(if_missing=None)
    kordus = Bool(if_missing=False)
    sooritusteated = Bool(if_missing=False)
    mittesooritusteated = Bool(if_missing=False)

class KohateatedForm(Schema):
    testiliik = String(not_empty=True)
    sessioon_id = Int()
    test_id = Int(if_missing=None)
    toimumisaeg_id = Int(if_missing=None)
    piirkond_id = Int(if_missing=None)
    koht_id = Int(if_missing=None)

    isikukood = Isikukood(if_missing=None)
    eesnimi = String(if_missing=None)
    perenimi = String(if_missing=None)

    kordus = Bool(if_missing=False)
    kool = Bool(if_missing=False)
    ise = Bool(if_missing=False)

class TeatedForm(Schema):
    testiliik = String(if_missing=None)
    sessioon_id = Int(if_missing=None)
    testimiskord_id = Int(if_missing=None)
    keeletase = String(if_missing=None)
    test_id = Int(if_missing=None)
    toimumisaeg_id = Int(if_missing=None)
    piirkond_id = Int(if_missing=None)
    koht_id = Int(if_missing=None)

    isikukood = Isikukood(if_missing=None)
    eesnimi = String(if_missing=None)
    perenimi = String(if_missing=None)
    grupp_id = Int(if_missing=None)
    saadetud_alates = EstDateConverter(if_missing=None)
    saadetud_kuni = EstDateConverter(if_missing=None)

    styyp = String(if_missing=None)
    ltyyp = String(if_missing=None)

    #kordus = Bool(if_missing=False)

    chained_validators = [Range('saadetud_alates',
                                'saadetud_kuni',
                                'Vahemiku lõpp ei saa olla enne algust')]

class TeadeSaadaForm(Schema):
    epost = Email(strip=True, max=255, if_missing=None)
    isikukood = Isikukood(if_missing=None)
    k_id = Int()

class TestitulemusedForm(Schema):
    testiliik = String(if_missing=None)
    sessioon_id = Int(if_missing=None)
    test_id = Int(if_missing=None)
    testimiskord_id = Int(if_missing=None)
    erinevus = Number(if_missing=None)
    vrld = String(if_missing=None)

class TulemusedForm(Schema):
    alla = Number(if_missing=None)
    yle = Number(if_missing=None)

class TestisooritusedForm(Schema):
    test_id = Int(if_missing=None)
    sooritus_id = Int(if_missing=None)
    sooritaja_id = Int(if_missing=None)
    kvst_id = Int(if_missing=None)
    vercode = Int(if_missing=None)
    
class RvtunnistusedForm(Schema):
    rveksam_id = Int(if_missing=None)
    aine = String(if_missing=None)
    isikukood = Isikukood(if_missing=None)
    alates = EstDateConverter(if_missing=None)
    kuni = EstDateConverter(if_missing=None)
    sis_alates = EstDateConverter(if_missing=None)
    sis_kuni = EstDateConverter(if_missing=None)

    chained_validators = [Range('alates',
                                'kuni',
                                'Vahemiku lõpp ei saa olla enne algust'),
                          Range('sis_alates',
                                'sis_kuni',
                                'Vahemiku lõpp ei saa olla enne algust')]

class SooritajatearvForm(Schema):
    alates = EstDateConverter(if_missing=None)
    kuni = EstDateConverter(if_missing=None)
    #alates_kell = EstTimeConverter(if_missing=None)
    #kuni_kell = EstTimeConverter(if_missing=None)
    step = Int(if_missing=None)
    chained_validators = [Range('alates',
                                'kuni',
                                'Vahemiku lõpp ei saa olla enne algust')]

class SooritajateolekForm(Schema):
    test_id = Int(if_missing=None)
    kord_tahis = String(if_missing=None)

class KasutajatearvForm(Schema):
    alates = EstDateConverter(if_missing=None)
    kuni = EstDateConverter(if_missing=None)
    step = Int(if_missing=None)
    chained_validators = [Range('alates',
                                'kuni',
                                'Vahemiku lõpp ei saa olla enne algust')]

class PiirkonnatulemusedForm(Schema):
    test_id = Int(if_missing=None)
    alates = EstDateConverter(if_missing=None)
    kuni = EstDateConverter(if_missing=None)
    testsessioon_id = Int(if_missing=None)
    alla = Number(if_missing=None)
    yle = Number(if_missing=None)
    
