# -*- coding: utf-8 -*- 
"""
Ärakuulamise tähtaja ületanud vaided märgitakse otsustamisel olekusse ning saadetakse teade
"""
from datetime import date, datetime, timedelta
from .scriptuser import *
import sqlalchemy as sa
from pyramid.renderers import render
from eis.lib.helpers import fstr

def usage():
    print('Kasuta kujul:')
    print('   python -m eis.scripts.vaidetahtaeg [-f KONFIFAIL]')
    sys.exit(0)

def poll_tahtaeg():
    q = (model.Session.query(model.Vaie,
                             model.Test.testiliik_kood,
                             model.Test.id)
         .filter(model.Vaie.staatus==const.V_STAATUS_ETTEPANDUD)
         .filter(model.Vaie.arakuulamine_kuni<date.today())
         .join(model.Vaie.sooritaja)
         .join(model.Sooritaja.test)
         .order_by(model.Test.testiliik_kood,
                   model.Test.id,
                   model.Vaie.id)
         )
    prev_testiliik_kood = None
    li_vaided = []
    for vaie, testiliik_kood, test_id in list(q.all()):
        vaie.staatus = const.V_STAATUS_OTSUSTAMISEL
        if testiliik_kood != prev_testiliik_kood:
            _send_vaidekom(li_vaided, prev_testiliik_kood)
            li_vaided = []
            prev_testiliik_kood = testiliik_kood
        li_vaided.append((vaie.id, vaie.vaide_nr))

    _send_vaidekom(li_vaided, prev_testiliik_kood)
    model.Session.commit()

def _send_vaidekom(li_vaided, testiliik_kood):
    "Vaidekomisjoni liikmetele saadetakse kiri"

    if not li_vaided:
        return
    
    # leiame kõik vaidekomisjoni liikmed
    q = (model.Session.query(model.Kasutaja.id, model.Kasutaja.epost)
         .filter(model.Kasutaja.kasutajarollid.any(
            sa.and_(model.Kasutajaroll.kasutajagrupp_id==const.GRUPP_VAIDEKOM,
                    model.Kasutajaroll.testiliik_kood==testiliik_kood,
                    model.Kasutajaroll.kehtib_alates<=datetime.now(),
                    model.Kasutajaroll.kehtib_kuni>=datetime.now())))
         .filter(model.Kasutaja.epost!=None)
         )
    kasutajad = [(k_id, epost) for (k_id, epost) in q.all()]
    aadressid = [epost for (k_id, epost) in kasutajad]
    if not aadressid:
        log.info('Vaidekomisjoni liikmete (testiliik %s) aadresse ei ole')
        return
    
    id_host = registry.settings.get('eis.pw.url')
    li = []
    for vaie_id, vaide_nr in li_vaided:
        vaie_url = '%s/ekk/muud/vaided/%d/edit' % (id_host, vaie_id)
        li.append((vaide_nr or vaie_id, vaie_url))
        
    data = {'vaided': li,
            }
    subject, body = _render_mail('mail/vaideotsus.otsustamisel.mako', data)
    try:
        Mailer(user.handler).send_ex(aadressid, subject, body)
    except Exception as e:
        script_error('Ei saa kirja saata', e)
    else:
        log.info('Teade %d vaide ärakuulamise tähtaja möödumise kotha on saadeutd vaidekomisjoni liikmetele %s' % (len(li), ', '.join(aadressid)))
        kiri = model.Kiri(tyyp=model.Kiri.TYYP_MUU,
                          sisu=body,
                          teema=subject,
                          teatekanal=const.TEATEKANAL_EPOST)
        for k_id, epost in kasutajad:
            model.Kirjasaaja(kiri=kiri, kasutaja_id=k_id, epost=epost)
        model.Session.commit()

def _render_mail(template, data):
    body = render(template, data, user.handler.request)
    subject = None
    li = body.split('\n', 1)
    if len(li) == 2:
        hdr = 'Subject:'
        if li[0].startswith(hdr):
            subject = li[0][len(hdr):]
            body = li[1]
    return subject, body
    
        
if __name__ == '__main__':
    fn_lock = '/srv/eis/log/vaidetahtaeg.lock'
    with FileLock(fn_lock) as lock:
        if not lock:
            log.info('Protsess juba käib (fail %s on lukus)' % fn_lock)
            sys.exit(0)
        poll_tahtaeg()
        
