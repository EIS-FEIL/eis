# -*- coding: utf-8 -*- 
"""
Riigiportaali autenditud kasutaja suunamine EISi riigieksamitele registreerimise vormile. Teenusega genereeritakse EISis unikaalne ühekordselt kasutatav URL, mis seotakse teenuse kasutaja identiteediga. Riigiportaal suunab kasutaja sellele URLile, EIS loeb kasutaja autendituks ilma täiendava sisse logimiseta ning avab soovitud liiki eksamitele registreerimise vormi. 
"""
from eis.lib.pyxadapterlib.xutils import *
import os
import binascii
from datetime import datetime

from eis import model

import logging
log = logging.getLogger(__name__)

def serve(paring, header=None, attachments=[], context=None):
    """Eesti.ee portaali kaudu sisenemise teenus
    Päringu sisendist saame kasutaja andmed ja genereerime võtme, millega need andmed seostame.
    Päringu väljundis anname võtmega URLi, mille poole kasutaja hiljem brauseriga otse pöördub
    ja kus saame võtme järgi kasutajaandmed kätte.
    """
    model.Paring_logi.log(header)
    return add_legacy(paring, header, context, None)
    
def add_legacy(paring, header, handler, param):
    
    settings = handler.request.registry.settings
    baseuri = settings.get('eis.legacy.baseurl') 
    assert baseuri, 'Seadistamata eis.legacy.baseurl'
    
    # genereerime juhusliku koodi, mida URLis kasutada võtmena
    kood = binascii.b2a_hex(os.urandom(16)).decode('utf-8')

    # jätame meelde kasutaja nime ja isikukoodi
    nimi = header.userName
    if nimi:
        li = nimi.rsplit(' ', 1)
        perenimi = li[-1]
        eesnimi = li[0]
    else:
        eesnimi = perenimi = None

    risikukood = header.userId

    # kustutame muud sama isiku koodid
    model.Legacy.query.filter(model.Legacy.risikukood==risikukood).delete()
    
    # salvestame andmed andmebaasis
    row = model.Legacy(kood=kood,
                       risikukood=risikukood,
                       eesnimi=eesnimi,
                       perenimi=perenimi,
                       param=param,
                       aeg=datetime.now())
    model.Session.commit()

    # vastame URLiga
    url = '%s/legacy?id=%s' % (baseuri, kood)
    res = E.response(E.url(url))
    return res, []

