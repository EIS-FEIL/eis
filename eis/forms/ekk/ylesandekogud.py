# -*- coding: utf-8 -*-
"Ülesandekogude valideerimisskeemid"

import formencode
from eis.forms.validators import *
import eiscore.const as const

class OtsingForm(Schema):
    "Otsingu vorm"
    id = Int(if_missing=None, min=1)
    nimi = String(if_missing=None)
    aste = String(if_missing=None)
    klass = String(if_missing=None)
    ainevald = String(if_missing=None)
    aine = String(if_missing=None)
    valdkond = String(if_missing=None)
    keeletase = String(if_missing=None)
    oskus = String(if_missing=None)
    ylesanne_id = Int(if_missing=None, min=1)
    y_alates = Int(if_missing=None, min=0)
    y_kuni = Int(if_missing=None, min=0)
    p_min = Int(if_missing=None, min=0)
    p_max = Int(if_missing=None, min=0)    
    alates = EstDateConverter(if_missing=None)
    kuni = EstDateConverter(if_missing=None)
    staatus = formencode.ForEach(formencode.validators.Int)

    chained_validators = [Range('y_alates',
                                'y_kuni',
                                'Vahemiku lõpp ei saa olla väiksem kui algus'),
                          Range('p_min',
                                'p_max',
                                'Vahemiku lõpp ei saa olla enne algust'),
                          Range('alates',
                                'kuni',
                                'Vahemiku lõpp ei saa olla enne algust'),
                          ]

class KoguteemaForm(Schema):
    id = Int()
    teema_kood = String()
    alateema_kood = String(if_missing=None)
    
class KoguForm(Schema):
    "Üldandmete vorm"
    f_staatus = Int(not_empty=True)
    f_nimi = String(not_empty=True, max=256)
    f_aine_kood = String(not_empty=True)
    f_seotud_ained = formencode.ForEach(String)
    teemad2 = formencode.ForEach(String)
    f_oskus_kood = String(if_missing=None)
    f_keeletase_kood = String(if_missing=None)
    f_ainevald_kood = String
    f_aste_kood = String(not_empty=True)
    f_klass = String
    ek_sisu = String
    kooliastmed = formencode.ForEach(String)
    yt = formencode.ForEach(KoguteemaForm())
    chained_validators = [NotEmptyIffSetTo('f_aine_kood',
                                           (const.AINE_YLD,),
                                           'f_seotud_ained'),
                          ]   

class KogusisuForm(Schema):
    alates = EstDateConverter(if_missing=None)
    kuni = EstDateConverter(if_missing=None)
