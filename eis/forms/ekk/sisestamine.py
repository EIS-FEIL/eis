# -*- coding: utf-8 -*-
# $Id: sisestamine.py 9 2015-06-30 06:34:46Z ahti $
"Sisestamise valideerimisskeemid"

import formencode
from eis.forms.validators import *
from eis.model import const

# Hinnete sisestamine

class AspektiHinneForm(Schema):
    toorpunktid = Toorpunkt(if_missing=None) # kui on disabled, siis ei tule
    a_kood = String()

#class KysimuseHinneSeqForm(Schema):
#    toorpunktid = Toorpunkt(if_missing=None) # kui on disabled, siis ei tule

class KysimuseHinneForm(Schema):
    k_id = Int()
    #seq = formencode.ForEach(KysimuseHinneSeqForm()) # kysimusel on mitu vastust
    #pre_validators = [formencode.NestedVariables()]
    toorpunktid = Toorpunkt(if_missing=None) # kui on disabled, siis ei tule

class HindamispaketidForm(Schema):
    "Ümbrike hindajatele väljastamisel hindajate otsimise otsinguvorm"
    filter_extra_fields = True
    # seda skeemi on vaja selleks, et parameeter "kleeps" ei satuks c sisse

    hindamiskogum_id = Int(if_missing=None)
    hindaja_id = Int(if_missing=None)

class TestiylesanneForm(Schema):
    ty_id = Int()
    vy_id = Int()
    vy_seq = Int(if_missing=0)
    toorpunktid = Toorpunkt(if_missing=None) # KASUTATAKSE SIIS, KUI TERVE ÜLESANDE PUNKTID SISESTATAKSE KORRAGA
    ha = formencode.ForEach(AspektiHinneForm()) # kui ylesandel on aspektid   
    k = formencode.ForEach(KysimuseHinneForm()) # kui ylesandel pole aspekte
    pre_validators = [formencode.NestedVariables()]

class HindamineForm(Schema):
    sooritus_id = Int()
    loobun = Bool(if_missing=None)
    komplekt_id = Int()
    labiviija_id = Int()
    kontroll_labiviija_id = Int(if_missing=None)
    intervjuu_labiviija_id = Int(if_missing=None)
    pre_validators = [formencode.NestedVariables()]
    ty = formencode.ForEach(TestiylesanneForm())    

class HindamiskogumForm(Schema):
    pre_validators = [formencode.NestedVariables()]
    hindamiskogum_id = Int()
    hmine = formencode.ForEach(HindamineForm())    
    hmine2 = formencode.ForEach(HindamineForm()) # parandamise korral teise sisestuse andmed    

class HindamisprotokollForm(Schema):
    pre_validators = [formencode.NestedVariables()]
    hk = formencode.ForEach(HindamiskogumForm())    


# kirjaliku p-testi vastuste sisestamine

class VyVastusForm(Schema):
    # soorituse valitudylesande vastuse sisestamine
    # väljade nimedeks on ylesandes esinevate kysimuste koodid
    pre_validators = [formencode.NestedVariables()]

class VastusedTestiylesanneForm(Schema):
    ty_id = Int()
    vy_id = Int()
    vy_seq = Int(if_missing=0)
    toorpunktid = Toorpunkt(if_missing=None) # kui sisestatakse hindepalle
    ha = formencode.ForEach(AspektiHinneForm()) # kui sisestatakse hindepalle   
    k = formencode.ForEach(KysimuseHinneForm()) # kui sisestatakse hindepalle   
    r = VyVastusForm(if_missing={}) # kui sisestatakse vastuseid
    r_error = VyVastusForm(if_missing={}) # sisestuserinevuse vigadest teatamise koha loomise jaoks, kui sisestatakse vastuseid
    pre_validators = [formencode.NestedVariables()]

class VastusedHindamineForm(Schema):
    labiviija_id = Int()
    kontroll_labiviija_id = Int(if_missing=None)
    #intervjuu_labiviija_id = Int(if_missing=None)
    pre_validators = [formencode.NestedVariables()]
    ty = formencode.ForEach(VastusedTestiylesanneForm())    

class VastusedHindamiskogumForm(Schema):
    # soorituse hindamiskogumi vastuste sisestamine
    pre_validators = [formencode.NestedVariables()]
    hindamiskogum_id = Int()
    hmine = VastusedHindamineForm()
    hmine2 = VastusedHindamineForm(if_missing={}) # parandamise korral teise sisestuse andmed        

class VastusedForm(Schema):
    # soorituse hindamiskogumite vastuste sisestamine
    pre_validators = [formencode.NestedVariables()]
    komplekt_id = Int()
    komplekt_id2 = Int(if_missing=None)
    hk = formencode.ForEach(VastusedHindamiskogumForm())        
    
class SkannimineForm(Schema):
    # skannimise laadimise vorm
    kataloog = String(not_empty=True)
    sisestuskogum_id = Int()

class TurvakotidForm(Schema):
    # turvakottide numbrite sisestamine, otsinguvorm
    ta_tahised = String(if_missing=None)
    sessioon_id = Int(if_missing=None)
    test_id = Int(if_missing=None)

class RvtunnistusedForm(Schema):
    # rahvusvahelise tunnistuse sisestamine
    rveksam_id = Int(if_missing=None)
    isikukood = Isikukood(if_missing=None)
    synnikpv = EstDateConverter(if_missing=None)
    eesnimi = String(if_missing=None, max=30)
    perenimi = String(if_missing=None, max=30)
    
class RvsooritusForm(Schema):
    # rahvusvahelise tunnistuse sisestamine
    rvosaoskus_id = Int(not_empty=True)
    tulemus = Number(if_missing=None)
    rvosatulemus_id = Int(if_missing=None)
    on_labinud = Bool(if_missing=None)
    
class RvtunnistusForm(Schema):
    # rahvusvahelise tunnistuse sisestamine

    # olemas ainult uue kirje lisamisel
    rveksam_id = Int(if_missing=None)
    kasutaja_id = Int(if_missing=None)

    sooritaja_id = Int(not_empty=True)
    t_eesnimi = String(max=30, not_empty=True)
    t_perenimi = String(max=30, not_empty=True)
    f_tunnistusenr = String(max=30, if_missing=None)
    t_valjastamisaeg = EstDateConverter(if_missing=None)
    f_kehtib_kuni = EstDateConverter(if_missing=None)
    f_tulemus = Number(if_missing=None)
    f_rveksamitulemus_id = Int(if_missing=None)
    f_arvest_lopetamisel = Bool(if_missing=False)
    osa = formencode.ForEach(RvsooritusForm())

    chained_validators = [Range('t_valjastamisaeg', 'f_kehtib_kuni', 'Vahemiku algus ei saa olla peale lõppu')]
