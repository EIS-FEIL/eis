"""
Vanade ajutiste andmete kustutamine

Käivitada crontabist mõnekümne minuti tagant:

python -m eis.scripts.remove_esitlus
"""
from datetime import datetime, timedelta
from eis.scripts.scriptuser import *
from eis.lib.testsaga import TestSaga

def usage():
    print('Kasuta kujul:')
    print('   python -m eis.scripts.remove_esitlus [-f KONFIFAIL] [-y TUNNID]')
    print()
    sys.exit(0)

def run():
    # vanade testi eelvaates soorituste kustutamine
    b_hours = 3
    dt = datetime.now() - timedelta(hours=b_hours)

    # leiame eelvaates kasutatud komplektid
    q = (model.Session.query(model.Soorituskomplekt.komplekt_id).distinct()
         .join((model.Sooritus, model.Sooritus.id==model.Soorituskomplekt.sooritus_id))
         .join(model.Sooritus.sooritaja)
         .filter(model.Sooritaja.regviis_kood==const.REGVIIS_EELVAADE)
         .filter(model.Sooritaja.modified<dt))
    komplektid_id = [k_id for k_id, in q.all()]

    # leiame eelvaate sooritused ja kustutame
    q = (model.Session.query(model.Sooritaja)
         .filter(model.Sooritaja.regviis_kood==const.REGVIIS_EELVAADE)
         .filter(model.Sooritaja.modified<dt))
    for sooritaja in q.all():
        sooritaja.delete()
    model.Session.flush()

    # arvutame komplektide lukustuse uuesti
    for k_id in komplektid_id:
        k = model.Komplekt.get(k_id)
        TestSaga(handler).komplekt_set_lukus(k, None)
    model.Session.commit()

    
    # heli kontrollimiseks tehtud salvestuste eemaldamine
    dt = datetime.now() - timedelta(hours=4)
    q = (model.Session.query(model.Helivastusfail)
         .filter(~ model.Helivastusfail.helivastused.any())
         .filter(model.Helivastusfail.created < dt)
         .filter(model.Helivastusfail.filename.like('helikontroll%'))
         )
    for r in q.all():
        r.delete()
    model.Session.commit()
    
    
    # vanade autentimata kasutajate seansside kustutamine
    # (autenditud kasutaja vanad seansid kustutatakse järgmisel sisselogimisel)
    b_hours = 24
    dt = datetime.now() - timedelta(hours=b_hours)
    
    q = (model_s.DBSession.query(model_s.Beaker_cache)
         .filter(model_s.Beaker_cache.accessed < dt)
         .filter(model_s.Beaker_cache.kasutaja_id==None))
    q.delete()

    # ylesande eelvaates lahendamiste kustutamine
    flt = sa.and_(model.Ylesandevastus.sooritus_id==None,
                  model.Ylesandevastus.testiylesanne_id==None,
                  model.Ylesandevastus.algus < dt)

    q = (model.Session.query(model.Kvsisu)
          .filter(model.Kvsisu.kysimusevastus_id.in_(
              sa.select(model.Kysimusevastus.id)
              .where(model.Kysimusevastus.ylesandevastus_id==model.Ylesandevastus.id)
              .where(flt)))
          )
    q.delete(synchronize_session='fetch')

    q = (model.Session.query(model.Kysimusevastus)
          .filter(model.Kysimusevastus.ylesandevastus_id.in_(
              sa.select(model.Ylesandevastus.id).where(flt)))
          )
    q.delete(synchronize_session='fetch')

    q = (model.Session.query(model.Sisuvaatamine)
          .filter(model.Sisuvaatamine.ylesandevastus_id.in_(
              sa.select(model.Ylesandevastus.id).where(flt)))
          )
    q.delete(synchronize_session='fetch')

    q = (model.Session.query(model.Loendur)
          .filter(model.Loendur.ylesandevastus_id.in_(
              sa.select(model.Ylesandevastus.id).where(flt)))
          )
    q.delete(synchronize_session='fetch')

    q = (model.Session.query(model.Npvastus)
          .filter(model.Npvastus.ylesandevastus_id.in_(
              sa.select(model.Ylesandevastus.id).where(flt)))
          )
    q.delete(synchronize_session='fetch')

    q = model.Session.query(model.Ylesandevastus).filter(flt)
    q.delete()

    # vanad
    q = (model_s.DBSession.query(model_s.Tempvastus)
         .filter(model_s.Tempvastus.modified<dt))
    q.delete()


    # pooleli jäänud arvutusprotsesside lõpetatuks märkimine
    b_hours = 3
    dt = datetime.now() - timedelta(hours=b_hours)

    q = (model.Session.query(model.Arvutusprotsess)
         .filter(model.Arvutusprotsess.lopp==None)
         .filter(model.Arvutusprotsess.modified < dt))
    for p in q.all():
        p.lopp = p.modified
    model.Session.commit()
    
def _error(exc, msg=''):
    script_error('Veateade (remove_esitlus)', exc, msg)
    sys.exit(1)   
       
if __name__ == '__main__':
    fn_lock = '/srv/eis/log/remove_esitlus.lock'
    with FileLock(fn_lock) as lock:
        if not lock:
            log.info('Protsess juba käib (fail %s on lukus)' % fn_lock)
            sys.exit(0)

        try:
            run()
        except Exception as e:
            _error(e, str(e))
