"Ülesannete valideerimisskeemid"

import formencode
from eis.forms.validators import *
   
class YlesandeaineForm(Schema):
    id = Int
    aine_kood = String(not_empty=True)
    oskus_kood = String()
    teemad2 = formencode.ForEach(String)    
    opitulemused = formencode.ForEach(Int)
    
class YldandmedForm(Schema):
    "Üldandmete vorm"
    f_nimi = String(not_empty=True, max=256)
    f_aste_kood = String()
    v_aste_kood = formencode.ForEach(String)
    f_markus = String()
    f_marksonad = String(max=256)
    pre_validators = [formencode.NestedVariables()]
    vahend_kood = formencode.ForEach(String)
    ya = formencode.ForEach(YlesandeaineForm)

class IsikudForm(Schema):
    isikukood = String
    eesnimi = String
    perenimi = String

class SisuSPForm(Schema):
    "Sisu vorm"
    id = Number
    
class SisuForm(Schema):
    "Sisu vorm"
    f_nimi = String(not_empty=True)
    f_paanide_arv = Int(if_missing=None)
    f_paan1_laius = Int(min=15, max=85)
    f_lahendada_lopuni = Bool(if_missing=False)
    f_valimata_vastused = Bool(if_missing=False)    
    f_spellcheck = Bool(if_missing=False)
    
    f_dlgop = Bool(if_missing=False)
    f_dlgop_aeg = Int(min=5, if_missing=None)
    f_dlgop_tekst = String(max=256, if_missing=None)
    f_dlgop_ei_edasi = Int(if_missing=None)
    sp = formencode.ForEach(SisuSPForm())
    j_juhis = String(if_missing=None)
    
    chained_validators = [NotEmptyIffNotEmpty('f_dlgop', 'f_dlgop_aeg', 'f_dlgop_tekst', 'f_dlgop_ei_edasi')]
    
class EditorsettingForm(Schema):
    icon = formencode.ForEach(String, not_empty=True)

class MathsettingForm(Schema):
    icon = formencode.ForEach(String, not_empty=True)

