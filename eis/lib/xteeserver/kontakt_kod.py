"""
Kontaktandmete allalaadimine riigiportaalis.
Kui sooritaja isikukoodiga kasutajat EISi andmebaasis pole, siis luuakse isiku kirje.
Küsitakse eesti.ee eposti andmekogust, kas kasutaja eesti.ee aadress on aktiveeritud.
Küsitakse rahvastikuregistrist isikuandmed ja salvestatakse need.
Väljastatakse isikuandmed. 
"""
from lxml import etree

from eis.lib.pyxadapterlib.xutils import *
import eis.model as model
import eiscore.const as const
import eis.lib.helpers as h
import eis.lib.xtee.rahvastikuregister as rahvastikuregister

import logging
log = logging.getLogger(__name__)

def serve(paring, header=None, attachments=[], context=None):
    error = teade = None
    userId = header.userId
    riik = userId[:2]
    if riik != 'EE':
        errror = 'Teenuse kasutamiseks palume portaali siseneda Eesti isikukoodiga'
        res = E.response(E.teade(error))
        return res, []
        
    ik = userId[2:]
    model.Paring_logi.log(header, paritav=ik)

    class XteeUser(object):
        def __init__(self, isikukood):
            self.isikukood = isikukood
    # X-tee päringute tegemiseks 
    handler = context
    handler.c.user = XteeUser(ik)

    k = model.Kasutaja.get_by_ik(ik)
    if not k:
        # kui isikut pole meie andmebaasis, siis loome kirje
        ametniknimi = header.userName
        if ametniknimi:
            eesnimi, perenimi = ametniknimi.rsplit(' ', 1)
            k = model.Kasutaja.add_kasutaja(ik,eesnimi,perenimi)
            k.flush()

    if k:
        # teeme päringu eesti.ee andmekogusse ja küsime, 
        # kas kodaniku ametlik eesti.ee e-post on olemas ja aktiivne (suunatud)
        eesti_aadress, faultstring = epost.get_eestiaadress(ik, handler=handler)
        if faultstring:
            log.error('Epost päring ebaõnnestus (%s)' % faultstring)                
        else:
            if eesti_aadress and not k.epost:
                k.epost = eesti_aadress

    # uuendame andmed rahvastikuregistrist
    k = rahvastikuregister.set_rr_pohiandmed(handler, k, ik)
    if not k:
        error = 'Rahvastikuregistrist ei saadud isikuandmeid'
        res = E.response()
    else:
        lahi_aadress = ''
        a = k.aadress
        if a:
            lahi_aadress = a.lahi_aadress

        try:
            ehak = '%04d' % int(a and a.kood3 or '')
        except:
            ehak = ''

        try:
            kood2 = '%04d' % int(a and a.kood2 or '')
        except:
            kood2 = ''

        try:
            kood1 = '%04d' % int(a and a.kood1 or '')
        except:
            kood1 = ''
        ehak = ehak or kood2 or kood1
        
        res = E.response(E.eesnimi(k.eesnimi),
                         E.perenimi(k.perenimi),
                         E.kodak(k.kodakond_kood or 'XXX'),
                         E.asula(ehak),
                         E.aadress(E.lahiaadress(lahi_aadress or ''),
                                   E.indeks(k.postiindeks or '')),
                         E.indeks(k.postiindeks or ''),
                         E.kontakt_tel(k.telefon or ''),
                         E.epost_aadr(k.epost or ''),
                         E.epost_teavita('1'))

        model.Session.commit()

        # kui on eesti.ee on suunatud, siis läheb käiku vaid m-teavituse numbri küsimine
        # kui on eesti.ee ei ole suunatud, siis läheb käiku e-teavituse aadressi 
        # ja m-teavituse numbri küsimine
        if eesti_aadress:
            # järgmisele päringule (komplekspäringu lüliti) antakse teada, 
            # et kuvatakse vaid m-teavituse variant
            res.append(E.edasi1(''))
        else:
            # järgmisele päringule (komplekspäringu lüliti) antakse teada, 
            # et kuvatakse nii e-teavituse kui ka m-teavituse variant
            res.append(E.edasi2(''))

    if error:
        res.append(E.teade(error))

    return res, []

