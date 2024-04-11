"""
Kustutatakse testid:
- mis on üle aasta vana ja tühi;
- mida pole aasta jooksul kasutatud.

Käivitada crontabist_

python -m eis.scripts.remove_test
"""
import traceback
import html
from datetime import datetime, timedelta
from eis.lib.mailer import Mailer
from .scriptuser import *

def usage():
    print('Kasuta kujul:')
    print('   python -m eis.scripts.remove_test [-f KONFIFAIL]')
    print()
    sys.exit(0)

def remove():
    dt = datetime.now() - timedelta(days=365)
    q = (model.Test.query
         .filter(model.Test.testityyp==const.TESTITYYP_AVALIK)
         .filter(model.Test.created<dt)
         .filter(~ model.Test.sooritajad.any(
             model.sa.or_(
                 model.Sooritaja.staatus>const.S_STAATUS_ALUSTAMATA,
                 model.Sooritaja.modified>dt)))
         .order_by(model.Test.id)
         )
    cnt = 0
    for test in q.all():
        cnt += 1
        _delete_test(test)

    log.info('Kustutatud %d testi' % (cnt))
    
def _delete_test(test):
    autor = model.Kasutaja.get_name_by_creator(test.creator)
    log.info('Kustutan testi %d (%s), loonud %s %s' % (test.id, test.nimi, test.created, autor))

    for osa in test.testiosad:
        q = (model.Ylesandestatistika.query
             .join(model.Ylesandestatistika.valitudylesanne)
             .join(model.Valitudylesanne.testiylesanne)
             .filter(model.Testiylesanne.testiosa_id==osa.id))
        for yst in q.all():
            yst.delete()
        q = model.Testikoht.query.filter_by(testiosa_id=osa.id)
        for r in q.all():
            r.delete()
        q = model.Kysimusestatistika.query.filter_by(testiosa_id=osa.id)
        for r in q.all():
            r.delete()            

    q = model.Tktest.query.filter_by(test_id=test.id)
    for r in q.all():
        r.delete()        
    q = model.Arvutusprotsess.query.filter_by(test_id=test.id)
    for r in q.all():
        r.delete()        
        
    for j in test.sooritajad:
        j.delete()
    test.delete()

def _error_mail(txt, msg=''):
    "Saadame vea kohta adminile kirja"
    log.error('%s\n%s' % (msg, txt))
    if registry.settings.get('smtp.error_to'):
        subject = 'Veateade (remove_test): %s' % (msg.split('\n')[0].split(',')[0])
        body = html.escape(txt)
        Mailer(handler).error(subject, body)

def _error(exc, msg=''):
    model.Session.rollback()

    txt = 'Skript remove_test.py katkestab töö\n\n' + msg
    if exc:
        txt += '\n' + traceback.format_exc()

    _error_mail(txt, msg)

    sys.exit(1)   

if __name__ == '__main__':
    try:
        remove()
    except Exception as e:
        _error(e, str(e))
    else:
        model.Session.commit()

