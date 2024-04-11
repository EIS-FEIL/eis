"""X-tee adapter
"""
import traceback
import logging
import html
from datetime import datetime
from webob import Response
import os
import eis
import eis.model as model
import eiscore.const as const
import eis.model_log as model_log
import eis.lib.xteeserver as xteeserver
from eis.lib.base import BaseController, rollback_callback, NewItem, Mailer, User
import eis.lib.utils as utils
from eis.lib.helpers import RequestHelpers
log = logging.getLogger(__name__)

class AdapterHandler(BaseController):
    """
    X-tee adapter
    """

    _authorize = False
    is_error_fullpage = False
    
    def __init__(self, request):
        # jätame meelde requesti ja kasutame seda edaspidi igal pool
        self.request = request
        request._log_started = datetime.now()
        # logikirjete jada
        request.logrows = []
        # et vajadusel saaks requestist kontrollerini jõuda, siis ka teistpidi
        request.handler = self
        # vormile renderdatavate andmete hoidmise objekt, vaja base.py funktsioonides
        c = self.c = NewItem()
        # vormil kasutatavad helper-funktsioonid
        self.h = RequestHelpers(request)
        # valikud
        c.opt = model.Opt(self)
        c.action = self._get_action(request)
            
        # lisame callbacki, et pärast alati andmebaasiseanss vabastataks
        request.add_finished_callback(rollback_callback)

    def _init_user(self, header_dict):
        "user objekti loomine, et andmemudeli tekstid saaks tõlgitud"
        user = User.from_none(self)
        try:
            userid = header_dict.userId
            if userid.startswith('EE'):
                user.isikukood = userid[2:]
        except:
            pass
        model.usersession.set_user(user)

    def serve(self):
        """Teenuste pakkumine
        """
        request = self.request
        reuse = None
        if self.is_devel:
            # arendussetrer, pole Apache all
            if request.method == 'GET':
                # taaskasutame viimast salvestatud sisendit
                reuse = 2
            else:
                # salvestame sisendi taaskasutamiseks
                reuse = 1
        return xteeserver.srv.dispatch(request, self._error, self, reuse)

    def check(self):
        "Monitooringupäring"
        # andmebaaside kontroll
        model.Session.query(1).scalar()
        model.SessionR.query(1).scalar()
        model_log.DBSession.query(1).scalar()
        # vastus
        res = {'server_addr': os.getenv('HOSTNAME'),
               'ver': eis.__version__,
               }
        return Response(json_body=res)
        
    def test(self):
        from eis.lib.xtee.testeis import TestEis
        reg = TestEis(handler=self,
                      userId='EE30101010007')
        reg.security_server = 'localhost:6543'
        reg.security_server_uri = '/'
        res = reg.e_tunnistus_am(12)
        attachments = reg.response_attachments
        return Response(reg.response, content_type='text/plain')

    def _error_mail(self, txt, param='', info='', logi_id=None, msg=None):
        # saadame vea kohta adminile kirja
        if self.request.registry.settings.get('smtp.error_to'):
            environ = self.request.environ
            server_addr = environ.get('HOSTNAME') or environ.get('SERVER_ADDR')
            try:
                mail_body = '<h2>Veateade X-tee adapteris</h2>\n'
                mail_body += '<b>Aeg:</b> %s<br/>\n' % (datetime.now())
                if logi_id:
                    mail_body += '<b>Logi id: </b>%s<br/>\n' % logi_id
                mail_body += '<b>Server:</b> %s<br/>' % (server_addr)
                if msg:
                    mail_body += msg + '<br/>\n'
                url = self.request.url
                mail_body += '<b>URL:</b> %s %s<br/>' % (self.request.method, url)
                mail_body += '<b>Viga:</b><br/>\n'
                mail_body += html.escape(txt) + '\n'
                if info:
                    mail_body += info

                subject = 'Veateade X-tee adapteris'
                if logi_id:
                    subject += ' %s' % (logi_id)
                if msg:
                    subject += ': ' + msg[:50].replace('\n',' ')
                Mailer(self).error(subject, mail_body)
            except Exception as ex:
                log.error('Ei saa saata e-posti. %s' % ex)

    def _error_log(self, txt, param='', tyyp=const.LOG_ERROR):
        # logime vea andmebaasis logitabelis
        logi_id = self.log_add(tyyp,
                               txt,
                               None,
                               kontroller='adapter',
                               tegevus='adapter')
        return logi_id       

    def response_on_error(self, error):
        "Vea korral antav vastus"
        if self.c.action == 'check':
            # jsoni vastus
            res = {'error': error}
            return Response(json_body=res, status=500)
        else:
            return super().response_on_error(error)
