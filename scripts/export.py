"Ülesannete eksportimine"

import logging.config
from pyramid.paster import get_app
import sys
from datetime import datetime
import pickle

datadir = 'data2'

def do_export(item, format):
    if format == 'qti':
        for lang in item.keeled:
            data = qti_export.export_zip(item, lang=lang)
            if lang == item.lang:
                lang = None
            _write_file(item, data, 'zip', lang)
    else:
        data = raw_export.export(item, True)
        _write_file(item, data, 'raw')

def _write_file(item, data, ext, lang=None):
    if isinstance(item, model.Test):
        fn = '%s/test-%d.%s' % (datadir, item.id, ext)
    elif lang:
        fn = '%s/ylesanne-%03d-%s.%s' % (datadir, item.id, lang, ext)        
    else:
        fn = '%s/ylesanne-%03d.%s' % (datadir, item.id, ext)        
    f = open(fn, 'wb')
    f.write(data)
    f.close()
    print('Kirjutatud faili %s' % fn)

def usage():
    print('Kasuta kujul:')
    print(' python export.py [-f /usr/local/eis/etc/config.ini] (qti|raw|test) [-test_id true] identifikaatorid')
    sys.exit(1)

def _parse_id(identifikaatorid):
    li = []
    for buf in identifikaatorid.split(','):
        if not buf:
            continue
        if buf.find('-') > 0:
            buf1, buf2 = buf.split('-')
            id1 = int(buf1)
            id2 = int(buf2)
            for id in range(id1, id2+1):
                li.append(id)
        else:
            li.append(int(buf))
    return li

def _get_items_in_test(identifikaatorid):
    # leitakse testi ylesannete id-d
    q = (model.Session.query(model.Valitudylesanne.ylesanne_id).distinct()
         .filter(model.Valitudylesanne.ylesanne_id!=None)
         .join(model.Valitudylesanne.testiylesanne)
         .join(model.Testiylesanne.testiosa)
         .filter(model.Testiosa.test_id.in_(identifikaatorid))
         .order_by(model.Valitudylesanne.ylesanne_id)
         )
    return [y_id for y_id, in q.all()]

if __name__ == '__main__':
    from eis.scripts.scriptuser import *
    import eis.lib.qti_export as qti_export
    import eis.lib.raw_export as raw_export    

    if len(noname_args) < 2:
        usage()

    format = noname_args[0]
    if format not in ('qti','raw','test','tmp'):
        usage()

    if format == 'test':
        what = 'test'
        format = 'raw'
    else:
        what = 'item'
        
    identifikaatorid = noname_args[1]
    li = _parse_id(identifikaatorid)
    if format == 'tmp':
        testid_id = [7693, 7694, 7695, 6109, 6110, 6111]
        q = (model.Session.query(model.Valitudylesanne.ylesanne_id).distinct()
             .filter(model.Valitudylesanne.test_id.in_(testid_id))
             .order_by(model.Valitudylesanne.ylesanne_id))
        li = [y_id for y_id, in q.all()]
    elif what == 'test':
        # eksporditakse test koos ylesannetega
        print('Eksporditavad testid: %s' % identifikaatorid)        
    else:
        # eksporditakse ylesanded
        if named_args.get('test_id'):
            # eksporditakse ylesandeid, mis on antud testis
            li = _get_items_in_test(li)
            identifikaatorid = ','.join([str(y_id) for y_id in li])
        print('Eksporditavad ülesanded: %s' % identifikaatorid)

    for id in li:
        if what == 'test':
            item = model.Test.get(id)
            if not item:
                print('Ei leitud testi %s' % id)
                continue
        else:
            item = model.Ylesanne.get(id)
            if not item:
                print('Ei leitud ylesannet %s' % id)
                continue
        print('Eksport id=%s (%s)...' % (item.id, item.nimi))
        do_export(item, format)
