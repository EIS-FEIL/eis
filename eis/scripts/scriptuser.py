# -*- coding: utf-8 -*- 
# Skriptide töökeskkonna loomine

# võimalikud argumendid:
# -admin - kasutaja isikukood (vaikimisi ADMIN)
# -f - konfifail (vaikimisi /srv/eis/etc/config.ini)
# -level - logitase: 10 - debug, 20 - info, 30 - warn, 40 - error

import sys
import os
import traceback
import cgi
import webob
from pyramid.i18n import make_localizer
from pyramid.paster import bootstrap
from eis.scripts.filelock import FileLock

ini_file = '/srv/eis/etc/config.ini'

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

class TmpEvent(object):
    def __init__(self, request):
        self.request = request

def _get_logger():
    level = int(named_args.get('level') or logging.INFO)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    formatter = logging.Formatter('%(asctime)s:%(levelname)s: %(message)s')
    console_handler.setFormatter(formatter)

    log = logging.getLogger('eis')
    log.setLevel(level)
    log.addHandler(console_handler)

    return log

named_args, noname_args = _find_args()

if 'f' in named_args:
    ini_file = named_args.get('f')

import logging
import logging.config

info = bootstrap(ini_file)
registry = info['registry']
request = info['request']
is_live = registry.settings.get('live') != 'false' and registry.settings.get('test') != 'true'
                
import eis
from eis.lib.base import *

BaseController._authorize = False
BaseController._get_is_readonly = False
event = TmpEvent(request)
eis.add_localizer(event)
handler = BaseController(request)
admin_ik = named_args.get('admin')
handler.c.controller = sys.argv[0].split('/')[-1]

user = User(handler)
user.auth_type = const.AUTH_TYPE_ID

if admin_ik:
    kasutaja = model.Kasutaja.get_by_ik(admin_ik)
    if not kasutaja:
        print('Kasutajat %s ei leitud' % admin_ik)
        sys.exit(1)
    user.id = kasutaja.id
    user.perenimi = kasutaja.perenimi
    user.eesnimi = kasutaja.eesnimi
else:
    admin_ik = 'ADMIN'
user.isikukood = admin_ik    
handler.user = handler.c.user = user
log = _get_logger()
       
def script_error(sub_prefix, e, msg='', prev_msg=None):
    "Vigade logimine"
    model.Session.rollback()
    if e:
        txt = str(e)
    else:
        txt = msg
    log.error(txt)
    if msg != prev_msg:
        handler._error(e, sub_prefix + ' ' + msg, rollback=False)
    return msg
