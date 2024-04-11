# -*- coding: utf-8 -*-
# $Id: labiviimine.py 9 2015-06-30 06:34:46Z ahti $
"Testide läbiviimise valideerimisskeemid"

import formencode
from eis.forms.validators import *
    
class NimekirjadForm(Schema):
    "Otsingu vorm"
    test_id = Int(if_missing=None, min=1)
    
class ToimumisajadForm(Schema):
    "Otsingu vorm"
    test_id = Int(if_missing=None, min=1)

class AlatestLisaaegForm(Schema):
    lisaaeg = Piiraeg()
    alatest_id = Int()

class LisaaegForm(Schema):
    "Otsingu vorm"
    tos_lisaaeg = Piiraeg(if_missing=None)
    ats = formencode.ForEach(AlatestLisaaegForm())    
    pre_validators = [formencode.NestedVariables()]

class TestimarkusForm(Schema):
    #teema = String(max=100, not_empty=True)
    sisu = String(not_empty=True)
    #ylem_id = Number()
