# Regulaarne andmevahetus ADSiga
# Käivitada crontabist igal ööl

# python -m eis.scripts.ads_update ...

import re
import sqlalchemy as sa
import traceback
import cgi
import fcntl
import os

from .scriptuser import *
from eis.lib.xtee import ads, SoapFault
from eis.lib.mailer import Mailer

# ADSi muudatuste syndmuste koodid
SYNDMUS_I = 'I' # lisamine
SYNDMUS_U = 'U' # muutmine
SYNDMUS_D = 'D' # tyhistamine
SYNDMUS_R = 'R' # taastamine

def olek():
    data = (('ADS aadressikomponentide klassifikaator', model.Olekuinfo.ID_ADS_KOMPONENT),
            ('ADS aadressimuudatuste logi', model.Olekuinfo.ID_ADS_AADRESS),
            )
    for (name, id) in data:
        info = model.Olekuinfo.give(id)
        if info and info.seisuga:
            log.info('%s: seisuga %s kuni logini %s' % \
                         (name, info.seisuga.isoformat(), info.seis_id))
        else:
            log.info('%s: andmevahetus puudub' % name)

    q = model.Session.query(model.Aadress.staatus, sa.func.count(model.Aadress.id)).\
        group_by(model.Aadress.staatus).\
        order_by(model.Aadress.staatus)
    for (staatus, cnt) in q.all():
        log.info('%s - %d kirjet' % (const.A_STAATUS.get(staatus), cnt))
    


def klassifikaatorid(reg):
    "Aadresskomponentide klassifikaatorite uuendamine"
    info = model.Olekuinfo.give(model.Olekuinfo.ID_ADS_KOMPONENT)
    alates = info.seisuga or date(2012,3,1)
    uus_seisuga = datetime.now()
    logId = info.seis_id or None
    MAXARV = 100
    total = 0
    while True:
        log.info('Küsin muudatusi alates %s ja logikirjest %s...' % \
                      (alates.strftime('%d.%m.%Y'), logId))
        try:
            message, soap_li = reg.kompklassif(alates, logId=logId, maxarv=MAXARV)
        except SoapFault as e:
            _error(e, e.faultstring)
        else:
            if message:
                _error(None, message)

            log.debug('%d kirjet muutub...' % len(soap_li))
            logId = None
            cnt = -1
            for cnt, rcd in enumerate(soap_li):
                syndmus = str(rcd.syndmus)
                #syndmus = rcd.syndmus
                logId = int(rcd.logId)
                _update_klassif(rcd, syndmus, logId)

            info.seis_id = logId
            model.Session.commit()
            total += cnt + 1
            if cnt < MAXARV - 1:
                # rohkem muudatusi ei ole
                break

    info.seisuga = uus_seisuga
    model.Session.commit()
    log.info('Uuendatud %d klassifikaatorikirjet' % total)


def _update_klassif(rcd, syndmus, logId):
    "Yhe klassifikaatorikirje uuendamine"

    tase = int(rcd.tase)
    kood = str(rcd.kood)
    nimetus = str(rcd.nimetus)
    nimetusLiigiga = str(rcd.nimetusLiigiga)
    ylemTase = int(rcd.ylemTase) or None
    ylemKood = str(rcd.ylemKood) or None
    if ylemKood == '0':
        ylemKood = None
    
    log.debug('  logId %s %s %s.%s' % (logId, syndmus, tase, kood))

    # I (insert) - komponent lisandus, 
    # U (update) - komponenti versiooniti, 
    # D (delete) - komponendi viimane versioon muudeti kehtetuks
    # R (restore) - komponent taastatakse

    komp = (model.Session.query(model.Aadresskomponent)
            .filter_by(tase=tase)
            .filter_by(kood=kood)
            .first())
    if komp:
        komp.ads_log_id = logId
        
    if syndmus == SYNDMUS_D:
        # komponent ei kehti
        if not komp:
            # komponent peaks olemas olema, aga ei ole
            log.warning('  Kustutatakse varem puudunud komponent %s.%s' % (tase, kood))
        else:
            komp.staatus = const.B_STAATUS_KEHTETU
            log.warning('  Muudetakse kehtetuks komponent %s.%s (logId %s)' % (tase,kood, logId))
                    
    else:
        # komponent kehtib
        if not komp:
            if syndmus == SYNDMUS_U:
                log.warning('  Muudetakse varem puudunud komponenti %s.%s' % (tase, kood))
            komp = model.Aadresskomponent(tase=tase,
                                          kood=kood,
                                          nimetus=nimetus,
                                          nimetus_liigiga=nimetusLiigiga,
                                          ylemkomp_tase=ylemTase,
                                          ylemkomp_kood=ylemKood,
                                          staatus=const.B_STAATUS_KEHTIV,
                                          ads_log_id=logId)
            model.Session.add(komp)
            model.Session.flush()
        else:
            komp.nimetus = nimetus
            komp.nimetus_liigiga = nimetusLiigiga
            komp.ylemkomp_tase = ylemTase
            komp.ylemkomp_kood = ylemKood
            komp.staatus = const.B_STAATUS_KEHTIV
            
def aadrmuudatused(reg):
    "Aadresside muudatuste logi jälgimine"
    info = model.Olekuinfo.give(model.Olekuinfo.ID_ADS_AADRESS)
    alates = info.seisuga or datetime(2020,10,3)
    uus_seisuga = datetime.now()
    logId = info.seis_id or None
    MAXARV = 100
    PAEVAD = 10
    total = 0
    total_changed = 0

    while True:
        log.info('Küsin muudatusi alates %s ja logikirjest %s...' % \
                      (alates.strftime('%d.%m.%Y'), logId))
        cnt_changed = 0
        try:
            message, soap_li = reg.aadrmuudatused(alates, logId=logId, maxarv=MAXARV, muudetudPaevad=PAEVAD)
        except SoapFault as e:
            _error(e, e.faultstring)
        else:
            if message:
                _error(None, message)

            logId = None
            cnt = -1
            for cnt, rcd in enumerate(soap_li):
                syndmus = str(rcd.syndmus)
                logId = int(rcd.logId)
                cnt_changed = _update_aadr(rcd, syndmus, logId)
                if cnt_changed:
                    total_changed += cnt_changed

            info.seis_id = logId
            info.seisuga = alates
            model.Session.commit()
            total += cnt + 1
            if cnt < MAXARV - 1:
                # rohkem muudatusi selle kuupäevaga ei ole
                alates += timedelta(days=PAEVAD)
                if alates >= uus_seisuga:
                    # kõik kuupäevavahemikud kuni praeguseni on läbi vaadatud
                    break

    info.seisuga = uus_seisuga
    model.Session.commit()
    log.info('Jälgitud %d muudatust, neist meie andmebaasi viidi %d muudatust' % (total, total_changed))

def _update_aadr(rcd, syndmus, logId):
    """Yhe ADSi aadressi uuendamine.
    Tagastatakse meie baasis muudetud aadresside kirjete arv.
    """
    if syndmus == SYNDMUS_D:
        # märgime aadressi tühistatuks
        log.debug('DELETE ADR %s' % rcd)
        adrId = int(rcd.adrId)        
        a = model.Session.query(model.Aadress).filter_by(id=adrId).first()
        if a:
            a.staatus = const.B_STAATUS_KEHTETU
            a.ads_log_id = logId
            log.debug('  logId %s aadress %s tühistatakse' % (logId, a.id))

    elif syndmus == SYNDMUS_I:
        log.debug('INSERT ADR %s' % rcd)        
        adrId = int(rcd.adrId)        
        a = model.Session.query(model.Aadress).filter_by(id=adrId).first()
        if not a:
            koodAadress = str(rcd.koodAadress)
            taisAadress = str(rcd.taisAadress)
            try:
                sihtnumber = int(rcd.sihtnumber)
            except:
                sihtnumber = None
            try:
                lahiAadress = str(rcd.lahiAadress)
            except AttributeError:
                lahiAadress = ''
            a = model.Aadress(id=adrId,
                              tais_aadress=taisAadress,
                              lahi_aadress=lahiAadress,
                              sihtnumber=sihtnumber,
                              staatus=const.B_STAATUS_KEHTIV,
                              ads_log_id=logId)
            a.from_koodaadress(koodAadress)
            model.Session.flush()
            
    elif syndmus == SYNDMUS_U:
        # muutmisel muutub ADR_ID väärtus ja peame otsima vana järgi
        log.debug('UPDATE ADR %s' % rcd)
        vanaAdrId = int(rcd.vanaAdrId)
        adrId = int(rcd.adrId)
        vana_a = model.Aadress.get(vanaAdrId)
        if vana_a:
            vana_a.uus_adr_id = adrId
            vana_a.ads_log_id = logId
        a = model.Aadress.get(adrId)
        if a:
            q = model.Session.query(model.Koht).filter_by(aadress_id=vanaAdrId)
            for r in q.all():
                r.aadress_id=adrId
            q = model.Session.query(model.Kasutaja).filter_by(aadress_id=vanaAdrId)
            for r in q.all():
                r.aadress_id=adrId
    return 1

def test_komp(reg, logid1):
    MAXARV = 100
    alates = date(2023,3,13)
    logId = logid1 or None
    while True:
        log.info('Küsin muudatusi alates %s ja logikirjest %s...' % \
                      (alates.strftime('%d.%m.%Y'), logId))
        try:
            message, soap_li = reg.kompklassif(alates, logId=logId, maxarv=logid1 and 1 or MAXARV)
        except SoapFault as e:
            _error(e, e.faultstring)
        else:
            if message:
                _error(None, message)
            cnt = -1
            for cnt, rcd in enumerate(soap_li):
                logId = int(rcd.logId)
                syndmus = rcd.syndmus
                tase = int(rcd.tase)
                if tase == 2:
                    # valla kustutamine
                    kood = rcd.kood
                    nimetus = rcd.nimetus
                    nimetusLiigiga = rcd.nimetusLiigiga
                    ylemTase = int(rcd.ylemTase) or None
                    ylemKood = rcd.ylemKood or None
                    log.info('KIRJE %d SYNDMUS:%s %s %s' % (logId, syndmus, kood, nimetus))

            if cnt < 0 or logid1:
                break
            break

def _error_mail(txt, msg=''):
    script_error(msg, None, txt)

def _error(exc, msg=''):
    script_error('Veateade (ADSi liides)', exc, msg)
    sys.exit(1)   

def usage():
    print('Kasuta kujul:')
    print('   python -m eis.scripts.ads_update [-f KONFIFAIL] [-t TEGEVUS]')
    print()
    print('kus TEGEVUS on (kui argument puudub, siis tehakse kõik):')
    print('   klassif - klassifikaatori uuendamine')
    print('   logi - aadresside logi jälgimine')
    print('   olek - uuendamise oleku vaatamine')
    print()
    sys.exit(0)

if __name__ == '__main__':
    tegevus = named_args.get('t')
    if tegevus == 'paranda':
        paranda()
        sys.exit(0)

    if tegevus == 'olek':
        olek()
        sys.exit(0)

    admin_ik = named_args.get('admin')
    if admin_ik:
        admin_ik = 'EE%s' % admin_ik
        
    if tegevus and tegevus not in ('normal', 'klassif', 'logi', 'test'):
        usage()

    fn_lock = '/srv/eis/log/ads.lock'
    with FileLock(fn_lock) as lock:
        if not lock:
            log.info('Protsess juba käib (fail %s on lukus)' % fn_lock)
            sys.exit(0)
        
        reg = ads.Ads(settings=registry.settings, 
                      userId=admin_ik, 
                      handler=handler)
        try:
            if tegevus == 'test':
                logId = named_args.get('logid')
                test_komp(reg, logId)
                sys.exit(0)
            if tegevus == 'klassif' or not tegevus:
                log.info('ADSi klassifikaatorite uuendamine')
                klassifikaatorid(reg)
            if tegevus == 'logi' or not tegevus:
                log.info('ADSi aadressimuudatuste logi jälgimine')
                aadrmuudatused(reg)
        except Exception as e:
            _error(e, str(e))
        else:
            model.Session.commit()
