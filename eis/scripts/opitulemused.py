# Õpitulemuste klassifikaatori laadimine oppekava.edu.ee Semantic Media Wiki serverist
# ES-2227

import requests
import urllib.parse
from datetime import datetime
from eis.scripts.scriptuser import *
import sqlalchemy as sa

def run():
    # Tõmmatakse alla kõik õpitulemused koos seotud ainetega
    # ning salvestatakse EISi klassifikaatoritena OPITULEMUS ja OPIAINE.

    # Andmete saamise näidis-URLid:
    # https://oppekava.edu.ee/w/api.php?action=ask&query=[[Modification%20date::%2B]]|%3FModification%20date|sort%3DModification%20date|order%3Ddesc&format=jsonfm
    # https://oppekava.edu.ee/w/api.php?action=ask&query=[[Modification%20date::%2B]][[Category:Haridus:Opivaljund]]|%3FModification%20date|sort%3DModification%20date|order%3Ddesc&format=jsonfm

    LIMIT = 1000
    offset = 0
    cnt = 0
    now = datetime.now()

    proxies = {}
    http_proxy = registry.settings.get('http_proxy')
    if http_proxy:
        proxies['https'] = http_proxy
    
    while offset is not None:
        query = "[[Modification date::+]][[Category:Haridus:Opivaljund]]" +\
                "|?Modification date" +\
                "|?Haridus:seotudOppeaine" +\
                "|sort=Modification date" +\
                "|order=desc" +\
                "|limit=%d" % LIMIT +\
                "|offset=%d" % offset
        qquery = urllib.parse.quote(query, safe='|')
        url = f"https://oppekava.edu.ee/w/api.php?action=ask&query={qquery}&format=json"

        headers = {'User-Agent': 'EIS'}
        try:
            r = requests.get(url, headers=headers, proxies=proxies)
        except Exception as ex:
            _error(ex, url)
        try:
            data = r.json()
        except Exception as ex:
            txt = r.text
            _error(ex, url + '\n' + text)
            
        offset = data.get('query-continue-offset')
        dataquery = data['query']
        results = dataquery['results']

        # klassifikaatori koodiks paneme arvu
        sql = "SELECT MAX(CAST(kood AS INTEGER)) FROM klrida WHERE " +\
              "klassifikaator_kood='OPITULEMUS' AND kood SIMILAR TO '\d+'"
        max_k = model.Session.execute(sa.text(sql)).scalar() or 0

        for key, attrs in results.items():
            cnt += 1
            fulltext = attrs['fulltext']
            fullurl = attrs['fullurl']
            #print('%d. %s' % (cnt, fulltext))

            opi = _give_opitulemus(fullurl, fulltext)
            if not opi.kood:
                max_k += 1
                opi.kood = str(max_k)
            opi.kehtib = True
            opi.modified = datetime.now()
            
            printouts = attrs['printouts']
            seotud = printouts['Haridus:seotudOppeaine']
            ained_id = []
            for seotu in seotud:
                a_fulltext = seotu['fulltext']
                a_fullurl = seotu['fullurl']
                #print('   ' + a_fulltext)
                aine = _give_aine(a_fullurl, a_fulltext)
                ained_id.append(aine.id)

            # salvestame seosed õppeainetega
            for r in list(opi.alam_klseosed):
                aine_id = r.ylem_klrida_id
                if aine_id in ained_id:
                    ained_id.remove(aine_id)
                else:
                    r.delete()
            for aine_id in ained_id:
                kls = model.Klseos(ylem_klrida_id=aine_id)
                opi.alam_klseosed.append(kls)

    total = cnt
    
    # märgistame kehtetuks muutunud õpitulemused
    cnt = 0
    q = (model.Session.query(model.Klrida)
         .filter_by(klassifikaator_kood='OPITULEMUS')
         .filter_by(kehtib=True)
         .filter(model.Klrida.modified<now)
         )
    for r in q.all():
        r.kehtib = False
        r.kuni = datetime.now()
        cnt += 1
    model.Session.commit()
    log.info(f'Saadud {total} kirjet, kehtetuks muudetud {cnt} kirjet')

def _give_opitulemus(fullurl, fulltext):
    q = (model.Session.query(model.Klrida)
         .filter_by(idurl=fullurl)
         .filter_by(klassifikaator_kood='OPITULEMUS')
         )
    r = q.first()

    name = fulltext
    if not r:
        r = model.Klrida(klassifikaator_kood='OPITULEMUS',
                         idurl=fullurl,
                         nimi=name,
                         alates=datetime.now())
    else:
        r.nimi = name
    return r

def _give_aine(fullurl, fulltext):
    q = (model.Session.query(model.Klrida)
         .filter_by(idurl=fullurl)
         .filter_by(klassifikaator_kood='OPIAINE')
         )
    r = q.first()
    if not r:
        r = model.Klrida(klassifikaator_kood='OPIAINE',
                         idurl=fullurl,
                         nimi=fulltext,
                         alates=datetime.now())
        model.Session.flush()
    else:
        r.nimi = fulltext
    return r

def _error(exc, msg=''):
    script_error('Veateade (opitulemused)', exc, msg)
    sys.exit(1)   
       
if __name__ == '__main__':
    fn_lock = '/srv/eis/log/opitulemused.lock'
    with FileLock(fn_lock) as lock:
        if not lock:
            log.info('Protsess juba käib (fail %s on lukus)' % fn_lock)
            sys.exit(0)

        try:
            run()
        except Exception as e:
            _error(e, str(e))
