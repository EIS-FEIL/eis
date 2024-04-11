import formencode
import re
from eis.forms import validators
from eis.lib.pyxadapterlib.xutils import *
from eis.lib.pyxadapterlib.xroadclient import (
    XroadClient,
    SoapFault,
    E,
    make_log_day_path,
)
import sys
import eiscore.const as const

class XroadClientEIS(XroadClient):
    def __init__(self, handler=None, security_server=None, userId=None, settings=None):
        XroadClient.__init__(self, handler, security_server, userId, settings)
        if not self.userId and handler:
            # märgime teenuse kasutajaks jooksva kasutaja
            ik = handler.c.user.isikukood
            if ik and ik != 'ADMIN' and ik != '0' and not re.match(r'[A-Z]{2}', ik):
                # Eesti isikukoodile lisada prefiks, teistel on olemas
                self.userId = 'EE%s' % ik
        if self.is_pseudo(self.userId):
            self.userId = None

    def is_pseudo(self, ik):
        # ES-1479
        if ik and ik.startswith('EE'):
            ik = ik[2:]
        return ik in ('39001019998','39001019987','39001019976','39001019965')

    def on_fault(self, e, service_name):
        buf = self.fault_text(e, service_name)
        log.error(buf)
        if self.handler:
            msg = f'X-tee liides ei toimi ({self.producer}, {service_name})'
            self.handler._error(e, msg, False)
        err = 'Välise süsteemi liides ei toimi (%s)' % (self.producer)
        raise SoapFault(None, err)

    def _trace_msg(self, method, ext, data, duration=None):
        "Log input and output messages"
        param = '%s %s' % (method, ext)
        if self.handler:
            c = self.handler.c
            request = self.handler.request
            self.handler.log_add(const.LOG_XTEE, data, param, kestus=duration)

    def call(self, service_name, params, list_path, service_version=None, attachments=[], timeout=None):
        try:
            if self.handler:
                t = self.handler.prf()
            return XroadClient.call(self, service_name, params, list_path, service_version, attachments, timeout)
        finally:
            if self.handler:
                self.handler.prf('xteecall', t)
                
def fstr(f, digits=3):
    # 3 kohta peale koma, aga ilma nullideta peale koma
    if isinstance(f, (float, int)):
        return re.sub(r'\.?0+$', '', (('%.' + str(digits) + 'f') % f))
    
def get_ee_user_id(header):
    userid = header.userId
    if userid and userid[:2] == 'EE':
        return userid[2:]    

def validate_isikukoodid(isikukoodid, check_digit=True):
    """Sisendis antud isikukoodide valideerimine.
    Tagastatakse veateade, kui on vigaseid isikukoode, 
    või None, kui ei ole.
    """
    # Eesti isikukoodid
    li_ee = []
    # mitte mingi riigi isikukoodid
    bad = []
    message = None
    for isikukood in isikukoodid:
        usp = validators.IsikukoodP(isikukood)
        if not usp.isikukood:
            bad.append(isikukood)
        elif usp.isikukood_ee:
            li_ee.append(isikukood)
    return li_ee, bad

def test_me(serve, name, request, named_args, version='v1', attachments=[]):
    class Handler(object):
        def __init__(self):
            pass

    admin = named_args.get('admin')
    header = Xresult()
    if admin:
        header.addattrs(userId='EE' + admin)
    header.addattrs(service=Xresult(serviceCode=name,
                                    serviceVersion=version),
                    client=Xresult(xRoadInstance='T',
                                   memberClass='T',
                                   memberCode='TESTCLIENT',
                                   subsystemCode='testme'),
                    consumer='testme',
                    id='test'
                    )
    res, att = serve(request, header, attachments=attachments, context=Handler())
    print(outer_xml(res))
    return res, att

def get_date_err(request, key):
    try:
        return get_date(request, key), None
    except:
        return None, 'Vigane kuupäev (%s)' % key

def get_datetime_err(request, key):
    try:
        return get_datetime(request, key), None
    except:
        return None, 'Vigane aeg (%s)' % key

def get_int_err(request, key):
    try:
        return get_int(request, key)
    except:
        return None, 'Vigane arv (%s)' % key


# Xresult väärtuste teisendamine
    
def none_float(value):
    if value is not None and value != '':
        return float(value)

def none_int(value):
    if value is not None and value != '':
        return int(value)

def none_date(value):
    if value is not None and value != '':
        return date_from_iso(value)

def none_boolean(value):
    if value is not None and value != '':
        if value in ('true', '1'):
            return True
        elif value in ('false', '0'):
            return False
        
