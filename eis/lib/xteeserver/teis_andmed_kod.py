# -*- coding: utf-8 -*- 
"""
Tasemeeksami soorituste ja registreeringute andmete väljastamine riigiportaalis.
Väljastatakse sooritatud eksamite tulemused, avaldatud või kehtetuks tunnistatud tunnistused, registreeringud ja registreeringu testiosade soorituskohad.
"""
from .teis_andmed import teis_andmed_x, model

import logging
log = logging.getLogger(__name__)

def serve(paring, header=None, attachments=[], context=None):
    error = None
    ik = header.userId[2:]
    model.Paring_logi.log(header, paritav=ik)
    return teis_andmed_x(ik)
