# -*- coding: utf-8 -*- 
"""
Tulemuste andmete ajatembeldamine GuardTime'i teenusega ning allkirjade kontroll
Käivitada crontabist regulaarselt


Allkirjastamine
---------------
Tulemuse muutmisel EISiga tekib Sooritajalogi kirje, kus sig_status=1.
Allkirjastamise skripti käivitamisel:

python -m eis.scripts.integrity sign

leitakse sellised kirjed, mis vajavad allkirjastamist.
Igale allkirjastamata sooritusele moodustatakse andmete string 
isikukood;nimi;testi ID;aine kood;pallid;tulemuse arvutamise aeg
ning võetakse sellest SHA-256 räsi.
Kõigi hetkel allkirjastamata tulemuste kohta tehakse üks tabeli Integritysig kirje,
mille väljal data on Sooritajalogi tulemuste andmete räsid koos (reavahetused vahel)
ning sellest võetud räsi on väljal data_hash.
Räsi allkirjastatakse Catena abil.


Allkirjade kontrollimine
------------------------
Kontrolli käivitamisel:

python -m eis.scripts.integrity verify [-d PÄEVADEARV]

leitakse kõik allkirjad, mida ei ole viimase PÄEVADEARV päeva jooksul kontrollitud.
Nende allkirjade kehtivates tulemustes (Sooritajalogi) pannakse uuesti kokku tulemuse andmete string,
võetakse sellest räsi, kontrollitakse, et see pole muutunud ning et see sisaldub Integritysig.data sees
ning kontrollitakse Catena abil Integritysig allkirja.

EISi Innove vaates registreeringu andmete vormil kuvatakse testisoorituse oleku muudatused
koos allkirjastamise aja, viimase kontrollimise aja ning saadud veateadetega.
"""
import hashlib
from datetime import datetime, timedelta
import base64
from .scriptuser import *
import sqlalchemy as sa
from eis.lib.xtee.catena import CatenaClient
from eis.lib.helpers import fstr

def usage():
    print('Allkirjastamata tulemuste allkirjastamiseks kasuta kujul:')
    print('   python -m eis.scripts.integrity sign [-f KONFIFAIL]')
    print('Allkirjade kontrollimiseks kasuta kujul:')
    print('   python -m eis.scripts.integrity verify [-d PÄEVADEARV] [-f KONFIFAIL]')    
    print('   kus PÄEVADEARV näitab, kui kaua kontrollimata olnud tulemusi kontrollida (vaikimisi 7 päeva)')
    print()
    sys.exit(0)

def sign_all():
    # allkirjastame või märgime allkirja mitte vajavaks
    testiliigid = (const.TESTILIIK_RIIGIEKSAM,
                   const.TESTILIIK_RV,
                   const.TESTILIIK_POHIKOOL,
                   const.TESTILIIK_TASE,
                   const.TESTILIIK_SEADUS)
    # testiliigid, mis ei vaja allkirjastamist
    upd = model.Sooritajalogi.__table__.update().values(sig_status=const.G_STAATUS_NONE).where(
        sa.and_(model.Sooritajalogi.sig_status==const.G_STAATUS_UNSIGNED,
                model.Sooritajalogi.sooritaja_id==model.Sooritaja.id,
                model.Sooritaja.test_id==model.Test.id,
                ~ model.Test.testiliik_kood.in_(testiliigid)
                ))
    model.Session.execute(upd)
    
    # testimiskorrata testid ei vaja allkirjastamist
    upd = model.Sooritajalogi.__table__.update().values(sig_status=const.G_STAATUS_NONE).where(
        sa.and_(model.Sooritajalogi.sig_status==const.G_STAATUS_UNSIGNED,
                model.Sooritajalogi.sooritaja_id==model.Sooritaja.id,
                model.Sooritaja.testimiskord_id==None)
        )
    model.Session.execute(upd)
    
    # kirjed, mida on hiljem juba uuendatud, ei vaja allkirjastamist
    Sooritajalogi2 = sa.orm.aliased(model.Sooritajalogi)
    upd = model.Sooritajalogi.__table__.update().values(sig_status=const.G_STAATUS_NONE).where(
        sa.and_(model.Sooritajalogi.sig_status==const.G_STAATUS_UNSIGNED,
                model.Sooritajalogi.sooritaja_id==model.Sooritaja.id,
                sa.exists().where(
                    sa.and_(Sooritajalogi2.sooritaja_id==model.Sooritajalogi.sooritaja_id,
                            Sooritajalogi2.created>model.Sooritajalogi.created,
                            Sooritajalogi2.sig_status>const.G_STAATUS_NONE))
                )
        )
    model.Session.execute(upd)
    
    # allkirjad kirjetel, mille tulemust on hiljem muudetud, on vananenud
    Sooritajalogi2 = sa.orm.aliased(model.Sooritajalogi)
    upd = model.Sooritajalogi.__table__.update().values(sig_status=const.G_STAATUS_OLD).where(
        sa.and_(model.Sooritajalogi.sig_status.in_((const.G_STAATUS_SIGNED, const.G_STAATUS_ERROR)),
                model.Sooritajalogi.sooritaja_id==model.Sooritaja.id,
                sa.exists().where(
                    sa.and_(Sooritajalogi2.sooritaja_id==model.Sooritajalogi.sooritaja_id,
                            Sooritajalogi2.created>model.Sooritajalogi.created,
                            sa.or_(Sooritajalogi2.sig_status>const.G_STAATUS_NONE,
                                   Sooritajalogi2.pallid==None))
                    )
                )
        )
    model.Session.execute(upd)
    
    # testimiskorraga tulemused allkirjastame
    q = (model.Session.query(model.Sooritajalogi, model.Test.aine_kood)
         .filter(model.Sooritajalogi.sig_status==const.G_STAATUS_UNSIGNED)
         .join(model.Sooritajalogi.sooritaja)
         .filter(model.Sooritaja.test_id==model.Test.id)
         .filter(model.Test.testiliik_kood.in_(testiliigid))
         .filter(model.Sooritaja.testimiskord_id!=None)
         .filter(~ sa.exists().where(
             sa.and_(Sooritajalogi2.sooritaja_id==model.Sooritajalogi.sooritaja_id,
                     Sooritajalogi2.created>model.Sooritajalogi.created,
                     Sooritajalogi2.sig_status>const.G_STAATUS_NONE)
             ))
         )
    if q.count() > 0:
        sig = model.Integritysig()
        sig_data = []
        # kogume testi kõik allkirjastamata tulemused kokku
        for sl, aine_kood in q.all():
            sl.data_sig, sl.data_hash = _get_sig_data(sl, aine_kood)
            if not sl.data_sig:
                sl.sig_status = const.G_STAATUS_NONE
                continue
            sl.sig_status = const.G_STAATUS_SIGNED
            sig.sooritajalogid.append(sl)
            sig_data.append(sl.data_hash)

            # märgime sooritaja kirje varasemad allkirjad aegunuks
            upd = model.Sooritajalogi.__table__.update().values(sig_status=const.G_STAATUS_OLD).where(
                sa.and_(model.Sooritajalogi.sig_status==const.G_STAATUS_SIGNED,
                        model.Sooritajalogi.sooritaja_id==sl.sooritaja_id,
                        model.Sooritajalogi.created<sl.created)
                )
            model.Session.execute(upd)
            
        log.info('  %s tulemust' % len(sig_data))
        sig.data = '\n'.join(sig_data)
        sig.data_hash = base64.b64encode(hashlib.sha256(sig.data).digest()).strip()

        srv = CatenaClient(settings=registry.settings)
        sig.response, jresponse, err = srv.sign(sig.data_hash)
        if err:
            return False, err
        else:
            sig.signature_id = jresponse['id']
            sig.signature = jresponse['signature']
            sig.signed = sig.verified = datetime.fromtimestamp(jresponse['createdAt']/1000.)
            sig.status = const.B_STAATUS_KEHTIV
    return True, None

def verify_sig(sig):
    # allkirja kontrollimine
    li_err = []
    Sooritajalogi2 = sa.orm.aliased(model.Sooritajalogi)
    q = (model.Sooritajalogi.query
         .filter(model.Sooritajalogi.integritysig_id==sig.id)
         .filter(model.Sooritajalogi.sig_status==const.G_STAATUS_SIGNED)
         .filter(~ sa.exists().where(
             sa.and_(Sooritajalogi2.sooritaja_id==model.Sooritajalogi.sooritaja_id,
                     Sooritajalogi2.sig_status>const.G_STAATUS_NONE,
                     Sooritajalogi2.created>model.Sooritajalogi.created)
             ))
         )
    cnt = 0
    for sl in q.all():
        err = None
        data_sig, data_hash = _get_sig_data(sl)
        if data_sig != sl.data_sig:
            # andmed on muutunud
            err = 'andmed ei vasta tegelikkusele - kirjes "%s", tegelikult "%s"' % (sl.data_sig, data_sig)
        elif data_hash != sl.data_hash:
            err = 'räsi ei ole õige - kirjes "%s", tegelikult "%s"' % (sig.data_hash, data_hash)
        elif data_hash not in sig.data:
            err = 'kirje räsi puudub allkirjastatud räsist - kirjes "%s"' % data_hash 
        if err:
            sooritaja = sl.sooritaja
            err = '%s %s test %s: %s' % (sooritaja.kasutaja.isikukood,
                                          sooritaja.nimi,
                                          sooritaja.test_id,
                                          err)
            sl.sig_status = const.G_STAATUS_ERROR
            sl.err_msg = err[:256]
            li_err.append(err)
        else:
            # kontrollime
            sl.err_msg = None
            cnt += 1

    if cnt > 0:
        err = None
        data_hash = base64.b64encode(hashlib.sha256(sig.data).digest()).strip()

        srv = CatenaClient(settings=registry.settings)
        response, jresponse, err = srv.verify(sig.signature_id)
        if err:
            model.Session.rollback()
            script_error('Veateade (integrity verify)', None, err)
            sys.exit(1)                
        elif jresponse['verificationResult']['status'] != 'OK':
            err = 'kontrolli tulemus on %s' % jresponse['verificationResult']['status']
        elif jresponse['details']['dataHash']['value'] != data_hash:
            err = 'allkirjastatud räsi erineb'
        else:
            createdAt = datetime.fromtimestamp(jresponse['createdAt']/1000.)
            if createdAt != sig.signed:
                err = 'allkirjastamise aeg erineb'
        sig.verified = datetime.now()
        if err:
            sig.status = const.B_STAATUS_KEHTETU
            sig.err_msg = err[:256]
            li_err.append('Allkiri %s (%s): %s' % (sig.id, sig.signature_id, err))
        else:
            sig.status = const.B_STAATUS_KEHTIV
            sig.err_msg = None
            
    return li_err

def _get_sig_data(sl, aine_kood=None):
    sooritaja = sl.sooritaja
    if sooritaja.pallid is None:
        return None, None
    if not aine_kood:
        aine_kood = sooritaja.test.aine_kood
    kasutaja = sooritaja.kasutaja
    data = [kasutaja.isikukood or '',
            sooritaja.nimi,
            str(sooritaja.test_id),
            aine_kood,
            fstr(sooritaja.pallid),
            sooritaja.tulemus_aeg.strftime('%Y-%m-%d %H.%M'),
            ]
    #print(data)
    data_sig = ';'.join(data)
    data_hash = base64.b64encode(hashlib.sha256(data_sig.encode('utf-8')).digest()).strip()
    return data_sig, data_hash

def poll_sign():
    rc, err = sign_all()
    if err:
        model.Session.rollback()
        script_error('Veateade (integrity sign, test %s)' % test.id, None, err)
        sys.exit(1)                
    if rc:
        model.Session.commit()

def poll_verify(days):
    "Leiame testid, milles on tulemusi vaja allkirjastada"
    q = (model.Session.query(model.Integritysig)
         .filter(model.Integritysig.verified<datetime.now()-timedelta(days=days))
         .order_by(model.Integritysig.id)
         )
    for sig in q.all():
        log.info('Kontrollin allkirja %s (%s)...' % (sig.id, sig.signature_id))
        li_err = verify_sig(sig)
        model.Session.commit()
        if li_err:
            li_err.insert(0, '%s #%s' % (sig.signed.strftime('%Y-%m-%d'), sig.id))
            script_error('Andmetervikluse viga', None, '\n'.join(li_err))

    # loeme kokku, kui palju on tervikluse vigadega sooritajalogisid
    q = (model.Session.query(sa.func.count(model.Sooritajalogi.id))
         .filter(model.Sooritajalogi.sig_status==const.G_STAATUS_ERROR))
    cnt_log = q.scalar()

    # kui palju on vigaseid allkirju
    q = (model.Session.query(sa.func.count(model.Integritysig.id))
         .filter(model.Integritysig.status==const.B_STAATUS_KEHTETU))
    cnt_sig = q.scalar()

    log.info('Andmebaasis on %d tervikluse veaga testitulemust ning %d vigast allkirja' % (cnt_log, cnt_sig))

        
if __name__ == '__main__':
    op = None
    if len(noname_args) == 1:
        op = noname_args[0]
    if op not in ('sign', 'verify'):
        usage()
        
    fn_lock = '/srv/eis/log/integrity.%s.lock' % op
    with FileLock(fn_lock) as lock:
        if not lock:
            log.info('Protsess juba käib (fail %s on lukus)' % fn_lock)
            sys.exit(0)
        if op == 'sign':
            poll_sign()
        elif op == 'verify':
            try:
                days = int(named_args.get('d') or 7)
            except:
                usage()
            poll_verify(days)
    
        
