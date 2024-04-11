"""
Vanade failide kustutamine puhvrist

python -m eis.scripts.remove_filecache
"""
import sys
import os
import glob
import time
import re
import psutil
import logging
from datetime import datetime, timedelta
from eis.scripts.filelock import FileLock

log = logging.getLogger(__name__)

CACHE_PATH = '/srv/eis/var/filecache'
FN_LOCK = '/srv/eis/log/remove_filecache.lock'

def usage():
    print('Kasuta kujul:')
    print('   python -m eis.scripts.remove_filecache [-d 100]')
    print()
    sys.exit(0)

def _find_args():
    named_args = {}
    noname_args = []

    key = None
    n = 1
    while n < len(sys.argv):
        arg = sys.argv[n]
        n += 1
        if arg.startswith('-'):
            key = arg[1:]
            named_args[key] = True
        else:
            value = arg
            if key:
                named_args[key] = value
                key = None
            else:
                noname_args.append(value)
    return named_args, noname_args  

def remove_files(days):
    "Käib kõik failid läbi ja kustutab need, mis on vanemad kui antud arv päevi"
    min_tm = time.mktime((datetime.now() - timedelta(days=days)).timetuple())
    for (dirpath, dirnames, filenames) in os.walk(CACHE_PATH):
        log.debug('dir:%s...' % dirpath)
        for fn in filenames:
            path = os.path.join(dirpath, fn)

            # kui oleme faili juba kustutanud
            if not os.path.isfile(path):
                continue

            # kustutame failid, mida pole etteantud arv päevi kasutatud
            if min_tm and min_tm > os.path.getatime(path):
                log.debug(' rm old %s' % path)
                os.remove(path)
                continue
            
            # kustutame sama faili vanemad versioonid
            m = re.match(r'.*\.([0-9]+)\.[^.]*$', path)
            if m:
                file_ver = int(m.groups()[0])
                glob_pattern = re.sub('\.[^.]*(.[^.]*)$', '.*\\1', path)
                for path2 in glob.glob(glob_pattern):
                    if path2 != path:
                        m2 = re.match(r'.*\.([0-9]+)\.[^.]*$', path2)
                        if m2:
                            file2_ver = int(m2.groups()[0])
                            if file2_ver < file_ver:
                                log.debug(' rm %s' % path2)
                                os.remove(path2)
                            else:
                                log.debug(' rm %s' % path)
                                os.remove(path)
                                path = path2
                                file_ver = file2_ver

def remove_filecache(days, min_freegb):
    if days is None:
        days = 14
    if min_freegb is None:
        min_freegb = 3
    min_freekb = min_freegb * 1000000000
    for n in range(days, -1, -1):
        # päevade arv väheneb seni, kuni on piisavalt palju vaba ruumi
        log.info(f'remove_filecache {days} days')
        remove_files(days)
        usage = psutil.disk_usage(CACHE_PATH)
        if usage.free > min_freekb:
            # piisavalt vaba ruumi
            break

def remove_filecache_lock(days, min_freegb):
    with FileLock(FN_LOCK) as lock:
        if not lock:
            log.info(_('Protsess juba käib (fail {fn} on lukus)').format(fn=fn_lock))
            return
        remove_filecache(days, min_freegb)

def check_filecache():
    "Kui on öö ja faile pole päeva jooksul kontrollitud, siis kontrollitakse"
    dt = datetime.now()
    if dt.hour > 6:
        return
    now = dt.timestamp()
    try:
        mtime = os.path.getmtime(FN_LOCK)
    except OSError:
        mtime = 0
    if now - mtime > 96400:
        remove_filecache_lock(None, None)
        
if __name__ == '__main__':
    named_args, noname_args = _find_args()
    # kustutame failid, mida pole 14 päeva jooksul loetud
    days = named_args.get('d')
    if days:
        days = int(days)

    # või kui vaba ruumi on alla 3 GB, siis veidi nooremad failid ka
    freegb = named_args.get('f')
    if freegb:
        freegb = int(freegb)

    remove_filecache_lock(days, freegb)
