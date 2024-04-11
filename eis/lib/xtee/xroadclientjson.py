"X-tee REST JSON klient"
import requests
import logging
log = logging.getLogger(__name__)

class XroadFault(RuntimeError):
    def __init__(self, faultcode, faultstring, detail=None):
        self.faultcode = faultcode
        self.faultstring = faultstring
        self.detail = detail       

class XroadClientJSON:
    security_server = None # security server IP (may be with :port)
    userid = None # user ID value in SOAP header
    handler = None # view handler
    producer = None
    baseurl = None
    settings = {} # configuration settings
    _callerid = None
    _providerid = None
    
    def __init__(self, handler=None, userid=None, settings=None):
        if handler:
            self.handler = handler
            if not settings:
                settings = handler.request.registry.settings

        self.settings = settings
        db = self.producer

        self._callerid = self._get_setting('client', db)
        self._providerid = self._get_setting('server', db)
            
        self.security_server = self._get_setting('security_server', db)


        self.key = self._get_setting('key', db)
        self.cert = self._get_setting('cert', db)
        self.http_proxy = self._get_setting('http_proxy', db) or None
        self.log_dir = self._get_setting('log_dir', db)

        json_protocol = 'r1'
        self.baseurl = f'http://{self.security_server}/{json_protocol}/{self._providerid}'
        self.userid = userid

        if not self.userid and handler:
            # märgime teenuse kasutajaks jooksva kasutaja
            ik = handler.c.user.isikukood
            if ik and ik != 'ADMIN' and ik != '0':
                self.userid = 'EE%s' % ik

    @property
    def active(self):
        return self._providerid is not None
        
    def _get_db_setting(self, key, db):
        return self.settings.get('xroad.%s.%s' % (key, db))

    def _get_setting(self, key, db):
        value = self._get_db_setting(key, db)
        if not value:
            value = self.settings.get('xroad.%s' % key)
        return value

    def on_fault(self, e, service_name, url, params=None):
        buf = self.fault_text(e, service_name, url, params)
        log.error(buf)
        if self.handler:
            msg = f'X-tee liides ei toimi ({self.producer}, {service_name}) {url}'
            self.handler._error(e, msg, False)
        err = 'X-tee liides ei toimi (%s: %s)' % (self.producer, str(e))
        raise XroadFault(None, err)

    def fault_text(self, e, service_name, url, params=None):
        buf = f'X-road error: {e} ({self.producer}, {service_name})\n' +\
              str(e) + f'\n URL: {url}'
        if params:
            buf += '\n' + str(params)
        return buf
    
