"""
EHIS informeerib EISi plankide väljastamisest.
EIS kontrollib iga sisendis antud plangi kohta, kas plank asub antud koolis ja on vaba. 
Kui planki on võimalik väljastada, siis märgitakse see väljastatuks. 
Kui planki pole võimalik antud koolis väljastada, siis seda väljastatuks ei märgita ning plangi andmed ja veateade lisatakse väljundis olevasse vigade jadasse. EIS saadab vigade jadas olevad veateated e-postiga Innove plankide haldurile, kes probleemi lahendab.
Medalid ja medalikotid väljastatakse koos tunnistusega: tunnistuse plangi numbri juures tehakse märge, kas lisaks väljastatakse kuldmedal või hõbemedal.

"""
from lxml import etree

from eis.lib.pyxadapterlib.xutils import *
from datetime import datetime

import eis.lib.helpers as h
from eis.lib.mailer import Mailer
from eis.forms import validators

from eis_plank import model
from eis_plank.model import const

import logging
log = logging.getLogger(__name__)

def serve(paring, header=None, attachments=[], context=None):
    kogus = 0
    vead = E.vead()
    errors = []
    plangijada = list(paring.find('plangijada'))
    for item in plangijada:
        viga, msg = _save_item(item)
        if viga:
            vead.append(viga)
            errors.append(msg)
        else:
            kogus += 1

    res = E.response(E.valjastatud_kogus(str(kogus)),
                 vead)
    if kogus > 0:
        model.Session.commit()
        
    if errors:
        # saadame veateated Kristile
        _send_errors(context, errors)

    return res, []

def _send_errors(handler, errors):
    q = model.Session.query(model.Kasutaja.epost).distinct().\
        filter(model.Kasutaja.epost!=None).\
        join(model.Kasutaja.kasutajarollid).\
        filter(model.Kasutajaroll.kasutajagrupp_id==const.GRUPP_PLANK)
    to = [r for r, in q.all()]
    if not to:
        log.error('Ei saa väljastamise vigu saata, kuna puudub plankide haldaja e-posti aadress')
        return

    subject = 'Plankide väljastamise vead'
    body = '<br/>\n '.join(errors)
    body = Mailer.replace_newline(body)
    if not Mailer(handler).send(to, subject, body, out_err=False):
        log.info('Kiri saadetud aadressile %s' % to)

def _save_item(item):
    error = None

    kool_id = item.find('kool_id').text
    kool = model.Koht.query.filter(model.Koht.kool_id==kool_id).first()
    if not kool:
        error = 'Kooli %s ei leitud' % kool_id

    oppetase_kood = item.find('oppetase').text

    oppekava_kood = None
    node = item.find('oppekava')
    if node is not None:
        oppekava_kood = node.text

    plank_nr = item.find('plank_nr').text
    
    node = item.find('medal')
    medal = node is not None and int(node.text) or None

    if not error:
        seeria, n = model.Plangiseeria.parts(plank_nr)

        q = model.Plank.query.\
            filter(model.Plank.nr==plank_nr).\
            join(model.Plank.plangiseeria).\
            join(model.Plangiseeria.plangiliik).\
            filter(model.Plangiliik.oppetase_kood==oppetase_kood)
        if seeria:
            q = q.filter(model.Plangiseeria.seeria==seeria)
        else:
            q = q.filter(model.Plangiseeria.seeria==None)

        if oppekava_kood:
            q = q.join(model.Plangiliik.plangitasemed).\
                filter(model.Plangitase.kavatase_kood==oppekava_kood)

        item = q.first()
        if not item:
            error = 'Planki nr %s, seeria "%s", õppetase "%s", õppekava "%s" ei leitud' % \
                (plank_nr, seeria, oppetase_kood, oppekava_kood or '')
        elif q.count() > 1:
            error = 'Plangiliiki ei õnnestu üheselt määrata'
        elif item.koht_id != kool.id:
            error = 'Plangi %s asukoht ei ole %s' % (plank_nr, kool.nimi)
        elif item.staatus != const.P_STAATUS_VABA:
            error = 'Plank %s ei ole vaba' % (plank_nr)

    valjastatud_kpv = datetime.now()
    if not error and medal:
        # otsime medali ja medalikoti
        if medal == 1:
            medal_liik_id = const.PLIIK_KULDMEDAL
            kott_liik_id = const.PLIIK_KULDMEDALI_KOTT
            nimi = 'kuld'
        elif medal == 2:
            medal_liik_id = const.PLIIK_HOBEMEDAL
            kott_liik_id = const.PLIIK_KULDMEDALI_KOTT
            nimi = 'hõbe'
        else:
            error = 'Tundmatu medali liik %s' % (medal)

        if not error:
            q = model.Plank.query.\
                filter(model.Plank.koht_id==kool.id).\
                filter(model.Plank.staatus==const.P_STAATUS_VABA).\
                join(model.Plank.plangiseeria)

            p_medal = q.filter(model.Plangiseeria.plangiliik_id==medal_liik_id).first()
            if not p_medal:
                error = 'Pole vabu %smedaleid' % nimi
                    
            p_kott = q.filter(model.Plangiseeria.plangiliik_id==kott_liik_id).first()
            if not p_kott:
                error = 'Pole vabu %smedalikotte' % nimi

        if not error:
            # märgime medali ja koti väljastatuks
            p_medal.staatus = const.P_STAATUS_KASUTATUD
            p_medal.valjastatud_kpv = valjastatud_kpv
            p_kott.staatus = const.P_STAATUS_KASUTATUD
            p_kott.valjastatud_kpv = valjastatud_kpv

    if not error:
        # märgime plangi väljastatuks
        item.staatus = const.P_STAATUS_KASUTATUD
        item.valjastatud_kpv = valjastatud_kpv


    if error:
        res = E.item(E.kool_id(kool_id),
                     E.plank_nr(plank_nr),
                     E.oppetase(oppetase_kood),
                     E.oppekava(oppekava_kood or ''),
                     E.veateade(error))
        if kool:
            msg = '%s (%s, plank %s, õppetase %s)' % (error, kool.nimi, plank_nr, oppetase_kood)
        else:
            msg = '%s (plank %s, õppetase %s)' % (error, plank_nr, oppetase_kood)
        return res, msg

    return None, None
