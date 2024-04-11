# -*- coding: utf-8 -*- 
# $Id: import.py 1243 2017-03-06 19:33:17Z ahti $
"Ülesannete importimine"

import sys
import os
import tempfile
import shutil
import pickle
from eis.lib.block import BlockController

def do_import(fn, aine_kood=None, staatus=None, imgdir=None):
    ext = fn.rsplit('.', 1)[-1].lower()
    if ext == 'raw':
        imp = RawImportPackage(fn, None)
    elif ext == 'zip':
        imp = QtiImportPackage(fn, None)
    elif ext == 'csv':
        aine = named_args.get('aine')
        keel = named_args.get('keel')
        imgdir = named_args.get('imgdir') or imgdir
        utf8 = named_args.get('utf8')
        encoding = utf8 and 'utf-8' or None
        if not aine or not keel:
            usage()
        imp = CsvImportPackage(fn, None, aine, keel, imgdir=imgdir, encoding=encoding)
    else:
        print('Tundmatu failitüüp %s' % ext)
        return False

    if imp:
        imp.handler = handler
        if imp.is_error:
            print('Import ei õnnestunud')
            rc = False
        else:
            imp.after_import()
            rc = True
        for tu in imp.messages:
            is_ok, txt = tu
            if is_ok:
                print(txt)
            else:
                print('VIGA ' + txt)

        if rc:
            for item in imp.items:
                if isinstance(item, model.Test):
                    print(' Test %s %s' % (item.id, item.nimi))
                elif isinstance(item, model.Ylesanne):
                    print('  Ülesanne %s %s' % (item.id, item.nimi))
                    if aine_kood and not len(item.ylesandeained):
                        yaine = model.Ylesandeaine(aine_kood=aine_kood, seq=0)
                        item.ylesandeained.append(yaine)                     
                    if staatus:
                        item.staatus = staatus
        return rc
    
def do_import_dir(datadir, aine_kood=None, staatus=None):
    li = os.listdir(datadir)
    li.sort()
    for fn in li:
        if fn.endswith('.zip') or fn.endswith('.raw') or fn.endswith('.csv'):
            print('Import %s...' % fn)
            fn_full = os.path.join(datadir, fn)
            rc = do_import(fn_full, aine_kood, staatus, datadir)
            if not rc:
                return False
    return True

def usage():
    print("""Kasuta kujul:
    python import.py [-f /usr/local/eis/etc/config.ini] {DIR|FILE.zip|FILE.raw}
    python import.py [-f /usr/local/eis/etc/config.ini] {DIR|FILE.csv} -aine AINEKOOD -keel KEELEKOOD [-imgdir DIR] [-utf8]
""")
    sys.exit(1)


if __name__ == '__main__':
    from eis.scripts.scriptuser import *
    from eis.lib.base import HandledError
    from eis.lib.qti_import import QtiImportPackage
    from eis.lib.raw_import import RawImportPackage
    from eis.lib.csv_import import CsvImportPackage

    if len(noname_args) != 1:
        if not (len(noname_args) == 2 and noname_args[0] == 'fix'):
            usage()
   
    fn = noname_args[0]
        
    rc = False
    try:
        staatus = model.const.Y_STAATUS_EELTEST
        if os.path.isdir(fn) and fn == 'data':
            rc = do_import_dir(fn, 'b', staatus)
        elif os.path.isdir(fn):
            rc = do_import_dir(fn, 'K', staatus)
        else:
            if not fn.endswith('.zip') and not fn.endswith('.raw') and not fn.endswith('.csv'):
                usage()
            rc = do_import(fn)
    except ValidationError as e:
        model.Session.rollback()
        messages = handler.request.session.pop_flash('error')
        for message in messages:
            print(message)
    except:
        model.Session.rollback()
        raise

    if rc:
        model.Session.commit()
        print("IMPORT OLI EDUKAS")
